/**
 * Generates backend/content/manifest.json from the typed frontend content.
 *
 * This is what keeps the database, the API, and the UI from disagreeing about page keys, question
 * keys, or content versions: there is one source of truth (src/content/*.ts) and the backend seeder
 * consumes its export. Run via `npm run export:manifest`; it also runs as part of `npm run build`.
 */

import { mkdirSync, writeFileSync } from 'node:fs';
import { dirname, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';
import { modules } from '../src/content/index';
import { ACTIVITY_GUIDANCE } from '../src/activities/guidance';
import type { Question, Section } from '../src/content/types';

const here = dirname(fileURLToPath(import.meta.url));
const OUT = resolve(here, '../../backend/content/manifest.json');

function questionSpec(question: Question): Record<string, unknown> {
  const spec: Record<string, unknown> = {};
  if (question.options) spec.options = question.options;
  if (question.correct !== undefined) spec.correct = question.correct;
  if (question.tolerance !== undefined) spec.tolerance = question.tolerance;
  if (question.min !== undefined) spec.min = question.min;
  if (question.max !== undefined) spec.max = question.max;
  if (question.step !== undefined) spec.step = question.step;
  if (question.unit !== undefined) spec.unit = question.unit;
  if (question.scaleLabels) spec.scaleLabels = question.scaleLabels;
  if (question.minLength !== undefined) spec.minLength = question.minLength;
  if (question.fields) spec.fields = question.fields;
  if (question.requiredFields) spec.requiredFields = question.requiredFields;
  if (question.explanation) spec.explanation = question.explanation;
  if (question.correctFeedback) spec.correctFeedback = question.correctFeedback;
  if (question.incorrectFeedback) spec.incorrectFeedback = question.incorrectFeedback;
  return spec;
}

/** Sections are exported without prose bodies: the backend needs structure and AI context, not copy. */
function sectionSummary(section: Section): Record<string, unknown> {
  const base = { id: section.id, kind: section.kind };
  switch (section.kind) {
    case 'prose':
      return { ...base, heading: section.heading, summary: section.summary };
    case 'callout':
      return { ...base, heading: section.heading };
    case 'reveal':
      return { ...base, label: section.label };
    case 'question':
      return { ...base, heading: section.heading, questionKey: section.question.key };
    case 'activity':
      return {
        ...base,
        heading: section.heading,
        activity: section.activity,
        summary: section.summary,
      };
    case 'aiActivity':
      return { ...base, heading: section.heading, promptKey: section.promptKey };
    default:
      return base;
  }
}

const manifest = {
  version: 1,
  generatedFrom: 'frontend/src/content',
  activityGuidance: ACTIVITY_GUIDANCE,
  modules: modules.map((module) => ({
    key: module.key,
    position: module.position,
    title: module.title,
    subtitle: module.subtitle,
    summary: module.summary,
    accent: module.accent,
    contentVersion: module.contentVersion,
    pages: module.pages.map((page) => ({
      key: page.key,
      moduleKey: module.key,
      position: page.position,
      slug: page.slug,
      title: page.title,
      kicker: page.kicker,
      kind: page.kind,
      objectives: page.objectives,
      requiredSections: page.requiredSections,
      estimatedMinutes: page.estimatedMinutes,
      contentVersion: page.contentVersion,
      sections: page.sections.map(sectionSummary),
      questions: page.sections.flatMap((section, index) =>
        section.kind === 'question'
          ? [
              {
                key: section.question.key,
                moduleKey: module.key,
                pageKey: page.key,
                position: index + 1,
                type: section.question.type,
                prompt: section.question.prompt,
                spec: questionSpec(section.question),
                version: section.question.version,
                isGraded: section.question.correct !== undefined,
              },
            ]
          : [],
      ),
    })),
  })),
};

// Fail loudly rather than writing a manifest the backend will reject.
const problems: string[] = [];
const seenPages = new Set<string>();
const seenQuestions = new Set<string>();

for (const module of manifest.modules) {
  if (module.pages.length !== 2) {
    problems.push(`${module.key} has ${module.pages.length} pages; exactly 2 are required`);
  }
  module.pages.forEach((page, index) => {
    if (page.position !== index + 1) {
      problems.push(`${page.key} position ${page.position} should be ${index + 1}`);
    }
    if (seenPages.has(page.key)) problems.push(`duplicate page key ${page.key}`);
    seenPages.add(page.key);

    const sectionIds = new Set(page.sections.map((section) => section.id));
    for (const required of page.requiredSections) {
      if (!sectionIds.has(required)) {
        problems.push(`${page.key} requires unknown section "${required}"`);
      }
    }
    for (const question of page.questions) {
      if (seenQuestions.has(question.key)) {
        problems.push(`duplicate question key ${question.key}`);
      }
      seenQuestions.add(question.key);
    }
  });
}

if (problems.length > 0) {
  console.error('Content manifest is invalid:');
  for (const problem of problems) console.error(`  - ${problem}`);
  process.exit(1);
}

mkdirSync(dirname(OUT), { recursive: true });
writeFileSync(OUT, `${JSON.stringify(manifest, null, 2)}\n`, 'utf8');

const pageCount = manifest.modules.reduce((sum, module) => sum + module.pages.length, 0);
const questionCount = manifest.modules.reduce(
  (sum, module) => sum + module.pages.reduce((s, page) => s + page.questions.length, 0),
  0,
);
console.log(
  `Wrote ${OUT}\n  ${manifest.modules.length} modules, ${pageCount} pages, ${questionCount} questions`,
);
