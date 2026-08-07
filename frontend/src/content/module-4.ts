import type { Module } from './types';

/**
 * Module 4 — Machine Learning.
 * Consolidates legacy microskills 4.1, 4.2, 4.4, 4.5, 4.6, 4.7. (4.3 was a duplicate of 4.2.)
 */
export const module4: Module = {
  key: 'module-4',
  position: 4,
  title: 'Machine Learning',
  subtitle: 'How models learn, and how to tell whether one is any good',
  summary:
    'Build an intuition for fitting, complexity, and validation, then evaluate and explain a model the way a reviewer or a clinician would.',
  accent: 'amber',
  contentVersion: 1,
  pages: [
    {
      key: 'm4p1',
      slug: 'how-models-learn',
      position: 1,
      kind: 'explore',
      title: 'How Models Learn',
      kicker: 'Module 4 · Page 1',
      lede:
        'A model fits a boundary through examples. Everything interesting follows from one question: how closely should it follow the data it was given?',
      objectives: [
        'Distinguish overfitting from underfitting using the gap between training and test performance.',
        'Identify the complexity at which a model stops generalizing.',
        'Choose a validation strategy appropriate to repeated measures and class imbalance.',
      ],
      estimatedMinutes: 24,
      contentVersion: 1,
      requiredSections: ['m4p1-q1', 'm4p1-boundary', 'm4p1-q2', 'm4p1-curve', 'm4p1-cv', 'm4p1-q3'],
      sections: [
        {
          kind: 'prose',
          id: 'm4p1-intro',
          heading: 'Features, labels, and the split',
          body: [
            '**Features** are what the model sees — age, creatinine, gene expression. The **label** is what it predicts. **Training** finds a rule mapping one to the other. **Testing** checks that rule on examples it has never seen.',
            'The test set is the entire basis for believing anything. If any information about it reached training — the same patient in both, a scaler fitted before splitting, a hyperparameter tuned on test scores — your reported performance is fiction.',
          ],
        },
        {
          kind: 'question',
          id: 'm4p1-q1',
          heading: 'Predict before you look',
          intro:
            'You will build this exact intuition in the next activity. Commit to an answer first — the comparison is what makes it stick.',
          question: {
            key: 'm4p1.q1',
            version: 1,
            type: 'single_choice',
            prompt:
              'A k-nearest-neighbour classifier with k=1 labels each new point by its single closest neighbour. How will its accuracy on the training data compare with a model using k=25?',
            options: [
              {
                value: 'much_higher',
                label: 'Much higher — close to perfect.',
                feedback:
                  'Correct, and it means nothing. With k=1 each training point is its own nearest neighbour, so training accuracy is ~100% by construction. This is why training accuracy is never evidence.',
              },
              {
                value: 'similar',
                label: 'About the same.',
                feedback:
                  'They differ sharply on training data. k=1 memorizes it; k=25 averages over a wide neighbourhood and will misclassify some training points.',
              },
              {
                value: 'lower',
                label: 'Lower, because k=1 is too simple.',
                feedback:
                  'k=1 is the *most* complex setting, not the simplest — it can carve out a region around every single point. Larger k means a smoother, simpler boundary.',
              },
            ],
            correct: 'much_higher',
            explanation:
              'High training accuracy with low test accuracy is the signature of overfitting. You are about to see the boundary that produces it.',
          },
        },
        {
          kind: 'activity',
          id: 'm4p1-boundary',
          activity: 'decision-boundary',
          heading: 'Overfitting and underfitting',
          intro:
            'The same patients, two model complexities, side by side. Watch the boundary shape change and the two accuracy numbers move apart.',
          summary:
            'Learner varies model complexity and compares decision-boundary shape against training and test accuracy.',
        },
        {
          kind: 'question',
          id: 'm4p1-q2',
          question: {
            key: 'm4p1.q2',
            version: 1,
            type: 'single_choice',
            prompt:
              'Your model scores 0.97 on training data and 0.71 on held-out data. What does that gap indicate?',
            options: [
              {
                value: 'overfit',
                label: 'Overfitting — the model learned patterns specific to the training sample.',
                feedback:
                  'Correct. The remedies are more data, a simpler model, regularization, or fewer features — and re-checking for leakage while you are there.',
              },
              {
                value: 'underfit',
                label: 'Underfitting — the model is too simple.',
                feedback:
                  'Underfitting looks different: both scores are poor and close together. A large gap means the model captured too much, not too little.',
              },
              {
                value: 'test_hard',
                label: 'The test set happens to be harder.',
                feedback:
                  'Possible with a small or unluckily-split test set — which is precisely why cross-validation exists. But a 26-point gap is far more likely to be overfitting.',
              },
            ],
            correct: 'overfit',
            explanation:
              'Watch the gap, not either number alone. Then find the complexity where test performance peaks — which is what the next activity does.',
          },
        },
        {
          kind: 'activity',
          id: 'm4p1-curve',
          activity: 'complexity-curve',
          heading: 'Find the sweet spot',
          intro:
            'Training and test accuracy across the whole complexity range. Look for where they separate — that is where memorization begins.',
          summary:
            'Learner sweeps model complexity and identifies the divergence point between training and test accuracy.',
        },
        {
          kind: 'prose',
          id: 'm4p1-cv-intro',
          heading: 'One split is a coin flip',
          body: [
            'With 200 patients, a single train/test split gives you one number with a wide confidence interval. Split differently and you get a different answer. **Cross-validation** rotates the held-out portion so every case is tested once, giving you a mean and — more usefully — a spread.',
            'A wide spread is information: it says your estimate is unstable, and reporting a single point estimate would be misleading.',
          ],
        },
        {
          kind: 'activity',
          id: 'm4p1-cv',
          activity: 'cross-validation',
          heading: 'Compare validation strategies',
          intro:
            'Watch what changes between a single split, k-fold, stratified k-fold, and grouping by patient — especially the variance.',
          summary:
            'Learner compares validation strategies and observes fold-to-fold variance and the effect of stratification and grouping.',
        },
        {
          kind: 'question',
          id: 'm4p1-q3',
          question: {
            key: 'm4p1.q3',
            version: 1,
            type: 'single_choice',
            prompt:
              'Your dataset has 200 admissions from 120 unique patients — some patients appear more than once. Which validation strategy is appropriate?',
            options: [
              {
                value: 'grouped',
                label: 'Grouped cross-validation, keeping all of a patient\'s admissions in the same fold.',
                feedback:
                  'Correct. Otherwise the model sees the same patient in training and testing and can recognize the individual rather than the condition. This is the most common silent leak in clinical ML.',
              },
              {
                value: 'stratified',
                label: 'Stratified k-fold on the outcome.',
                feedback:
                  'Stratification balances outcome prevalence across folds, which is worth doing — but it does nothing about the same patient appearing on both sides. Use grouped *and* stratified where you can.',
              },
              {
                value: 'random',
                label: 'Standard k-fold; with 200 rows the effect is negligible.',
                feedback:
                  'With 80 repeat admissions among 200 rows the effect is substantial, and it inflates performance in exactly the flattering direction.',
              },
              {
                value: 'loo',
                label: 'Leave-one-out, since the dataset is small.',
                feedback:
                  'Leave-one-out uses the data efficiently but has the same patient-leakage problem, and its variance estimate is unreliable.',
              },
            ],
            correct: 'grouped',
            explanation:
              'Ask what unit your conclusion is about. If it is patients, patients must not straddle the split — whatever the rows look like.',
          },
        },
        {
          kind: 'reveal',
          id: 'm4p1-more',
          label: 'Learn more: choosing a model family',
          body: [
            '**Logistic regression** — few features, need interpretable coefficients and odds ratios, small n. Still the right default for most clinical prediction tasks, and a baseline you must beat before claiming anything.',
            '**Tree ensembles (random forest, gradient boosting)** — tabular data with non-linear interactions and mixed types. Usually the strongest performer on structured clinical data.',
            '**Deep learning** — images, waveforms, text, or very large n. On a 500-row tabular dataset it will typically lose to logistic regression while being far harder to explain.',
            'The honest sequence: start with logistic regression, report it, and only add complexity that measurably earns its cost in interpretability.',
          ],
        },
      ],
    },
    {
      key: 'm4p2',
      slug: 'evaluating-models',
      position: 2,
      kind: 'apply',
      title: 'Evaluating and Explaining',
      kicker: 'Module 4 · Page 2',
      lede:
        'Accuracy is the least useful metric in medicine. The threshold you choose is a clinical decision, not a technical default.',
      objectives: [
        'Explain why accuracy is inadequate for imbalanced clinical outcomes.',
        'Predict how sensitivity, specificity, and PPV move as the decision threshold changes.',
        'Explain why PPV depends on prevalence and what that means for deployment.',
        'Distinguish global from local model explanation and use each appropriately.',
      ],
      estimatedMinutes: 26,
      contentVersion: 1,
      requiredSections: ['m4p2-q1', 'm4p2-threshold', 'm4p2-q2', 'm4p2-explain', 'm4p2-whatif', 'm4p2-q3'],
      sections: [
        {
          kind: 'prose',
          id: 'm4p2-intro',
          heading: 'Why accuracy misleads',
          body: [
            'Take a condition affecting 2% of patients. A model that predicts "no" for everybody is 98% accurate and clinically worthless. Accuracy is dominated by the majority class, and in medicine the minority class is the reason you built the model.',
            'What you need instead: **sensitivity** (of those with the condition, how many did we catch?), **specificity** (of those without it, how many did we correctly clear?), and **PPV** (of those we flagged, how many actually have it?). PPV depends on prevalence, which is why a model can transfer between hospitals and still become unusable.',
          ],
        },
        {
          kind: 'question',
          id: 'm4p2-q1',
          heading: 'Predict first',
          question: {
            key: 'm4p2.q1',
            version: 1,
            type: 'single_choice',
            prompt:
              'You lower the decision threshold from 0.5 to 0.3 so the model flags more patients. What happens?',
            options: [
              {
                value: 'sens_up_spec_down',
                label: 'Sensitivity rises, specificity falls.',
                feedback:
                  'Correct, and this trade is unavoidable — it is the same model, just a different cut point. The question is never "which is better" but "which error costs more here".',
              },
              {
                value: 'both_up',
                label: 'Both rise, because the model is more cautious.',
                feedback:
                  'Moving one threshold cannot improve both. To improve both you need a genuinely better model, not a different cut point.',
              },
              {
                value: 'auc_up',
                label: 'AUC rises.',
                feedback:
                  'AUC is computed across all thresholds, so it does not change when you pick one. That is exactly why AUC alone cannot tell you how the model will behave in your clinic.',
              },
            ],
            correct: 'sens_up_spec_down',
            explanation:
              'For a screening test that triggers a cheap confirmatory step, buy sensitivity. For one that triggers an invasive procedure, protect specificity.',
          },
        },
        {
          kind: 'activity',
          id: 'm4p2-threshold',
          activity: 'threshold-explorer',
          heading: 'Move the threshold',
          intro:
            'A diagnostic model on 400 patients. Move the threshold and watch the confusion matrix, every metric, and the ROC operating point move together.',
          summary:
            'Learner varies the decision threshold and observes the coupled movement of the confusion matrix, sensitivity, specificity, PPV, F1, and the ROC operating point.',
        },
        {
          kind: 'question',
          id: 'm4p2-q2',
          question: {
            key: 'm4p2.q2',
            version: 1,
            type: 'slider_estimate',
            prompt:
              'A test with 90% sensitivity and 90% specificity is applied where the condition affects 1% of patients. Of 100 patients who test positive, roughly how many actually have the condition?',
            min: 0,
            max: 100,
            step: 1,
            unit: '%',
            correct: { min: 4, max: 14 },
            explanation:
              'About 8%. Out of 10,000 patients, 100 have the condition and 90 are caught; 9,900 do not and 990 test positive anyway. So 90 true positives among 1,080 positives ≈ 8%. A "90/90" test is right about the diagnosis roughly one time in twelve at this prevalence — the single most consequential fact about screening, and the most counter-intuitive.',
            correctFeedback:
              'Close. The answer is ~8%, and most people guess 90%. False positives from the large healthy majority swamp the true positives.',
            incorrectFeedback:
              'The answer is ~8%. Work it through with 10,000 patients: 100 with the condition → 90 caught. 9,900 without → 990 false positives. 90 / (90 + 990) ≈ 8%.',
          },
        },
        {
          kind: 'callout',
          id: 'm4p2-ppv-note',
          tone: 'info',
          heading: 'Why this decides deployments',
          body: [
            'A model validated in a specialist clinic where 30% of referrals are positive will have a respectable PPV. Move it to primary care where 2% are positive and the same model — unchanged, same sensitivity, same specificity — starts producing mostly false alarms.',
            'Sensitivity and specificity are properties of the model. PPV is a property of the model *and the population*. Always state the prevalence your PPV assumes.',
          ],
        },
        {
          kind: 'prose',
          id: 'm4p2-explain-intro',
          heading: 'Global and local explanation',
          body: [
            'Two different questions. **Global**: across all patients, which features drive this model? Useful for sanity-checking that it learned medicine rather than an artifact. **Local**: for *this* patient, why this prediction? That is what a clinician needs at the point of care.',
            'A model can be globally sensible and locally absurd. Both views are necessary.',
          ],
        },
        {
          kind: 'activity',
          id: 'm4p2-explain',
          activity: 'explanation-lab',
          heading: 'Explain the model',
          intro:
            'Global feature contributions, then any individual patient\'s breakdown. Look for a patient whose explanation contradicts the global picture.',
          summary:
            'Learner compares global feature importance with per-patient contribution breakdowns from a transparent logistic model.',
        },
        {
          kind: 'activity',
          id: 'm4p2-whatif',
          activity: 'what-if',
          heading: 'What-if simulator',
          intro:
            'Build a patient one variable at a time and watch the predicted risk respond. Find the variable that moves the prediction most — and then ask whether that is clinically sensible.',
          summary:
            'Learner constructs a synthetic patient profile and observes the model\'s live risk prediction and confidence.',
        },
        {
          kind: 'question',
          id: 'm4p2-q3',
          question: {
            key: 'm4p2.q3',
            version: 1,
            type: 'free_text',
            prompt:
              'You are presenting this model to clinicians who will use it. In three or four sentences, describe its performance and its limits in the way you would actually say it out loud.',
            placeholder:
              'e.g. At the threshold we chose it catches about 8 in 10 cases, and about 1 in 3 flagged patients turn out to have the condition. It has not been validated for patients under 18 or for…',
            minLength: 100,
            rows: 6,
            explanation:
              'A good version names the operating point (not just AUC), states PPV with the prevalence it assumes, names at least one population where the model is not validated, and says what the clinician should do when they disagree with it. If you said "AUC 0.87" and stopped, the audience learned nothing actionable.',
          },
        },
        {
          kind: 'reveal',
          id: 'm4p2-more',
          label: 'Learn more: reading a ROC curve honestly',
          body: [
            'AUC is the probability that a randomly chosen positive case is ranked above a randomly chosen negative one. It is threshold-free, prevalence-independent, and therefore silent about how the model behaves in your clinic.',
            'For rare outcomes, the **precision-recall curve** and its area (average precision) are more informative: they focus on the minority class instead of being dominated by the easy negatives.',
            'And report a confidence interval. On 200 patients, an AUC of 0.87 might carry a 95% CI of 0.79–0.94 — which means it is not distinguishable from a model reported at 0.81.',
          ],
        },
      ],
    },
  ],
};
