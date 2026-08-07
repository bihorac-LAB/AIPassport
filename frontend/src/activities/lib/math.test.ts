import { describe, expect, it } from 'vitest';
import {
  auc,
  calibrationBins,
  cohenKappa,
  confusion,
  iqrBounds,
  median,
  metrics,
  rng,
  sd,
} from './math';

describe('simulation maths', () => {
  it('produces the same sequence for the same seed', () => {
    const a = Array.from({ length: 5 }, rng(42));
    const b = Array.from({ length: 5 }, rng(42));
    expect(a).toEqual(b);
    expect(Array.from({ length: 5 }, rng(43))).not.toEqual(a);
  });

  it('computes a confusion matrix at a threshold', () => {
    const labels = [1, 1, 0, 0];
    const scores = [0.9, 0.4, 0.6, 0.1];
    expect(confusion(labels, scores, 0.5)).toEqual({ tp: 1, fn: 1, fp: 1, tn: 1 });
  });

  it('derives clinical metrics from the confusion matrix', () => {
    const m = metrics({ tp: 8, fn: 2, fp: 10, tn: 80 });
    expect(m.sensitivity).toBeCloseTo(0.8);
    expect(m.specificity).toBeCloseTo(80 / 90);
    expect(m.ppv).toBeCloseTo(8 / 18);
    expect(m.prevalence).toBeCloseTo(0.1);
  });

  it('reproduces the low-prevalence PPV result the module teaches', () => {
    // 90% sensitivity, 90% specificity, 1% prevalence, 10,000 patients.
    const m = metrics({ tp: 90, fn: 10, fp: 990, tn: 8910 });
    expect(m.sensitivity).toBeCloseTo(0.9);
    expect(m.specificity).toBeCloseTo(0.9);
    expect(m.ppv).toBeGreaterThan(0.07);
    expect(m.ppv).toBeLessThan(0.09);
  });

  it('gives AUC 1 for perfect separation and 0.5 for none', () => {
    expect(auc([1, 1, 0, 0], [0.9, 0.8, 0.2, 0.1])).toBe(1);
    expect(auc([1, 0, 1, 0], [0.5, 0.5, 0.5, 0.5])).toBeCloseTo(0.5);
  });

  it('leaves the median unmoved by an extreme value but moves the mean', () => {
    const clean = [70, 72, 75, 78, 80];
    const withOutlier = [...clean, 400];
    expect(median(clean)).toBe(75);
    expect(median(withOutlier)).toBeCloseTo(76.5);
    expect(sd(withOutlier)).toBeGreaterThan(sd(clean) * 3);
  });

  it('computes IQR bounds that flag the intended tails', () => {
    const values = [10, 12, 13, 14, 15, 16, 17, 18, 19, 100];
    const bounds = iqrBounds(values, 1.5);
    expect(bounds.upper).toBeLessThan(100);
    expect(values.filter((v) => v > bounds.upper)).toEqual([100]);
  });

  it('reproduces the high-agreement, low-kappa paradox at low prevalence', () => {
    // 100 cases, both readers say "negative" almost always; they agree on 92 but on few positives.
    const a = Array.from({ length: 100 }, (_, i) => (i < 4 ? 1 : 0));
    const b = Array.from({ length: 100 }, (_, i) => (i >= 2 && i < 6 ? 1 : 0));
    const rawAgreement = a.filter((value, i) => value === b[i]).length / a.length;
    expect(rawAgreement).toBeGreaterThan(0.9);
    expect(cohenKappa(a, b)).toBeLessThan(0.6);
  });

  it('bins calibration only where there is data', () => {
    // 0.1 and 0.15 both land in bin 1; 0.85 and 0.9 land in bins 8 and 9 — three occupied bins.
    const bins = calibrationBins([1, 0, 1, 0], [0.9, 0.85, 0.1, 0.15], 10);
    expect(bins.length).toBe(3);
    for (const bin of bins) {
      expect(bin.count).toBeGreaterThan(0);
      expect(bin.predicted).toBeGreaterThanOrEqual(0);
      expect(bin.predicted).toBeLessThanOrEqual(1);
    }
  });
});
