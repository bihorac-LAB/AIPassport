import type { Module } from './types';

/**
 * Module 3 — Data.
 * Consolidates legacy microskills 3.2–3.6.
 */
export const module3: Module = {
  key: 'module-3',
  position: 3,
  title: 'Data',
  subtitle: 'Sourcing it ethically, then making it usable',
  summary:
    'Audit a biomedical dataset against consent, representation, security, and benefit — then run the preparation decisions that determine what any model can learn.',
  accent: 'violet',
  contentVersion: 1,
  pages: [
    {
      key: 'm3p1',
      slug: 'sourcing-data',
      position: 1,
      kind: 'explore',
      title: 'Sourcing Data Responsibly',
      kicker: 'Module 3 · Page 1',
      lede:
        'Whose data is it, who is missing from it, how is it protected, and what do the people who provided it get back?',
      objectives: [
        'Explain why informed consent requires comprehension rather than a signature.',
        'Identify how passive recruitment reproduces existing inequities, and which strategies change that.',
        'Select data protections proportionate to the sensitivity of the data.',
        'Describe what a common data model standardizes and why fields are dropped.',
      ],
      estimatedMinutes: 22,
      contentVersion: 1,
      requiredSections: ['m3p1-consent', 'm3p1-q1', 'm3p1-representation', 'm3p1-security', 'm3p1-omop', 'm3p1-q2'],
      sections: [
        {
          kind: 'prose',
          id: 'm3p1-intro',
          heading: 'You are the compliance officer',
          body: [
            'A study protocol has arrived for review. It plans to build a risk model from a biomedical dataset — clinical records, or immunology specimens if you work in basic science. Your job is to find the failures before the data is collected, not after.',
            'Four audits: consent, representation, security, and benefit. Each one is a place real studies fail.',
          ],
        },
        {
          kind: 'activity',
          id: 'm3p1-consent',
          activity: 'consent-rewriter',
          heading: 'Audit 1 · Consent as comprehension',
          intro:
            'The protocol uses standard legal consent language. Read it, then move the plain-language control and watch what the participant is actually agreeing to.',
          summary:
            'Learner rewrites consent language across three literacy levels and sees the effect on comprehension and on what the participant can meaningfully agree to.',
        },
        {
          kind: 'question',
          id: 'm3p1-q1',
          question: {
            key: 'm3p1.q1',
            version: 1,
            type: 'single_choice',
            prompt:
              'A participant signed a consent form they did not understand. Legally the form is valid. Is the consent informed?',
            options: [
              {
                value: 'no',
                label: 'No — informed consent requires comprehension, not just a signature.',
                feedback:
                  'Correct. A signature documents consent; it does not create it. If the person cannot state what they agreed to, the ethical requirement is unmet even where the legal one is satisfied.',
              },
              {
                value: 'yes',
                label: 'Yes — they had the opportunity to read it and ask questions.',
                feedback:
                  'Opportunity is not comprehension. Consent documents routinely test at graduate reading level while the median participant reads well below it; "you could have asked" shifts a researcher\'s duty onto the participant.',
              },
              {
                value: 'depends',
                label: 'It depends on whether the study is high risk.',
                feedback:
                  'Risk level changes how much explanation is owed, not whether comprehension is required.',
              },
            ],
            correct: 'no',
            explanation:
              'The practical test: ask the participant to say back, in their own words, what will happen to their data and how to withdraw. If they cannot, the form failed — and it is the form that needs fixing.',
          },
        },
        {
          kind: 'activity',
          id: 'm3p1-representation',
          activity: 'representation-planner',
          heading: 'Audit 2 · Who is missing',
          intro:
            'The current recruitment plan is passive — an email to the patient portal. Set a representation target and choose strategies until you can actually reach it.',
          summary:
            'Learner sets a representation target for an under-served group and selects active recruitment strategies, seeing which combinations close the gap.',
        },
        {
          kind: 'callout',
          id: 'm3p1-rep-note',
          tone: 'warning',
          heading: 'Passive recruitment reproduces existing access',
          body: [
            'An email to a patient portal reaches people who have a portal account, an email address, stable housing, and a reason to trust the institution. Every one of those filters correlates with the disparities you are trying to study.',
            'This is how a dataset ends up 90% one ancestry group without anyone deciding it should be. Nobody excluded anyone; the recruitment method did it silently.',
          ],
        },
        {
          kind: 'activity',
          id: 'm3p1-security',
          activity: 'security-audit',
          heading: 'Audit 3 · Protecting the data',
          intro:
            'Select the protection layers this protocol needs. Each has a real cost — pick what the data sensitivity justifies, not everything.',
          summary:
            'Learner assembles a layered protection plan and sees which residual risks each layer does and does not address.',
        },
        {
          kind: 'prose',
          id: 'm3p1-omop-intro',
          heading: 'Audit 4 · Making it usable by anyone else',
          body: [
            'Your hospital records sex as "M"/"F", the next one as "1"/"2", the third as "male"/"female". Multiply that by every diagnosis, drug, and lab in the record and a multi-site study becomes a year of data wrangling.',
            'A **common data model** fixes this by mapping every local value to a shared concept identifier. It is unglamorous and it is what makes reproducible multi-site research possible at all. Do the mapping yourself below.',
          ],
        },
        {
          kind: 'activity',
          id: 'm3p1-omop',
          activity: 'omop-mapper',
          heading: 'Standardize a patient record',
          intro:
            'One messy source row. Map each field to its standard concept, and notice which fields disappear entirely.',
          summary:
            'Learner maps source values to OMOP concept identifiers and observes which identifiers are dropped during standardization.',
        },
        {
          kind: 'question',
          id: 'm3p1-q2',
          question: {
            key: 'm3p1.q2',
            version: 1,
            type: 'single_choice',
            prompt:
              'During standardization, patient name and full address are dropped while year of birth is kept. Why keep year of birth?',
            options: [
              {
                value: 'age_needed',
                label: 'Age is clinically essential, and year alone is far less identifying than a full date.',
                feedback:
                  'Correct. This is data minimization in action: keep the analytic resolution you need and no more. Full date of birth plus ZIP plus sex is famously re-identifying; year of birth alone is much weaker.',
              },
              {
                value: 'not_pii',
                label: 'Year of birth is not personally identifiable information.',
                feedback:
                  'It is a quasi-identifier — weak alone, potent in combination. It is kept because it is *necessary*, not because it is harmless.',
              },
              {
                value: 'required',
                label: 'The common data model requires it.',
                feedback:
                  'The model has the field because researchers need age. The reasoning runs from the analytic need, not from the schema.',
              },
            ],
            correct: 'age_needed',
            explanation:
              'Every retained field should survive one question: what analysis becomes impossible without it? Name and street address never survive it. Year of birth usually does.',
          },
        },
        {
          kind: 'reveal',
          id: 'm3p1-more',
          label: 'Learn more: returning value to participants',
          body: [
            'Beneficence does not end at publication. Concrete forms of return: plain-language summaries of findings sent to participants; returning clinically actionable individual results where a validated pathway exists; depositing derived data where the contributing community can use it; and co-authorship or acknowledgement for community partners who did real work.',
            'The version that is easiest to skip and matters most: telling participants what came of the study. Non-return is a documented driver of the mistrust that makes the next study harder to recruit for.',
          ],
        },
      ],
    },
    {
      key: 'm3p2',
      slug: 'preparing-data',
      position: 2,
      kind: 'apply',
      title: 'Preparing Data for AI',
      kicker: 'Module 3 · Page 2',
      lede:
        'Label quality sets the ceiling on model performance. Preprocessing choices decide whether you get anywhere near it.',
      objectives: [
        "Interpret percent agreement alongside Cohen's kappa and explain the low-prevalence paradox.",
        'State the assumption behind mean imputation and when it fails in clinical data.',
        'Explain what federated learning does and does not solve.',
      ],
      estimatedMinutes: 25,
      contentVersion: 1,
      requiredSections: ['m3p2-agreement', 'm3p2-q1', 'm3p2-pipeline', 'm3p2-q2', 'm3p2-federated', 'm3p2-q3'],
      sections: [
        {
          kind: 'prose',
          id: 'm3p2-intro',
          heading: 'No model beats its labels',
          body: [
            'Supervised learning learns to reproduce your labels — including their mistakes. If two radiologists agree on only 70% of cases, no model trained on one radiologist\'s reads can be more than about 70% "correct" against the other.',
            'So the first question about any labelled dataset is not which model to use. It is: how much do the labellers agree, and where do they disagree?',
          ],
        },
        {
          kind: 'activity',
          id: 'm3p2-agreement',
          activity: 'label-agreement',
          heading: 'Inter-rater agreement',
          intro:
            'Twelve images read by up to five annotators. Add annotators and watch agreement, the consensus label, and the achievable accuracy ceiling move together.',
          summary:
            'Learner varies annotator count, inspects percent agreement versus Cohen\'s kappa, and reviews the specific cases where readers disagree.',
        },
        {
          kind: 'question',
          id: 'm3p2-q1',
          question: {
            key: 'm3p2.q1',
            version: 1,
            type: 'single_choice',
            prompt:
              'Two readers agree on 92% of cases, but Cohen\'s kappa is only 0.31. What is going on?',
            options: [
              {
                value: 'prevalence',
                label: 'The condition is rare, so most agreement is on the easy negatives and could happen by chance.',
                feedback:
                  'Correct. Kappa corrects for chance agreement. At 5% prevalence, two readers who both say "normal" almost always will hit ~90% agreement while agreeing on almost none of the positives.',
              },
              {
                value: 'error',
                label: 'Kappa was calculated incorrectly.',
                feedback:
                  'This pattern — high raw agreement, low kappa — is the expected and well-documented behavior at low prevalence, not a computational error.',
              },
              {
                value: 'good',
                label: 'Nothing; 92% agreement is good enough to proceed.',
                feedback:
                  'For a rare finding, 92% agreement can mean the readers agree on nearly nothing that matters. Kappa 0.31 is "fair" at best.',
              },
            ],
            correct: 'prevalence',
            explanation:
              'Report both, plus agreement restricted to positive cases. For rare findings, the positive-case agreement is the number that tells you whether your labels support the study.',
          },
        },
        {
          kind: 'prose',
          id: 'm3p2-pipeline-intro',
          heading: 'Then the preparation decisions',
          body: [
            'Three decisions, each with a real effect: what counts as an outlier, what to do about missing values, and whether to rescale. None has a universally right answer, and the effects compound.',
            'Change one setting at a time below and watch the distribution respond. Then ask which change you would be willing to defend in a methods section.',
          ],
        },
        {
          kind: 'activity',
          id: 'm3p2-pipeline',
          activity: 'preprocessing-pipeline',
          heading: 'Preprocessing pipeline',
          intro:
            'A cohort with genuine measurement errors, real physiological extremes, and 10% missing values in one variable.',
          summary:
            'Learner tunes z-score threshold, imputation strategy, and scaling, seeing each step\'s effect on the distribution and on how many rows survive.',
        },
        {
          kind: 'question',
          id: 'm3p2-q2',
          question: {
            key: 'm3p2.q2',
            version: 1,
            type: 'single_choice',
            prompt:
              'Oxygen saturation is missing for 10% of patients. You fill those with the cohort mean. What have you assumed?',
            options: [
              {
                value: 'mcar',
                label: 'That the values are missing for reasons unrelated to how sick the patient is.',
                feedback:
                  'Correct — that is missing-completely-at-random, and it is usually false in clinical data. Sats often go unrecorded because the patient was stable and nobody bothered, which means the missing values are systematically *better* than average, not average.',
              },
              {
                value: 'nothing',
                label: 'Nothing; mean imputation is a neutral default.',
                feedback:
                  'It is a strong assumption disguised as a default. It also shrinks variance and weakens any real association with the outcome.',
              },
              {
                value: 'normal',
                label: 'That the variable is normally distributed.',
                feedback:
                  'Distribution shape affects whether the mean is a sensible center, but the load-bearing assumption is about *why* the data is missing.',
              },
            ],
            correct: 'mcar',
            explanation:
              'Missingness is often informative. Two practical moves: add a "was this measured" indicator variable, and compare your result under mean imputation against multiple imputation or complete-case analysis.',
          },
        },
        {
          kind: 'prose',
          id: 'm3p2-fed-intro',
          heading: 'Collaborating without moving the data',
          body: [
            'Two institutions each have too few cases for a reliable model. Neither can send patient records to the other. **Federated learning** trains locally at each site and shares only model parameters with an aggregator — the rows never leave.',
            'It genuinely solves a governance problem. It also introduces two new ones, which the simulation below will make visible.',
          ],
        },
        {
          kind: 'activity',
          id: 'm3p2-federated',
          activity: 'federated-round',
          heading: 'Run a federated round',
          intro:
            'Two sites with deliberately different populations. Train locally, aggregate, and compare against what a pooled model would have achieved.',
          summary:
            'Learner runs local training and aggregation, seeing that no rows are shared and that site heterogeneity degrades the aggregated model.',
        },
        {
          kind: 'question',
          id: 'm3p2-q3',
          question: {
            key: 'm3p2.q3',
            version: 1,
            type: 'multi_choice',
            prompt:
              'Federated learning shares only model parameters. Which concerns does that leave unresolved? Select all that apply.',
            options: [
              {
                value: 'inversion',
                label: 'Parameters can leak information about individual training records.',
                feedback:
                  'Yes. Model-inversion and membership-inference attacks are demonstrated, which is why differential privacy is often layered on top.',
              },
              {
                value: 'heterogeneity',
                label: 'Sites that preprocess differently produce incompatible parameters.',
                feedback:
                  'Yes, and this is the practical killer. Federated learning requires every site to agree on the pipeline *before* training — harmonization does not disappear, it moves earlier.',
              },
              {
                value: 'bias',
                label: 'A group absent from every participating site stays absent from the model.',
                feedback:
                  'Yes. Federation broadens the sample; it does not fix a shared blind spot.',
              },
              {
                value: 'accuracy',
                label: 'It always produces a less accurate model than pooling would.',
                feedback:
                  'Not always. With similar site distributions, federated averaging can approach pooled performance. With very different sites it degrades — which is what the simulation shows.',
              },
            ],
            correct: ['inversion', 'heterogeneity', 'bias'],
            explanation:
              'Federated learning solves data *transfer*, not data *quality*, *representation*, or *privacy in the absolute*. It is one control among several, not a substitute for governance.',
          },
        },
        {
          kind: 'reveal',
          id: 'm3p2-more',
          label: 'Learn more: the preprocessing record that makes a study reproducible',
          body: [
            'Record, for every variable: the plausible range you enforced and where it came from; how many values fell outside it and what you did with them; the missingness rate and the imputation method; and whether you scaled, with the scaler fitted on training data only.',
            'That last clause is the one most often violated. Fitting a scaler on the full dataset before splitting leaks test-set statistics into training and inflates your reported performance. Fit on train, apply to test — always.',
          ],
        },
      ],
    },
  ],
};
