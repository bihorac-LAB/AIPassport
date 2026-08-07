import type { Module } from './types';

/**
 * Module 2 — Alignment.
 * Consolidates legacy microskills 2.1, 2.3, 2.5, 2.6, 2.7.
 */
export const module2: Module = {
  key: 'module-2',
  position: 2,
  title: 'Alignment',
  subtitle: 'Ethics, fairness, and keeping a deployed model safe',
  summary:
    'Work through the ethical tensions a real biomedical AI project creates, then run the monitoring and transparency practices that keep a live model trustworthy.',
  accent: 'teal',
  contentVersion: 1,
  pages: [
    {
      key: 'm2p1',
      slug: 'principles-in-tension',
      position: 1,
      kind: 'explore',
      title: 'Principles in Tension',
      kicker: 'Module 2 · Page 1',
      lede:
        'Ethics in AI is rarely a choice between right and wrong. It is usually two defensible principles pulling in opposite directions, and someone has to decide.',
      objectives: [
        'Name the four bioethics principles and identify which are in tension in a concrete AI case.',
        'Explain why overall accuracy conceals subgroup failure, and which metrics expose it.',
        'Decide when reliance on an AI tool is appropriate and what control makes it defensible.',
      ],
      estimatedMinutes: 22,
      contentVersion: 1,
      requiredSections: ['m2p1-q1', 'm2p1-q2', 'm2p1-fairness', 'm2p1-q3', 'm2p1-transcription'],
      sections: [
        {
          kind: 'prose',
          id: 'm2p1-intro',
          heading: 'Four principles',
          body: [
            '**Autonomy** — people decide what happens to them and to their data. **Beneficence** — act to benefit. **Non-maleficence** — do not harm. **Justice** — distribute benefits and burdens fairly.',
            'Individually they are uncontroversial. The work begins when they conflict, which in AI they almost always do: a model that helps most patients (beneficence) while performing worse for one group (justice) is the single most common ethical shape in this field.',
          ],
        },
        {
          kind: 'callout',
          id: 'm2p1-case',
          tone: 'neutral',
          heading: 'The case',
          body: [
            'Dr. Lee has built a model that predicts disease risk from genetic data. It identifies high-risk individuals early enough for preventive care, and validation shows it works.',
            'It also systematically over-predicts risk for two racial groups, because the training cohort was overwhelmingly of European ancestry. Deploying it would benefit many patients now. It would also generate false alarms — extra tests, extra anxiety, extra cost — concentrated in populations already poorly served.',
            'Delaying deployment for two years to build a representative cohort means everyone waits, including the groups the model currently fails.',
          ],
        },
        {
          kind: 'question',
          id: 'm2p1-q1',
          question: {
            key: 'm2p1.q1',
            version: 1,
            type: 'multi_choice',
            prompt: 'Which principles are in genuine tension in this case? Select all that apply.',
            options: [
              {
                value: 'beneficence',
                label: 'Beneficence — the model prevents disease for many patients now.',
                feedback: 'Yes. Withholding a working tool has a real cost that is easy to overlook.',
              },
              {
                value: 'justice',
                label: 'Justice — the benefit and the error are unevenly distributed.',
                feedback:
                  'Yes. This is the crux: unequal performance means unequal benefit from the same tool.',
              },
              {
                value: 'nonmaleficence',
                label: 'Non-maleficence — false positives cause real harm.',
                feedback:
                  'Yes. Unnecessary biopsies, surveillance, and insurance consequences are harms, not inconveniences.',
              },
              {
                value: 'autonomy',
                label: 'Autonomy — patients cannot meaningfully consent to a risk score they were not told is less reliable for them.',
                feedback:
                  'Yes, and this is the one most often missed. Disclosure of differential performance is an autonomy question.',
              },
            ],
            correct: ['beneficence', 'justice', 'nonmaleficence', 'autonomy'],
            explanation:
              'All four apply. Naming them individually is what turns "this feels wrong" into a decision you can defend and document.',
          },
        },
        {
          kind: 'question',
          id: 'm2p1-q2',
          heading: 'Make the call',
          intro:
            'There is no scored answer here. What matters is whether your reasoning names the principle you are subordinating and what you do to limit that cost.',
          question: {
            key: 'm2p1.q2',
            version: 1,
            type: 'single_choice',
            prompt: 'What should Dr. Lee do?',
            options: [
              {
                value: 'deploy_all',
                label: 'Deploy to everyone now; fix the disparity in the next version.',
                feedback:
                  'This maximizes immediate benefit and accepts a justice cost. It is defensible **only** with three things: disclosure of the differential performance to clinicians and patients, a stated timeline for remediation, and monitoring that would detect harm. Without those it is the disparity-entrenching option.',
              },
              {
                value: 'deploy_restricted',
                label: 'Deploy only for the population where it is validated, and recruit for the rest.',
                feedback:
                  'The most common real-world answer, and it has a real cost people gloss over: it delivers benefit first to the already-better-served group. Defensible when paired with genuinely funded recruitment — not "we intend to."',
              },
              {
                value: 'delay',
                label: 'Delay entirely until performance is equitable.',
                feedback:
                  'Principled and expensive. Everyone forgoes benefit, including the under-served groups. Ask honestly: is the two-year cohort actually funded, or does "delay" mean "never"?',
              },
              {
                value: 'recalibrate',
                label: 'Deploy with group-specific recalibration and a higher alert threshold for the affected groups.',
                feedback:
                  'Technically the strongest option and the one most likely to be missed. Recalibration can reduce differential false-positive rates without new data collection. It raises its own question — is using race as a model input appropriate here? — which is exactly the discussion worth having.',
              },
            ],
            explanation:
              'Any of these can be right. What is never right is deploying without disclosure, monitoring, or a plan — because then nobody has made a decision at all.',
          },
        },
        {
          kind: 'prose',
          id: 'm2p1-fairness-intro',
          heading: 'What a disparity actually looks like',
          body: [
            'Overall accuracy hides subgroup failure. A model can be 88% accurate everywhere and miss half the cases in a group that is 8% of your cohort, because that group barely moves the average.',
            'Below is a real-shaped diagnostic cohort. Split it by subgroup and by decision threshold, and watch which metric hides the problem and which exposes it.',
          ],
        },
        {
          kind: 'activity',
          id: 'm2p1-fairness',
          activity: 'fairness-explorer',
          heading: 'Subgroup performance explorer',
          intro:
            'Predict first: do you expect sensitivity to be higher or lower in the smaller subgroup? Then look.',
          summary:
            'Learner compares accuracy, sensitivity, specificity, and PPV across subgroups at varying thresholds and sees that overall accuracy conceals subgroup failure.',
        },
        {
          kind: 'question',
          id: 'm2p1-q3',
          question: {
            key: 'm2p1.q3',
            version: 1,
            type: 'single_choice',
            prompt:
              'Your model has identical overall accuracy for two subgroups, but sensitivity is 0.82 in one and 0.61 in the other. What does that mean in practice?',
            options: [
              {
                value: 'missed_cases',
                label: 'The second group has substantially more missed cases — the model under-detects their disease.',
                feedback:
                  'Correct. Equal accuracy with unequal sensitivity usually means differing prevalence and a threshold that suits one group. The concrete harm is missed diagnoses.',
              },
              {
                value: 'fine',
                label: 'Nothing important — accuracy is equal, so the model is fair.',
                feedback:
                  'Equal accuracy is one of the weakest fairness criteria. It is satisfiable by being right about the majority class in a low-prevalence group while missing most actual cases.',
              },
              {
                value: 'more_data',
                label: 'It only means the second group has a smaller sample.',
                feedback:
                  'Sample size affects your *certainty* about the gap, not its existence. Check the confidence intervals, but do not use small n to dismiss it.',
              },
            ],
            correct: 'missed_cases',
            explanation:
              'Always report sensitivity, specificity, and PPV per subgroup, with intervals. "Overall accuracy" is the metric most likely to let a disparity through.',
          },
        },
        {
          kind: 'prose',
          id: 'm2p1-transcription-intro',
          heading: 'Appropriate reliance',
          body: [
            'A research team adopted an AI transcription tool for qualitative interviews, expecting more accurate notes. On review, the transcripts contained fabricated passages that never occurred, characterized some interviewees as aggressive when they were not, degraded badly for accented speech, and stored identifiable information in file metadata.',
            'The interesting question is not "is this tool bad." It is: under what conditions, if any, would using it be defensible?',
          ],
        },
        {
          kind: 'question',
          id: 'm2p1-transcription',
          question: {
            key: 'm2p1.q4',
            version: 1,
            type: 'free_text',
            prompt:
              'Should the team use the tool? Name the specific failure that concerns you most and the control that would have to be in place before you would accept it.',
            placeholder:
              'e.g. The fabricated passages are disqualifying for verbatim analysis because… but with 100% human verification against audio it could still save time on…',
            minLength: 80,
            rows: 6,
            explanation:
              'A strong answer separates the four failures by severity. Fabrication and the tone misattribution are the serious ones: they corrupt the data and could defame a participant. Accent degradation is a systematic bias that skews which voices are represented. Metadata PHI is a compliance failure with a straightforward technical fix. "Human verification against the audio" is the control that makes fabrication survivable — and it removes most of the time saving, which is the honest trade-off.',
          },
        },
        {
          kind: 'reveal',
          id: 'm2p1-more',
          label: 'Learn more: fairness definitions that cannot all hold at once',
          body: [
            '**Demographic parity** — equal positive-prediction rates across groups. **Equal opportunity** — equal sensitivity. **Predictive parity** — equal PPV. **Calibration** — a predicted 70% means 70% in every group.',
            'It is mathematically proven that when true prevalence differs between groups, you cannot satisfy calibration, equal sensitivity, and equal PPV simultaneously. This is not a gap in the literature; it is an impossibility result.',
            'So the practical task is to choose which fairness criterion matters for **this** decision and say so. For a screening test that triggers further investigation, equal sensitivity usually matters most: a missed case is worse than an extra test.',
          ],
        },
      ],
    },
    {
      key: 'm2p2',
      slug: 'quality-and-safety',
      position: 2,
      kind: 'apply',
      title: 'Quality and Safety',
      kicker: 'Module 2 · Page 2',
      lede:
        'A model that passed validation can still be wrong next year. Drift, miscalibration, and undocumented limits are how good models cause harm.',
      objectives: [
        'Distinguish covariate shift from concept drift and describe how each is detected.',
        'Separate discrimination from calibration and explain why a high AUC can still mislead a care pathway.',
        'Write a model card that states intended use, out-of-scope use, and subgroup limitations.',
      ],
      estimatedMinutes: 25,
      contentVersion: 1,
      requiredSections: ['m2p2-drift', 'm2p2-q1', 'm2p2-calibration', 'm2p2-q2', 'm2p2-modelcard'],
      sections: [
        {
          kind: 'prose',
          id: 'm2p2-intro',
          heading: 'Validation is a snapshot',
          body: [
            'Your model learned a relationship between inputs and outcomes in one population at one time. Deployment does not freeze either. A lab changes assay. A new guideline shifts who gets admitted. A pandemic changes who is in the hospital at all.',
            'When the inputs shift, it is **covariate shift**. When the input-to-outcome relationship shifts, it is **concept drift**. The first is easier to detect; the second is more dangerous, because your inputs look normal.',
          ],
        },
        {
          kind: 'activity',
          id: 'm2p2-drift',
          activity: 'drift-simulator',
          heading: 'Drift and retraining',
          intro:
            'A sepsis model deployed twelve months ago. Advance time, watch the lactate distribution move away from what the model learned, and decide whether to retrain.',
          summary:
            'Learner advances deployment time to induce covariate shift, observes the false-positive rate climb, and compares doing nothing against retraining.',
        },
        {
          kind: 'question',
          id: 'm2p2-q1',
          question: {
            key: 'm2p2.q1',
            version: 1,
            type: 'single_choice',
            prompt:
              'Your sepsis alert\'s false-positive rate has doubled over six months. Nurses now dismiss most alerts. What is the first thing to check?',
            options: [
              {
                value: 'input_dist',
                label: 'Whether the input distributions have moved compared with the training data.',
                feedback:
                  'Correct, and it is the cheapest check available: it needs no outcome labels, so you can run it weekly. If lactate or WBC has shifted, you have found covariate shift.',
              },
              {
                value: 'retrain',
                label: 'Retrain immediately on the last six months of data.',
                feedback:
                  'Retraining before diagnosing risks baking in the problem. If the shift came from a miscalibrated analyzer, you would be teaching the model that bad values are normal.',
              },
              {
                value: 'threshold',
                label: 'Raise the alert threshold until the alert volume looks reasonable.',
                feedback:
                  'This suppresses the symptom and silently reduces sensitivity — you will miss real sepsis. It might be a justified stopgap, but only after you know what changed.',
              },
              {
                value: 'training',
                label: 'Retrain the nursing staff on the importance of responding to alerts.',
                feedback:
                  'Alert fatigue is a rational response to a low-precision alert. The people are behaving correctly; the model is the problem.',
              },
            ],
            correct: 'input_dist',
            explanation:
              'Diagnose before intervening. Distribution monitoring needs no labels and runs continuously, which is why it belongs in every deployment plan from day one.',
          },
        },
        {
          kind: 'prose',
          id: 'm2p2-calibration-intro',
          heading: 'A model can rank perfectly and still lie about probability',
          body: [
            '**Discrimination** (AUC) asks: does the model rank sicker patients above healthier ones? **Calibration** asks: when it says 30%, does 30% of that group actually have the outcome?',
            'These come apart constantly. A vendor model trained on a healthier population can rank your patients correctly — AUC 0.88, looks great — while systematically under-stating their absolute risk. If your protocol says "admit above 40%," you are now under-admitting, and the AUC never told you.',
          ],
        },
        {
          kind: 'activity',
          id: 'm2p2-calibration',
          activity: 'calibration-lab',
          heading: 'Calibration vs. discrimination',
          intro:
            'A vendor readmission model, evaluated on a local population you can make progressively less like the vendor\'s. Predict what happens to AUC before you move the slider.',
          summary:
            'Learner increases population mismatch and observes that AUC stays high while the reliability diagram bends away from the diagonal.',
        },
        {
          kind: 'question',
          id: 'm2p2-q2',
          question: {
            key: 'm2p2.q2',
            version: 1,
            type: 'single_choice',
            prompt:
              'A vendor model has AUC 0.87 on your patients, but its reliability curve sits well below the diagonal. Your care pathway treats anyone above 40% predicted risk. What should you do?',
            options: [
              {
                value: 'recalibrate',
                label: 'Recalibrate on local data, then re-derive the threshold.',
                feedback:
                  'Correct. Below the diagonal means the model over-states risk, so a 40% cut point is capturing more people than intended. Recalibration (Platt scaling or isotonic regression) needs far less data than retraining and fixes exactly this.',
              },
              {
                value: 'accept',
                label: 'Accept it — AUC 0.87 shows the model works.',
                feedback:
                  'AUC is threshold-free and tells you nothing about whether "40%" means 40%. Your pathway depends on the absolute number.',
              },
              {
                value: 'retrain',
                label: 'Discard it and train your own model from scratch.',
                feedback:
                  'Possible, but you are throwing away good discrimination that you would have to rebuild. Recalibration preserves the ranking and fixes the probabilities.',
              },
              {
                value: 'lower',
                label: 'Lower the threshold to 20% so more patients are captured.',
                feedback:
                  'Moving an uncalibrated threshold by intuition is guessing. Fix the probabilities first, then choose the threshold from the sensitivity you need.',
              },
            ],
            correct: 'recalibrate',
            explanation:
              'Report both. Discrimination tells you whether the model ranks; calibration tells you whether its numbers mean what your protocol assumes.',
          },
        },
        {
          kind: 'prose',
          id: 'm2p2-modelcard-intro',
          heading: 'Write down the limits',
          body: [
            'Most AI harm in healthcare is not a wrong prediction. It is a right prediction used outside the conditions it was validated for — an adult model applied to a 14-year-old, an outpatient model applied in the ED.',
            'A model card is the artifact that prevents that. It is short, it is boring, and it is the difference between a tool and a liability.',
          ],
        },
        {
          kind: 'activity',
          id: 'm2p2-modelcard',
          activity: 'model-card-builder',
          heading: 'Build a model card',
          intro:
            'Complete a card for the sepsis model you just monitored. Your entries are saved and you can return to them.',
          summary:
            'Learner authors a model card covering intended use, out-of-scope use, training population, metrics, subgroup findings, and limitations.',
        },
        {
          kind: 'reveal',
          id: 'm2p2-more',
          label: 'Learn more: a minimum viable monitoring plan',
          body: [
            'Four things, checked on a schedule you write down before deployment:',
            '- **Input distributions**, weekly. No labels needed, catches covariate shift first.\n- **Prediction distribution**, weekly. A sudden change in alert volume is often the earliest visible signal.\n- **Outcome performance**, quarterly, once labels mature. AUC, calibration slope, and per-subgroup sensitivity.\n- **A pre-agreed trigger.** "If calibration slope falls outside 0.8–1.25, or subgroup sensitivity drops more than 0.10, we recalibrate." Decide the number while nobody is under pressure.',
            'Also decide in advance who is accountable for looking. Monitoring nobody owns is monitoring that does not happen.',
          ],
        },
      ],
    },
  ],
};
