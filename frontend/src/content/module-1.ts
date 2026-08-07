import type { Module } from './types';

/**
 * Module 1 — Fundamentals.
 * Consolidates legacy microskills 1.1–1.7 into two pages. See docs/legacy-audit.md §5–6.
 */
export const module1: Module = {
  key: 'module-1',
  position: 1,
  title: 'Fundamentals',
  subtitle: 'What AI is, and how an AI study is actually built',
  summary:
    'Replace the mystique around AI with a working mental model, then walk the path from a research question to a validated model.',
  accent: 'blue',
  contentVersion: 1,
  pages: [
    {
      key: 'm1p1',
      slug: 'demystifying-ai',
      position: 1,
      kind: 'explore',
      title: 'Demystifying AI',
      kicker: 'Module 1 · Page 1',
      lede:
        'AI is not magic, not sentient, and not new. It is a set of methods for finding patterns in data — built by people, for specific problems.',
      objectives: [
        'Distinguish artificial intelligence, machine learning, and deep learning by where the rules come from.',
        'Place major AI milestones in historical context and explain why deep learning became dominant when it did.',
        'Evaluate a claim about AI as fact, conditional, misleading, or not a claim at all.',
      ],
      estimatedMinutes: 18,
      contentVersion: 1,
      requiredSections: ['m1p1-nesting', 'm1p1-q1', 'm1p1-timeline', 'm1p1-q2', 'm1p1-fof'],
      sections: [
        {
          kind: 'prose',
          id: 'm1p1-intro',
          heading: 'Three words people use interchangeably',
          summary: 'Establishes the AI / ML / DL relationship before any technique is named.',
          body: [
            '**Artificial intelligence** is the broad goal: get a computer to do something we would call intelligent. **Machine learning** is one way to get there — instead of writing the rules, you show the computer examples and it derives the rules. **Deep learning** is machine learning using many-layered neural networks.',
            'They nest. Every deep learning system is machine learning; every machine learning system is AI; not all AI is machine learning. A 1980s expert system that diagnosed infections from hand-written IF-THEN rules was AI and learned nothing.',
            'That distinction matters clinically. If a tool learned from examples, its behavior depends on **which** examples — which is why "it works at our hospital" and "it works at yours" are different claims.',
          ],
        },
        {
          kind: 'activity',
          id: 'm1p1-nesting',
          activity: 'concept-sorter',
          heading: 'Sort the systems',
          intro:
            'Six real biomedical tools. Place each one at the right level. You will get a reason for each answer, right or wrong.',
          summary: 'Learner classifies real systems as rule-based AI, machine learning, or deep learning.',
        },
        {
          kind: 'question',
          id: 'm1p1-q1',
          heading: 'Check your model',
          question: {
            key: 'm1p1.q1',
            version: 1,
            type: 'single_choice',
            prompt:
              'A hospital installs a sepsis alert that fires when heart rate, temperature, and white cell count each cross fixed thresholds written by a clinical committee. Is this machine learning?',
            options: [
              {
                value: 'no_rules',
                label: 'No — the rules were written by people, not learned from data.',
                feedback:
                  'Correct. This is rule-based AI. It can be useful and it is auditable, but it did not learn anything, so it cannot discover a pattern the committee did not already know.',
              },
              {
                value: 'yes_data',
                label: 'Yes — it uses patient data to make a prediction.',
                feedback:
                  'Using data at prediction time is not learning. The question is where the rules came from. Here a committee wrote them, so nothing was learned from examples.',
              },
              {
                value: 'yes_ai',
                label: 'Yes — anything called AI is machine learning.',
                feedback:
                  'AI is the wider category. Rule-based expert systems were the dominant form of AI for decades and involve no learning at all.',
              },
            ],
            correct: 'no_rules',
            explanation:
              'The dividing line is the origin of the rules. Hand-written rules → rule-based AI. Rules derived from labelled examples → machine learning.',
          },
        },
        {
          kind: 'prose',
          id: 'm1p1-history-intro',
          heading: 'Why the field keeps surprising people',
          body: [
            'AI has moved in waves: a breakthrough, inflated expectations, then a "winter" when the technique hit its limits. Knowing the pattern is practical — it tells you to ask what a new method actually does better, not just what it is called.',
            'Two things changed in the 2010s that were not new ideas: labelled data at scale, and GPUs. Neural networks from the 1980s suddenly worked because they finally had enough of both.',
          ],
        },
        {
          kind: 'activity',
          id: 'm1p1-timeline',
          activity: 'ai-timeline',
          heading: 'The AI timeline',
          intro:
            'Fifteen milestones from 1950 to 2025. Filter by era or by paradigm and watch which approach was dominant when.',
          summary:
            'Learner explores major AI milestones and the paradigm shifts between symbolic AI, machine learning, deep learning, and generative AI.',
        },
        {
          kind: 'question',
          id: 'm1p1-q2',
          question: {
            key: 'm1p1.q2',
            version: 1,
            type: 'multi_choice',
            prompt:
              'Deep learning ideas existed in the 1980s but only became dominant around 2012. Which factors explain the gap? Select all that apply.',
            options: [
              {
                value: 'data',
                label: 'Large labelled datasets became available.',
                feedback: 'Yes — ImageNet-scale labelled data was the missing ingredient.',
              },
              {
                value: 'compute',
                label: 'GPUs made training deep networks practical.',
                feedback: 'Yes — the same maths ran orders of magnitude faster on graphics hardware.',
              },
              {
                value: 'brain',
                label: 'Scientists finally understood how the brain works.',
                feedback:
                  'No. Artificial neural networks are loosely brain-*inspired* but are not models of neuroscience, and no such breakthrough occurred.',
              },
              {
                value: 'improvements',
                label: 'Practical training improvements (activation functions, regularization, initialization).',
                feedback: 'Yes — unglamorous engineering advances made deep networks trainable.',
              },
            ],
            correct: ['data', 'compute', 'improvements'],
            explanation:
              'Data, compute, and training tricks — not a new theory of intelligence. This is why "the algorithm is better" is rarely the whole story behind a performance jump.',
          },
        },
        {
          kind: 'prose',
          id: 'm1p1-fof-intro',
          heading: 'Test a claim of your own',
          body: [
            'Most confusion about AI arrives as a confident sentence: *AI can already read scans better than radiologists.* *AI is unbiased because it is just maths.* *AI will replace clinicians.* Some are true under conditions, some are false, some are not really claims at all.',
            'Type a statement you have heard — or one you half-believe — and get a structured evaluation: a verdict, the conditions that make it true or false, real biomedical examples, and what would have to change.',
          ],
        },
        {
          kind: 'aiActivity',
          id: 'm1p1-fof',
          promptKey: 'fact_or_fiction',
          heading: 'AI: Fact or Fiction?',
          intro:
            'This activity uses a generative model to produce feedback. Read it critically — it is a study aid, not an authority. It can be wrong.',
          inputLabel: 'A statement about AI you want evaluated',
          placeholder: 'e.g. AI models are objective because they only look at the data.',
          submitLabel: 'Evaluate this statement',
          render: 'verdict',
        },
        {
          kind: 'reveal',
          id: 'm1p1-more',
          label: 'Learn more: why "the algorithm is biased" is imprecise',
          body: [
            'An algorithm is a procedure. Logistic regression has no opinion about anybody. What carries bias is the **data** it learned from, the **label** someone chose to predict, and the **decision** attached to the output.',
            'The clearest documented case: a widely used US care-management algorithm predicted future *health costs* as a proxy for future *health needs*. Because less money had historically been spent on Black patients at the same level of illness, the model systematically under-referred them. The maths was correct. The target variable was the harm.',
            'Say precisely which of the three you mean, and the fix becomes findable.',
          ],
        },
      ],
    },
    {
      key: 'm1p2',
      slug: 'question-to-model',
      position: 2,
      kind: 'apply',
      title: 'From Question to Model',
      kicker: 'Module 1 · Page 2',
      lede:
        'Every AI study is the same six decisions. Most failures happen in the first three, long before a model is trained.',
      objectives: [
        'Sequence the six decisions that make up an AI study and identify where failures actually occur.',
        'Recognize target leakage in a feature list.',
        'Choose a data-splitting strategy that accounts for time, site, and repeated patients.',
        'Justify an outlier-handling decision and describe it reproducibly.',
      ],
      estimatedMinutes: 25,
      contentVersion: 1,
      requiredSections: [
        'm1p2-lifecycle',
        'm1p2-q1',
        'm1p2-splitting',
        'm1p2-outliers',
        'm1p2-q2',
        'm1p2-reflection',
      ],
      sections: [
        {
          kind: 'prose',
          id: 'm1p2-intro',
          heading: 'The six decisions',
          body: [
            'Define the question → assemble the data → prepare it → choose and train a model → validate it → decide whether to deploy and monitor. That sequence does not change whether you are predicting readmission or classifying cell phenotypes.',
            'What changes is how much damage a bad decision does. A poor model choice costs you accuracy. A poor **data split** invents accuracy that does not exist.',
          ],
        },
        {
          kind: 'activity',
          id: 'm1p2-lifecycle',
          activity: 'lifecycle-simulator',
          heading: 'Run a study end to end',
          intro:
            'You are predicting 30-day readmission for heart-failure patients (or classifying compounds, if you prefer the basic-science track). Make each decision and see the consequence before you move on.',
          summary:
            'Learner makes the six lifecycle decisions and receives targeted consequences for each choice.',
        },
        {
          kind: 'question',
          id: 'm1p2-q1',
          heading: 'The most expensive mistake',
          question: {
            key: 'm1p2.q1',
            version: 1,
            type: 'single_choice',
            prompt:
              'A model predicting ICU mortality reaches AUC 0.94 in testing. One of its strongest features is "number of lab tests ordered in the last 6 hours." What should worry you most?',
            options: [
              {
                value: 'leakage',
                label: 'The feature may encode the outcome: dying patients get tested more.',
                feedback:
                  'Correct — this is target leakage. The feature is a consequence of deterioration, not an independent predictor of it, so the model looks brilliant retrospectively and is useless prospectively.',
              },
              {
                value: 'small',
                label: 'AUC 0.94 means the dataset is too small.',
                feedback:
                  'A high AUC is not itself evidence of a small dataset. The real problem here is what that particular feature represents.',
              },
              {
                value: 'nothing',
                label: 'Nothing — AUC 0.94 is an excellent result.',
                feedback:
                  'A suspiciously good result deserves more scrutiny, not less. Ask what each strong feature actually measures and when it becomes available.',
              },
              {
                value: 'interpretable',
                label: 'The model is not interpretable enough to trust.',
                feedback:
                  'Interpretability matters, but here the specific defect is identifiable without it: a feature that only exists because the outcome is already underway.',
              },
            ],
            correct: 'leakage',
            explanation:
              'Ask of every feature: would this value be available, with this meaning, at the moment I need the prediction? If it only exists because the outcome is already happening, it is leakage.',
          },
        },
        {
          kind: 'activity',
          id: 'm1p2-splitting',
          activity: 'split-strategy',
          heading: 'Split the data four ways',
          intro:
            'Ten thousand chest X-rays, three hospitals, five scanner models, three years. Choose a splitting strategy and see the internal score next to the score on a genuinely new hospital.',
          summary:
            'Learner compares random, temporal, site-held-out, and grouped splits and sees the internal-versus-external performance gap each produces.',
        },
        {
          kind: 'callout',
          id: 'm1p2-split-note',
          tone: 'info',
          heading: 'Why a random split flatters you',
          body: [
            'A random split puts images from the same patient, the same scanner, and the same month on both sides of the line. The model can then succeed by recognizing the *setting* rather than the *disease* — and the test set rewards it, because the test set shares that setting.',
            'A held-out hospital removes that shortcut. The score drops. That drop is not the model getting worse; it is the earlier number being wrong.',
          ],
        },
        {
          kind: 'prose',
          id: 'm1p2-outlier-intro',
          heading: 'Then there is the boring part that decides everything',
          body: [
            'Real clinical data contains a heart rate of 2, a temperature of 42, a blood pressure of 300. Some are transcription errors. Some are the sickest patient on the ward. You cannot tell them apart from the number alone, and what you do about them changes your results.',
            'The reproducibility problem is not that researchers handle outliers — it is that they rarely say how.',
          ],
        },
        {
          kind: 'activity',
          id: 'm1p2-outliers',
          activity: 'outlier-lab',
          heading: 'Outlier handling lab',
          intro:
            'Thirty ICU patients with real-looking vitals and a few genuine extremes. Set a detection rule, choose a handling strategy, and watch the mean, standard deviation, and median move.',
          summary:
            'Learner applies IQR or z-score detection, then compares removal, winsorizing, and median imputation on summary statistics.',
        },
        {
          kind: 'question',
          id: 'm1p2-q2',
          question: {
            key: 'm1p2.q2',
            version: 1,
            type: 'single_choice',
            prompt:
              'You remove all heart rates outside 1.5×IQR before modelling in-hospital mortality. What is the most likely consequence?',
            options: [
              {
                value: 'removes_signal',
                label: 'You remove some of the sickest patients, weakening the signal you care about.',
                feedback:
                  'Correct. Physiological extremes are often the strongest predictors of deterioration. A statistical outlier rule cannot tell a data-entry error from a crashing patient.',
              },
              {
                value: 'improves',
                label: 'Model accuracy reliably improves because noise is gone.',
                feedback:
                  'Accuracy on your cleaned test set may rise, but it has risen partly because you deleted the hard cases. That is not a real improvement.',
              },
              {
                value: 'nothing',
                label: 'Nothing much; outliers are rare by definition.',
                feedback:
                  'They are rare and disproportionately informative. In mortality prediction the tails carry most of the signal.',
              },
            ],
            correct: 'removes_signal',
            explanation:
              'Prefer clinical plausibility ranges over purely statistical ones, handle implausible values as missing rather than deleting the patient, and report exactly what you did.',
          },
        },
        {
          kind: 'question',
          id: 'm1p2-reflection',
          heading: 'Apply it to your own work',
          intro:
            'Short and specific beats long and general. Three or four sentences is enough.',
          question: {
            key: 'm1p2.q3',
            version: 1,
            type: 'free_text',
            prompt:
              'Think of a dataset you actually work with. Name one variable where an extreme value could be either an error or a real finding, and say how you would tell the difference.',
            placeholder:
              'e.g. In our registry, serum creatinine above 8 mg/dL is usually real (dialysis patients) but values below 0.2 are almost always unit errors, because…',
            minLength: 60,
            rows: 5,
            explanation:
              'The useful test is domain knowledge, not distribution: what value is physiologically possible, and what would have to be true for it to be real?',
          },
        },
        {
          kind: 'reveal',
          id: 'm1p2-more',
          label: 'Learn more: what to write in your methods section',
          body: [
            'Five sentences make an outlier decision reproducible: which variables you screened; the rule and its exact threshold; how many values it flagged; what you did with them; and whether your conclusions change if you do the opposite.',
            'That last sentence — the sensitivity analysis — is what separates a defensible choice from an arbitrary one. If your finding survives both removal and winsorizing, say so. If it does not, you have learned something important.',
          ],
        },
      ],
    },
  ],
};
