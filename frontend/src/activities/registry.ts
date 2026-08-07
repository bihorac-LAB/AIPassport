/**
 * Activity registry.
 *
 * Every entry is a `lazy()` import so a module page downloads only its own activities. Module 5's
 * imaging code is never in Module 1's chunk.
 */

import { lazy, type ComponentType, type LazyExoticComponent } from 'react';
import type { ActivityProps } from './ActivityShell';

type ActivityComponent = LazyExoticComponent<ComponentType<ActivityProps>>;

const m1 = () => import('./module1');
const m2 = () => import('./module2');
const m3 = () => import('./module3');
const m4 = () => import('./module4');
const m5 = () => import('./module5');
const m6 = () => import('./module6');
const m7 = () => import('./module7');

export const ACTIVITIES: Record<string, ActivityComponent> = {
  // Module 1
  'concept-sorter': lazy(() => m1().then((m) => ({ default: m.ConceptSorter }))),
  'ai-timeline': lazy(() => m1().then((m) => ({ default: m.AiTimeline }))),
  'lifecycle-simulator': lazy(() => m1().then((m) => ({ default: m.LifecycleSimulator }))),
  'split-strategy': lazy(() => m1().then((m) => ({ default: m.SplitStrategy }))),
  'outlier-lab': lazy(() => m1().then((m) => ({ default: m.OutlierLab }))),

  // Module 2
  'fairness-explorer': lazy(() => m2().then((m) => ({ default: m.FairnessExplorer }))),
  'drift-simulator': lazy(() => m2().then((m) => ({ default: m.DriftSimulator }))),
  'calibration-lab': lazy(() => m2().then((m) => ({ default: m.CalibrationLab }))),
  'model-card-builder': lazy(() => m2().then((m) => ({ default: m.ModelCardBuilder }))),

  // Module 3
  'consent-rewriter': lazy(() => m3().then((m) => ({ default: m.ConsentRewriter }))),
  'representation-planner': lazy(() => m3().then((m) => ({ default: m.RepresentationPlanner }))),
  'security-audit': lazy(() => m3().then((m) => ({ default: m.SecurityAudit }))),
  'omop-mapper': lazy(() => m3().then((m) => ({ default: m.OmopMapper }))),
  'label-agreement': lazy(() => m3().then((m) => ({ default: m.LabelAgreement }))),
  'preprocessing-pipeline': lazy(() => m3().then((m) => ({ default: m.PreprocessingPipeline }))),
  'federated-round': lazy(() => m3().then((m) => ({ default: m.FederatedRound }))),

  // Module 4
  'decision-boundary': lazy(() => m4().then((m) => ({ default: m.DecisionBoundary }))),
  'complexity-curve': lazy(() => m4().then((m) => ({ default: m.ComplexityCurve }))),
  'cross-validation': lazy(() => m4().then((m) => ({ default: m.CrossValidation }))),
  'threshold-explorer': lazy(() => m4().then((m) => ({ default: m.ThresholdExplorer }))),
  'explanation-lab': lazy(() => m4().then((m) => ({ default: m.ExplanationLab }))),
  'what-if': lazy(() => m4().then((m) => ({ default: m.WhatIf }))),

  // Module 5
  'pixel-reveal': lazy(() => m5().then((m) => ({ default: m.PixelReveal }))),
  'attenuation-phantom': lazy(() => m5().then((m) => ({ default: m.AttenuationPhantom }))),
  'window-level': lazy(() => m5().then((m) => ({ default: m.WindowLevel }))),
  'convolution-lab': lazy(() => m5().then((m) => ({ default: m.ConvolutionLab }))),
  'noise-denoise': lazy(() => m5().then((m) => ({ default: m.NoiseDenoise }))),
  'histogram-equalization': lazy(() => m5().then((m) => ({ default: m.HistogramEqualization }))),
  'imaging-checklist': lazy(() => m5().then((m) => ({ default: m.ImagingChecklist }))),

  // Module 6
  tokenizer: lazy(() => m6().then((m) => ({ default: m.Tokenizer }))),
  'next-token': lazy(() => m6().then((m) => ({ default: m.NextToken }))),
  'embedding-space': lazy(() => m6().then((m) => ({ default: m.EmbeddingSpace }))),
  'hallucination-hunt': lazy(() => m6().then((m) => ({ default: m.HallucinationHunt }))),

  // Module 7
  'study-designer': lazy(() => m7().then((m) => ({ default: m.StudyDesigner }))),
};

export function getActivity(key: string): ActivityComponent | undefined {
  return ACTIVITIES[key];
}

export type { ActivityProps };
