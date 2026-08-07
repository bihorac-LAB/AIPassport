/**
 * Deterministic simulation maths.
 *
 * Everything here is a pure function with a seeded RNG, so a slider drag recomputes locally with no
 * network round-trip and every learner sees the same numbers. This is what replaces the legacy app's
 * server-side scikit-learn call on every widget change.
 */

/** Mulberry32 — small, fast, reproducible. */
export function rng(seed: number): () => number {
  let state = seed >>> 0;
  return () => {
    state = (state + 0x6d2b79f5) >>> 0;
    let t = state;
    t = Math.imul(t ^ (t >>> 15), t | 1);
    t ^= t + Math.imul(t ^ (t >>> 7), t | 61);
    return ((t ^ (t >>> 14)) >>> 0) / 4294967296;
  };
}

/** Box–Muller normal sample from a uniform generator. */
export function normal(next: () => number, mean = 0, sd = 1): number {
  const u1 = Math.max(next(), 1e-12);
  const u2 = next();
  return mean + sd * Math.sqrt(-2 * Math.log(u1)) * Math.cos(2 * Math.PI * u2);
}

export function gamma(next: () => number, shape: number, scale: number): number {
  // Sum-of-exponentials approximation, adequate for integer-ish shapes used here.
  let total = 0;
  const k = Math.max(1, Math.round(shape));
  for (let i = 0; i < k; i += 1) total += -Math.log(Math.max(next(), 1e-12));
  return total * scale;
}

export const clamp = (value: number, lo: number, hi: number): number =>
  Math.min(hi, Math.max(lo, value));

export const sigmoid = (z: number): number => 1 / (1 + Math.exp(-z));

export const mean = (values: number[]): number =>
  values.length === 0 ? 0 : values.reduce((a, b) => a + b, 0) / values.length;

export function sd(values: number[]): number {
  if (values.length < 2) return 0;
  const m = mean(values);
  return Math.sqrt(values.reduce((a, v) => a + (v - m) ** 2, 0) / (values.length - 1));
}

export function quantile(values: number[], q: number): number {
  if (values.length === 0) return 0;
  const sorted = [...values].sort((a, b) => a - b);
  const pos = (sorted.length - 1) * q;
  const lo = Math.floor(pos);
  const hi = Math.ceil(pos);
  const loVal = sorted[lo] ?? 0;
  const hiVal = sorted[hi] ?? loVal;
  return loVal + (hiVal - loVal) * (pos - lo);
}

export const median = (values: number[]): number => quantile(values, 0.5);

export function iqrBounds(values: number[], multiplier = 1.5) {
  const q1 = quantile(values, 0.25);
  const q3 = quantile(values, 0.75);
  const iqr = q3 - q1;
  return { q1, q3, iqr, lower: q1 - multiplier * iqr, upper: q3 + multiplier * iqr };
}

export function zScores(values: number[]): number[] {
  const m = mean(values);
  const s = sd(values) || 1;
  return values.map((v) => (v - m) / s);
}

// ── Classification metrics ───────────────────────────────────────────────────

export type Confusion = { tn: number; fp: number; fn: number; tp: number };

export function confusion(labels: number[], scores: number[], threshold: number): Confusion {
  let tn = 0;
  let fp = 0;
  let fn = 0;
  let tp = 0;
  for (let i = 0; i < labels.length; i += 1) {
    const positive = (scores[i] ?? 0) >= threshold;
    const actual = labels[i] === 1;
    if (actual && positive) tp += 1;
    else if (actual) fn += 1;
    else if (positive) fp += 1;
    else tn += 1;
  }
  return { tn, fp, fn, tp };
}

export type Metrics = Confusion & {
  accuracy: number;
  sensitivity: number;
  specificity: number;
  ppv: number;
  npv: number;
  f1: number;
  prevalence: number;
};

export function metrics(c: Confusion): Metrics {
  const total = c.tn + c.fp + c.fn + c.tp || 1;
  const sensitivity = c.tp + c.fn === 0 ? 0 : c.tp / (c.tp + c.fn);
  const specificity = c.tn + c.fp === 0 ? 0 : c.tn / (c.tn + c.fp);
  const ppv = c.tp + c.fp === 0 ? 0 : c.tp / (c.tp + c.fp);
  const npv = c.tn + c.fn === 0 ? 0 : c.tn / (c.tn + c.fn);
  return {
    ...c,
    accuracy: (c.tp + c.tn) / total,
    sensitivity,
    specificity,
    ppv,
    npv,
    f1: ppv + sensitivity === 0 ? 0 : (2 * ppv * sensitivity) / (ppv + sensitivity),
    prevalence: (c.tp + c.fn) / total,
  };
}

/** Rank-based AUC (Mann–Whitney U), ties counted as half. */
export function auc(labels: number[], scores: number[]): number {
  const pos: number[] = [];
  const neg: number[] = [];
  labels.forEach((label, i) => {
    (label === 1 ? pos : neg).push(scores[i] ?? 0);
  });
  if (pos.length === 0 || neg.length === 0) return Number.NaN;
  let wins = 0;
  for (const p of pos) {
    for (const n of neg) {
      if (p > n) wins += 1;
      else if (p === n) wins += 0.5;
    }
  }
  return wins / (pos.length * neg.length);
}

export function rocCurve(labels: number[], scores: number[], steps = 60) {
  const points: Array<{ fpr: number; tpr: number; threshold: number }> = [];
  for (let i = 0; i <= steps; i += 1) {
    const threshold = 1 - i / steps;
    const m = metrics(confusion(labels, scores, threshold));
    points.push({ fpr: 1 - m.specificity, tpr: m.sensitivity, threshold });
  }
  return points;
}

export function calibrationBins(
  labels: number[],
  scores: number[],
  bins = 10,
): Array<{ predicted: number; observed: number; count: number }> {
  const buckets = Array.from({ length: bins }, () => ({ sum: 0, hits: 0, count: 0 }));
  scores.forEach((score, i) => {
    const index = clamp(Math.floor(score * bins), 0, bins - 1);
    const bucket = buckets[index];
    if (!bucket) return;
    bucket.sum += score;
    bucket.hits += labels[i] === 1 ? 1 : 0;
    bucket.count += 1;
  });
  return buckets
    .filter((bucket) => bucket.count > 0)
    .map((bucket) => ({
      predicted: bucket.sum / bucket.count,
      observed: bucket.hits / bucket.count,
      count: bucket.count,
    }));
}

/** Cohen's kappa for two binary raters. */
export function cohenKappa(a: number[], b: number[]): number {
  const n = Math.min(a.length, b.length);
  if (n === 0) return Number.NaN;
  let agree = 0;
  let aPos = 0;
  let bPos = 0;
  for (let i = 0; i < n; i += 1) {
    if (a[i] === b[i]) agree += 1;
    if (a[i] === 1) aPos += 1;
    if (b[i] === 1) bPos += 1;
  }
  const po = agree / n;
  const pe = (aPos / n) * (bPos / n) + (1 - aPos / n) * (1 - bPos / n);
  if (pe === 1) return 1;
  return (po - pe) / (1 - pe);
}

export const percent = (value: number, digits = 0): string =>
  Number.isFinite(value) ? `${(value * 100).toFixed(digits)}%` : '—';

export const fixed = (value: number, digits = 2): string =>
  Number.isFinite(value) ? value.toFixed(digits) : '—';
