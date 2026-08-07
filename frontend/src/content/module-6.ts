import type { Module } from './types';

/**
 * Module 6 — Generative AI.
 * New content. The legacy application advertised this module in navigation but shipped no pages
 * for it (docs/legacy-audit.md §2, §6).
 */
export const module6: Module = {
  key: 'module-6',
  position: 6,
  title: 'Generative AI',
  subtitle: 'What language models actually do, and how to use them responsibly',
  summary:
    'Understand next-token prediction well enough to predict when a model will fail, then practise using one for biomedical work without creating a privacy or integrity problem.',
  accent: 'green',
  contentVersion: 1,
  pages: [
    {
      key: 'm6p1',
      slug: 'how-generative-models-work',
      position: 1,
      kind: 'explore',
      title: 'How Generative Models Work',
      kicker: 'Module 6 · Page 1',
      lede:
        'A language model predicts the next token. Every capability and every failure — including hallucination — falls out of that one mechanism.',
      objectives: [
        'Explain next-token prediction and why it produces hallucination structurally.',
        'Relate tokenization to reliability on rare biomedical terms.',
        'Choose a sampling temperature appropriate to the task.',
        'Explain what an embedding is and how semantic similarity is computed.',
      ],
      estimatedMinutes: 22,
      contentVersion: 1,
      requiredSections: ['m6p1-tokens', 'm6p1-q1', 'm6p1-nexttoken', 'm6p1-q2', 'm6p1-embeddings', 'm6p1-q3'],
      sections: [
        {
          kind: 'prose',
          id: 'm6p1-intro',
          heading: 'It does one thing',
          body: [
            'Given a sequence of text, the model produces a probability distribution over what comes next. It samples one token, appends it, and repeats. That is the entire loop.',
            'Summarizing, translating, answering, writing code — these are not separate abilities. They are all the same next-token loop, applied to text arranged so that continuing it produces the thing you wanted.',
            'This is worth sitting with, because it explains the failure mode that matters most: the model is optimizing for **plausible continuation**, never for **truth**. A fabricated citation is not a malfunction. It is the mechanism working exactly as designed on a prompt where plausible and true diverge.',
          ],
        },
        {
          kind: 'activity',
          id: 'm6p1-tokens',
          activity: 'tokenizer',
          heading: 'Tokens, not words',
          intro:
            'Type biomedical text and see how it splits. Try a common word, then a drug name, then a gene symbol.',
          summary:
            'Learner tokenizes text and discovers that rare biomedical terms fragment into many tokens while common words do not.',
        },
        {
          kind: 'question',
          id: 'm6p1-q1',
          question: {
            key: 'm6p1.q1',
            version: 1,
            type: 'single_choice',
            prompt:
              'The word "the" is one token. "Pembrolizumab" splits into several. Why does that matter in practice?',
            options: [
              {
                value: 'rare',
                label: 'Rare terms are assembled from fragments, so the model has seen less evidence about them as units.',
                feedback:
                  'Correct. Tokenization reflects training frequency. Specialist vocabulary — drug names, gene symbols, rare diagnoses — fragments, and fragmented rare terms are exactly where models confuse similar-looking entities.',
              },
              {
                value: 'length',
                label: 'Longer words always use more tokens.',
                feedback:
                  'Only loosely. "Internationalization" is long and common enough to tokenize efficiently; a short rare gene symbol may fragment badly. Frequency matters more than length.',
              },
              {
                value: 'nothing',
                label: 'It only affects billing, not accuracy.',
                feedback:
                  'It affects cost too, but the accuracy implication is the important one: fragmentation is a signal that the model has thin evidence about that term.',
              },
            ],
            correct: 'rare',
            explanation:
              'Practical consequence: be most sceptical of model output about rare entities — unusual drugs, gene variants, uncommon syndromes. That is where confident-sounding errors cluster.',
          },
        },
        {
          kind: 'activity',
          id: 'm6p1-nexttoken',
          activity: 'next-token',
          heading: 'Watch it predict',
          intro:
            'A clinical sentence, mid-generation. See the candidate next tokens with their probabilities, then change the temperature and watch the distribution reshape.',
          summary:
            'Learner inspects the next-token probability distribution and manipulates temperature to see the trade-off between reliability and variety.',
        },
        {
          kind: 'question',
          id: 'm6p1-q2',
          question: {
            key: 'm6p1.q2',
            version: 1,
            type: 'single_choice',
            prompt:
              'You are using a model to extract structured findings from clinical notes. What temperature setting is appropriate?',
            options: [
              {
                value: 'low',
                label: 'Near zero — you want the most probable output every time, and reproducibility.',
                feedback:
                  'Correct. Extraction has one right answer per note. Low temperature also makes runs reproducible, which you need to report a method at all.',
              },
              {
                value: 'high',
                label: 'High — so the model considers more possibilities.',
                feedback:
                  'High temperature increases variety, which for extraction means inconsistency between runs on identical input. Save it for brainstorming.',
              },
              {
                value: 'medium',
                label: 'Around 0.7, the usual default.',
                feedback:
                  'That default suits conversation. For a deterministic extraction task it introduces run-to-run variation you cannot justify in a methods section.',
              },
            ],
            correct: 'low',
            explanation:
              'Match temperature to the task: near zero for extraction, classification, and anything you must reproduce; higher only when variety is the point.',
          },
        },
        {
          kind: 'prose',
          id: 'm6p1-embed-intro',
          heading: 'How meaning becomes arithmetic',
          body: [
            'Before any prediction, each token becomes a vector — a list of numbers positioning it in a high-dimensional space. Terms used in similar contexts land near each other, so "myocardial infarction" sits close to "heart attack" without anyone writing that rule.',
            'This is why semantic search over a literature corpus works when keyword search fails, and it is the mechanism behind retrieval-augmented generation: find the nearest real documents first, then ask the model to answer using only those.',
          ],
        },
        {
          kind: 'activity',
          id: 'm6p1-embeddings',
          activity: 'embedding-space',
          heading: 'Similarity in embedding space',
          intro:
            'Pick a biomedical term and see what sits nearest to it. Then find a pair that is close in the space but should not be treated as interchangeable.',
          summary:
            'Learner explores semantic similarity between biomedical terms and finds cases where proximity is misleading.',
        },
        {
          kind: 'question',
          id: 'm6p1-q3',
          question: {
            key: 'm6p1.q3',
            version: 1,
            type: 'single_choice',
            prompt:
              'A model produces a fluent paragraph citing a study that does not exist. What is the best explanation?',
            options: [
              {
                value: 'plausible',
                label: 'It generated the most plausible continuation; a citation-shaped string is plausible whether or not the paper is real.',
                feedback:
                  'Correct, and this is the whole point. The model has no lookup table of papers to check against. It knows what citations *look like* — author-year-journal patterns — and produces one that fits. Fluency and factuality are separate properties.',
              },
              {
                value: 'lying',
                label: 'The model is being deceptive.',
                feedback:
                  'Deception requires intent and a represented truth to conceal. Neither is present. Framing it morally obscures the real lesson, which is structural.',
              },
              {
                value: 'bad_data',
                label: 'Its training data contained that fake citation.',
                feedback:
                  'Sometimes an error is memorized, but fabricated citations are usually assembled fresh from patterns — which is why the same prompt can invent a different fake paper each time.',
              },
            ],
            correct: 'plausible',
            explanation:
              'The operational rule: any claim of fact from a generative model needs an independent source. Not because the model is untrustworthy in character, but because verification is not part of what it does.',
          },
        },
        {
          kind: 'reveal',
          id: 'm6p1-more',
          label: 'Learn more: reducing hallucination',
          body: [
            '**Retrieval-augmented generation** — retrieve real documents, then require the answer to come from them, with quotes. The single most effective technique for factual work.',
            '**Ask for uncertainty explicitly** — "say you do not know rather than guessing" measurably reduces confident fabrication.',
            '**Ground the task in supplied text** — summarizing a paragraph you provided is far more reliable than recalling a fact from training.',
            '**Verify every identifier** — DOIs, PMIDs, accession numbers, drug doses. These are the highest-risk, easiest-to-check outputs.',
            'What does not work: asking the model whether it is confident. Self-reported confidence from a next-token predictor is itself a generated continuation.',
          ],
        },
      ],
    },
    {
      key: 'm6p2',
      slug: 'using-generative-ai',
      position: 2,
      kind: 'apply',
      title: 'Using Generative AI Responsibly',
      kicker: 'Module 6 · Page 2',
      lede:
        'The skill is not prompting. It is knowing what to delegate, what to verify, and what must never leave your institution.',
      objectives: [
        'Apply a decision rule for whether text may be sent to a general-purpose model.',
        'Write a prompt specific enough to produce a usable result.',
        'Identify which claims in generated text require verification first.',
        'State a personal policy for generative AI use in research.',
      ],
      estimatedMinutes: 24,
      contentVersion: 1,
      requiredSections: ['m6p2-q1', 'm6p2-promptlab', 'm6p2-hallucination', 'm6p2-q2', 'm6p2-scenario'],
      sections: [
        {
          kind: 'prose',
          id: 'm6p2-intro',
          heading: 'A decision rule',
          body: [
            'Before pasting anything into a general-purpose model, answer two questions. **Could this text identify a patient?** If yes, stop — use an institutionally approved deployment or do not use a model at all. **Would a wrong answer here cause harm before someone notices?** If yes, the model can draft but a human must verify every factual claim.',
            'Both answers no, and you have a genuinely good use: restructuring your own text, drafting boilerplate, explaining an unfamiliar method, generating code you will test.',
          ],
        },
        {
          kind: 'question',
          id: 'm6p2-q1',
          question: {
            key: 'm6p2.q1',
            version: 1,
            type: 'multi_choice',
            prompt:
              'Which of these are acceptable uses of a public, general-purpose model in a clinical research setting? Select all that apply.',
            options: [
              {
                value: 'rewrite',
                label: 'Rewriting your own draft abstract to be clearer.',
                feedback: 'Yes. Your text, no patient data, and you verify the result.',
              },
              {
                value: 'note',
                label: 'Summarizing a de-identified discharge summary to test an extraction idea.',
                feedback:
                  'Careful. "De-identified" is a technical claim requiring verification — free-text notes routinely retain identifying detail (rare diagnoses, dates, place names) even after names are stripped. Use approved infrastructure, or a genuinely synthetic note.',
              },
              {
                value: 'explain',
                label: 'Asking it to explain what a propensity score is.',
                feedback:
                  'Yes, with the usual caveat: verify anything you will act on or cite. Explaining a standard concept is a well-supported use.',
              },
              {
                value: 'refs',
                label: 'Asking it for five references supporting your hypothesis.',
                feedback:
                  'No. This is the highest-risk request you can make — the output is citation-shaped and unverified by construction. Use a real database, then read what you cite.',
              },
              {
                value: 'code',
                label: 'Generating analysis code that you then review and test.',
                feedback: 'Yes, provided "review and test" actually happens. Generated code fails silently more often than loudly.',
              },
            ],
            correct: ['rewrite', 'explain', 'code'],
            explanation:
              'The pattern: your own content in, verified content out, no identifiable data, no unverifiable facts. The two rejected options fail on data governance and on fabrication risk respectively.',
          },
        },
        {
          kind: 'aiActivity',
          id: 'm6p2-promptlab',
          promptKey: 'prompt_craft',
          heading: 'Prompt workshop',
          intro:
            'Write a prompt you would actually send for a work task. You will get back what it will likely produce, what is ambiguous in it, and a stronger version — plus a warning if it would put identifiable data into a general-purpose model.',
          inputLabel: 'A prompt you would use for biomedical work',
          placeholder:
            'e.g. Summarize this study for a lay audience.\n\n(Try a deliberately vague one first, then compare it with a specific version.)',
          submitLabel: 'Review my prompt',
        },
        {
          kind: 'activity',
          id: 'm6p2-hallucination',
          activity: 'hallucination-hunt',
          heading: 'Hallucination hunt',
          intro:
            'A fluent, professional-sounding paragraph of model output about a clinical topic. Four claims are wrong. Flag them, then check.',
          summary:
            'Learner identifies fabricated and distorted claims in fluent generated text and learns which claim types carry the most risk.',
        },
        {
          kind: 'question',
          id: 'm6p2-q2',
          question: {
            key: 'm6p2.q2',
            version: 1,
            type: 'single_choice',
            prompt:
              'Which type of claim in generated text deserves verification first?',
            options: [
              {
                value: 'specific',
                label: 'Specific numbers and identifiers — doses, percentages, DOIs, accession numbers.',
                feedback:
                  'Correct. Specificity reads as authority, which is exactly why an invented number is dangerous, and these are the fastest claims to check against a real source.',
              },
              {
                value: 'general',
                label: 'General statements about how a method works.',
                feedback:
                  'Broad conceptual statements are usually well supported by training data and are lower risk. Not zero — but not first.',
              },
              {
                value: 'opinion',
                label: 'Opinions and recommendations.',
                feedback:
                  'These need judgement rather than fact-checking. A fabricated dose can hurt someone; a debatable opinion is visible as an opinion.',
              },
            ],
            correct: 'specific',
            explanation:
              'A useful habit: highlight every number and every identifier in generated text before you read the prose. Those are your verification list.',
          },
        },
        {
          kind: 'question',
          id: 'm6p2-scenario',
          heading: 'Write your own rule',
          question: {
            key: 'm6p2.q3',
            version: 1,
            type: 'free_text',
            prompt:
              'Write the generative-AI policy you would actually follow in your own work: one thing you will use it for, one thing you will never use it for, and the verification step you commit to.',
            placeholder:
              'I will use it for… I will never use it for… Before I act on any output I will…',
            minLength: 100,
            rows: 6,
            explanation:
              'The best versions are specific enough to be checkable. "I will verify outputs" is not a rule. "I will look up every DOI in PubMed before it enters a manuscript, and I will never paste text from our EHR into a non-approved tool" is.',
          },
        },
        {
          kind: 'reveal',
          id: 'm6p2-more',
          label: 'Learn more: disclosure in publication',
          body: [
            'Most journals and funders now require disclosure of generative AI use in manuscript preparation, and the convergent position is clear: an AI system cannot be an author, because authorship requires accountability that software cannot hold.',
            'Standard practice: disclose in the methods or acknowledgements which tool and version you used and for what — language editing, code generation, literature triage. Authors remain fully responsible for every claim, including ones a model drafted.',
            'Check the specific policy of your target venue before submission; they differ in detail and they change.',
          ],
        },
      ],
    },
  ],
};
