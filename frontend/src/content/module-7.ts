import type { Module } from './types';

/**
 * Module 7 — Impact Project.
 * Consolidates legacy microskills 7.1–7.7, all of which were the same textarea → LLM interaction
 * with a different system instruction (docs/legacy-audit.md §2).
 */
export const module7: Module = {
  key: 'module-7',
  position: 7,
  title: 'Impact Project',
  subtitle: 'Design a study, then communicate and defend it',
  summary:
    'Turn your own research interest into a specified AI study, then practise the three forms of communication it will face: a plain-language pitch, a funder-style summary, and peer review.',
  accent: 'slate',
  contentVersion: 1,
  pages: [
    {
      key: 'm7p1',
      slug: 'design-your-study',
      position: 1,
      kind: 'explore',
      title: 'Design Your Study',
      kicker: 'Module 7 · Page 1',
      lede:
        'A designed study answers six questions before anyone writes code. Specify yours here and get structured feedback on it.',
      objectives: [
        'Specify a study in terms of question, data, comparator, metric, validation, and risk.',
        'Identify a required baseline for an AI study.',
        'Recognize which facts a datasheet or model card requires that you have not yet documented.',
      ],
      estimatedMinutes: 30,
      contentVersion: 1,
      requiredSections: ['m7p1-builder', 'm7p1-review', 'm7p1-opportunity', 'm7p1-datasheet'],
      sections: [
        {
          kind: 'prose',
          id: 'm7p1-intro',
          heading: 'Six answers',
          body: [
            '**The question** — what decision would change if you knew the answer? **The data** — what exists, for whom, and does it contain the outcome? **The comparator** — what is current practice, and what simple baseline must you beat? **The metric** — which number matters, and at what operating point? **The validation** — what makes you believe it generalizes? **The risk** — what is the most likely way this is wrong?',
            'A study missing the comparator or the baseline is the most common reviewable weakness in biomedical AI. "Our model achieves AUC 0.85" invites the question a reviewer will certainly ask: better than what?',
          ],
        },
        {
          kind: 'activity',
          id: 'm7p1-builder',
          activity: 'study-designer',
          heading: 'Specify your study',
          intro:
            'Fill in the six answers for a project you would actually want to do. Your work autosaves, and the AI review below reads what you wrote here.',
          summary:
            'Learner specifies question, data, comparator, metric, validation plan, and primary risk for their own project.',
        },
        {
          kind: 'prose',
          id: 'm7p1-review-intro',
          heading: 'Get it reviewed',
          body: [
            'Describe your idea in prose — more detail gets more useful feedback. You will get back what is clear, what is missing, the data you would need, a reasonable baseline, how you would know it worked, and two risks to plan for.',
            'This is a study aid, not peer review. It will sometimes be wrong or generic; the useful part is usually the "what is missing" section.',
          ],
        },
        {
          kind: 'aiActivity',
          id: 'm7p1-review',
          promptKey: 'design_review',
          heading: 'AI design review',
          inputLabel: 'Describe your biomedical AI study idea',
          placeholder:
            'e.g. I want to predict which post-operative patients will develop delirium, using pre-op cognitive screening plus intra-op vitals from our anaesthesia records…',
          submitLabel: 'Review my design',
        },
        {
          kind: 'aiActivity',
          id: 'm7p1-opportunity',
          promptKey: 'ai_opportunity',
          heading: 'Where could AI help?',
          intro:
            'If you are not sure AI belongs in your work yet, start here instead. Describe a bottleneck — something slow, inconsistent, or impossible at scale — and get a concrete suggestion with an honest note on why it might not work.',
          inputLabel: 'A challenge or bottleneck in your field',
          placeholder:
            'e.g. Grading histology slides for our cohort takes two pathologists three months and they disagree on borderline cases…',
          submitLabel: 'Suggest an approach',
        },
        {
          kind: 'aiActivity',
          id: 'm7p1-datasheet',
          promptKey: 'datasheet',
          heading: 'Datasheet / model card generator',
          intro:
            'Name a dataset, a model, or both. The generated artifact will mark every fact you have not supplied as "needs to be documented" — those gaps are the point of the exercise.',
          inputLabel: 'A dataset or model to document',
          placeholder:
            'e.g. Our institutional cohort of 4,000 post-operative patients, 2018–2023, with a gradient-boosted delirium risk model.',
          submitLabel: 'Generate documentation',
        },
        {
          kind: 'reveal',
          id: 'm7p1-more',
          label: 'Learn more: the baseline you must include',
          body: [
            'Report at least one of these next to your model, always: current clinical practice (including an existing validated score if one exists); a simple logistic regression on a handful of obvious variables; and the trivial rule — always predict the majority class.',
            'If your deep learning model does not beat logistic regression on your tabular data, that is a finding worth reporting honestly, and it is far better discovered by you than by a reviewer.',
          ],
        },
      ],
    },
    {
      key: 'm7p2',
      slug: 'communicate-and-review',
      position: 2,
      kind: 'apply',
      title: 'Communicate and Review',
      kicker: 'Module 7 · Page 2',
      lede:
        'The same study needs three different tellings, and it needs to survive a reviewer who is trying to find the flaw.',
      objectives: [
        'Specify a study in terms of question, data, comparator, metric, validation, and risk.',
        'Identify a required baseline for an AI study.',
        'Recognize which facts a datasheet or model card requires that you have not yet documented.',
      ],
      estimatedMinutes: 30,
      contentVersion: 1,
      requiredSections: ['m7p2-pitch', 'm7p2-proposal', 'm7p2-critique', 'm7p2-misconduct', 'm7p2-q1'],
      sections: [
        {
          kind: 'prose',
          id: 'm7p2-intro',
          heading: 'Three audiences',
          body: [
            'A **colleague in the elevator** needs the point in two sentences with no jargon. A **funder** needs significance, innovation, approach, and impact in the register reviewers expect. A **reviewer** is looking for the reason to reject.',
            'Most researchers practise only the second. The first is what gets you collaborators, and the third is what gets you funded.',
          ],
        },
        {
          kind: 'aiActivity',
          id: 'm7p2-pitch',
          promptKey: 'pitch',
          heading: 'The plain-language version',
          intro:
            'Paste an abstract — yours or one you admire — and get it back in under 100 words with no jargon. Then compare: what did compression force out, and was any of it load-bearing?',
          inputLabel: 'An abstract or description of scientific work',
          placeholder: 'Paste an abstract here…',
          submitLabel: 'Compress it',
        },
        {
          kind: 'aiActivity',
          id: 'm7p2-proposal',
          promptKey: 'proposal',
          heading: 'The funder version',
          intro:
            'Describe your topic and get back an NIH-style project summary. Read it for its *structure* — significance, innovation, approach, impact — rather than adopting its words. Anything it invented is a gap you need to fill yourself.',
          inputLabel: 'Your research topic',
          placeholder:
            'e.g. Using routinely collected anaesthesia data to predict and prevent post-operative delirium in patients over 65…',
          submitLabel: 'Draft a project summary',
        },
        {
          kind: 'aiActivity',
          id: 'm7p2-critique',
          promptKey: 'review_critique',
          heading: 'The reviewer version',
          intro:
            'Submit your own idea and get it critiqued in a reviewer\'s register. Read the "major concerns" section first — those are the objections you will face whether or not you prepare for them.',
          inputLabel: 'Your biomedical AI research idea',
          placeholder: 'Describe the study you want reviewed…',
          submitLabel: 'Critique my idea',
        },
        {
          kind: 'callout',
          id: 'm7p2-integrity-intro',
          tone: 'neutral',
          heading: 'A research integrity case',
          body: [
            'A clinical trial run by a pharmaceutical company with a university reported positive outcomes for a new cancer drug in a high-impact journal.',
            'It later emerged that adverse events had been underreported, that two outcome definitions were changed after data collection was complete, and that a statistician who raised concerns was left off the author list.',
          ],
        },
        {
          kind: 'aiActivity',
          id: 'm7p2-misconduct',
          promptKey: 'misconduct',
          heading: 'Analyze the case',
          intro:
            'Answer both questions in your own words, then submit. You will get an assessment of what you identified, what you missed, and preventive measures worth knowing.',
          inputLabel:
            '1) What specific integrity failures occurred here?  2) What should have prevented each of them?',
          placeholder:
            '1) The failures I can identify are…\n\n2) Each could have been prevented by…',
          submitLabel: 'Submit my analysis',
        },
        {
          kind: 'question',
          id: 'm7p2-q1',
          heading: 'The one you will actually face',
          question: {
            key: 'm7p2.q1',
            version: 1,
            type: 'single_choice',
            prompt:
              'Your analysis is nearly finished. A secondary outcome is significant; the pre-registered primary outcome is not. What do you do?',
            options: [
              {
                value: 'report_both',
                label: 'Report the primary outcome as the primary result, and the secondary as exploratory.',
                feedback:
                  'Correct. This is the only honest option, and it is publishable. A well-powered null result on a pre-registered primary outcome is a real contribution; the secondary finding is a hypothesis for the next study.',
              },
              {
                value: 'switch',
                label: 'Lead with the secondary outcome, since that is where the signal is.',
                feedback:
                  'This is outcome switching — one of the failures in the case above. It inflates the false-positive rate and it is detectable by anyone who reads your registration.',
              },
              {
                value: 'both_equal',
                label: 'Present both as co-primary outcomes.',
                feedback:
                  'Retrospectively promoting an outcome to co-primary is outcome switching with extra steps, and it does not correct for the multiple comparisons involved.',
              },
              {
                value: 'more_data',
                label: 'Collect more data until the primary outcome reaches significance.',
                feedback:
                  'That is optional stopping, and it drives the true false-positive rate far above 5%. If you extend a study, the extension needs to be pre-specified.',
              },
            ],
            correct: 'report_both',
            explanation:
              'Pre-registration exists precisely to make this decision in advance, when it is easy. The pressure you feel here is the pressure it was designed to remove.',
          },
        },
        {
          kind: 'reveal',
          id: 'm7p2-more',
          label: 'Learn more: reporting standards worth knowing',
          body: [
            '**TRIPOD+AI** — prediction model studies. The checklist reviewers increasingly expect for clinical prediction models.',
            '**CONSORT-AI** and **SPIRIT-AI** — trials of AI interventions and their protocols.',
            '**STARD-AI** — diagnostic accuracy studies.',
            '**CLAIM** — medical imaging AI.',
            'Read the relevant checklist *before* you design, not while you write. Most items are design decisions you cannot retrofit.',
          ],
        },
      ],
    },
  ],
};
