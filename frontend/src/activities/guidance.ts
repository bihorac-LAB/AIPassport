/**
 * One line per activity describing its educational purpose.
 *
 * Exported into the backend manifest so the AI tutor knows what the learner is doing without the
 * client having to post a free-form description it could manipulate.
 */
export const ACTIVITY_GUIDANCE: Record<string, string> = {
  'concept-sorter':
    'Learner classifies real biomedical systems as rule-based AI, machine learning, or deep learning. Guide toward the origin of the rules, not the presence of data.',
  'ai-timeline':
    'Learner explores 15 AI milestones from 1950 to 2025, filtered by era and paradigm. Emphasize that data and compute, not new theory, drove the deep learning era.',
  'lifecycle-simulator':
    'Learner makes six sequential study-design decisions and receives consequences. The high-stakes decisions are the data split and the choice of outcome variable.',
  'split-strategy':
    'Learner compares random, temporal, site-held-out, and grouped splits. The point is that a random split inflates the score because it shares setting between train and test.',
  'outlier-lab':
    'Learner applies IQR or z-score detection then compares removal, winsorizing, and median imputation. The point is that statistical rules cannot separate errors from real extremes.',
  'fairness-explorer':
    'Learner compares metrics across subgroups at varying thresholds. The point is that overall accuracy hides subgroup failure and sensitivity exposes it.',
  'drift-simulator':
    'Learner advances deployment time to induce covariate shift and compares doing nothing against retraining. Emphasize diagnosing before intervening.',
  'calibration-lab':
    'Learner increases population mismatch and sees AUC stay high while calibration degrades. The point is that ranking and probability are separate properties.',
  'model-card-builder':
    'Learner authors a model card. Push for specific out-of-scope populations rather than generic caveats.',
  'consent-rewriter':
    'Learner rewrites consent language across literacy levels. The point is that consent requires comprehension, not a signature.',
  'representation-planner':
    'Learner sets a representation target and selects active recruitment strategies. The point is that passive recruitment reproduces existing access inequities.',
  'security-audit':
    'Learner assembles layered data protections and sees which residual risks remain. Encourage proportionality to data sensitivity.',
  'omop-mapper':
    'Learner maps source values to standard concept identifiers. The point is data minimization: keep only fields an analysis requires.',
  'label-agreement':
    'Learner varies annotator count and compares percent agreement with Cohen\'s kappa. The point is that label quality caps achievable model performance.',
  'preprocessing-pipeline':
    'Learner tunes outlier threshold, imputation, and scaling. Emphasize that mean imputation assumes missingness is unrelated to severity.',
  'federated-round':
    'Learner runs local training and aggregation across two sites. The point is that federation solves data transfer, not data quality or representation.',
  'decision-boundary':
    'Learner varies model complexity and compares boundary shape with train/test accuracy. The point is the gap, not either number.',
  'complexity-curve':
    'Learner sweeps complexity to find where train and test accuracy diverge. That divergence point is where memorization begins.',
  'cross-validation':
    'Learner compares single split, k-fold, stratified, and grouped validation. Emphasize fold-to-fold variance and patient-level grouping.',
  'threshold-explorer':
    'Learner moves the decision threshold and watches the confusion matrix and every metric respond. The point is that threshold choice is a clinical decision.',
  'explanation-lab':
    'Learner compares global feature importance with per-patient contributions. The point is that a model can be globally sensible and locally wrong.',
  'what-if':
    'Learner builds a synthetic patient and watches predicted risk respond. Push toward asking whether the sensitivity is clinically plausible.',
  'pixel-reveal':
    'Learner toggles between rendered pixels and their numeric values. The point is that an image is an array of intensities.',
  'attenuation-phantom':
    'Learner sets tissue densities and watches the intensity histogram. The point is that overlapping distributions make findings hard for models and humans alike.',
  'window-level':
    'Learner adjusts window centre and width. The point is that the same data under a different mapping is a different model input.',
  'convolution-lab':
    'Learner applies kernels and steps through the per-position arithmetic. The point is that a CNN learns these nine numbers rather than being given them.',
  'noise-denoise':
    'Learner compares mean and median filtering on impulse noise. The point is the same robustness property seen with clinical outliers.',
  'histogram-equalization':
    'Learner compares global equalization with CLAHE. The point is that enhancement amplifies noise along with signal.',
  'imaging-checklist':
    'Learner audits an imaging pipeline for reproducibility. Each unchecked item names a specific replication failure.',
  tokenizer:
    'Learner tokenizes biomedical text and sees rare terms fragment. The point is that fragmentation signals thin training evidence.',
  'next-token':
    'Learner inspects next-token probabilities and manipulates temperature. The point is that plausibility, not truth, is being optimized.',
  'embedding-space':
    'Learner explores semantic similarity between biomedical terms and finds misleading proximities.',
  'hallucination-hunt':
    'Learner flags fabricated claims in fluent generated text. The point is that specific numbers and identifiers carry the most risk.',
  'study-designer':
    'Learner specifies question, data, comparator, metric, validation, and risk for their own project. The comparator and baseline are the most commonly missing pieces.',
};
