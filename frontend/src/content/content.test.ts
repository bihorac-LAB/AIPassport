import { describe, expect, it } from 'vitest';
import { ACTIVITIES } from '@/activities/registry';
import { ACTIVITY_GUIDANCE } from '@/activities/guidance';
import { modules, pageByKey, questionByKey } from './index';

describe('course content', () => {
  it('has seven modules with exactly two learner-facing pages each', () => {
    expect(modules).toHaveLength(7);
    for (const module of modules) {
      expect(module.pages).toHaveLength(2);
      expect(module.pages.map((page) => page.position)).toEqual([1, 2]);
    }
  });

  it('numbers modules 1 through 7 without gaps', () => {
    expect(modules.map((module) => module.position)).toEqual([1, 2, 3, 4, 5, 6, 7]);
  });

  it('uses unique, stable keys for every page and question', () => {
    const pageKeys = modules.flatMap((module) => module.pages.map((page) => page.key));
    expect(new Set(pageKeys).size).toBe(pageKeys.length);
    expect(pageByKey.size).toBe(pageKeys.length);

    const questionKeys = [...questionByKey.keys()];
    expect(new Set(questionKeys).size).toBe(questionKeys.length);
    expect(questionKeys.length).toBeGreaterThan(20);
  });

  it('gives every question a version so stored responses stay interpretable', () => {
    for (const [key, question] of questionByKey) {
      expect(question.version, key).toBeGreaterThanOrEqual(1);
      expect(question.prompt.length, key).toBeGreaterThan(10);
    }
  });

  it('gives every graded choice question a correct answer that is one of its options', () => {
    for (const [key, question] of questionByKey) {
      if (question.type === 'single_choice' && question.correct !== undefined) {
        const values = (question.options ?? []).map((option) => option.value);
        expect(values, key).toContain(question.correct);
      }
      if (question.type === 'multi_choice' && Array.isArray(question.correct)) {
        const values = (question.options ?? []).map((option) => option.value);
        for (const answer of question.correct) expect(values, key).toContain(answer);
      }
    }
  });

  it('gives every option on a graded question its own feedback', () => {
    for (const [key, question] of questionByKey) {
      if (question.correct === undefined) continue;
      for (const option of question.options ?? []) {
        expect(option.feedback, `${key}/${option.value}`).toBeTruthy();
      }
    }
  });

  it('only lists required sections that actually exist on the page', () => {
    for (const { page } of pageByKey.values()) {
      const ids = new Set(page.sections.map((section) => section.id));
      for (const required of page.requiredSections) {
        expect(ids, `${page.key} requires ${required}`).toContain(required);
      }
      expect(page.requiredSections.length).toBeGreaterThan(0);
    }
  });

  it('registers a component for every activity referenced by content', () => {
    for (const { page } of pageByKey.values()) {
      for (const section of page.sections) {
        if (section.kind === 'activity') {
          expect(ACTIVITIES, `${page.key}/${section.activity}`).toHaveProperty(section.activity);
          expect(ACTIVITY_GUIDANCE, section.activity).toHaveProperty(section.activity);
        }
      }
    }
  });

  it('states objectives and a realistic time estimate on every page', () => {
    for (const { page } of pageByKey.values()) {
      expect(page.objectives.length, page.key).toBeGreaterThanOrEqual(3);
      expect(page.estimatedMinutes, page.key).toBeGreaterThan(5);
      expect(page.estimatedMinutes, page.key).toBeLessThanOrEqual(40);
      expect(page.lede.length, page.key).toBeGreaterThan(30);
    }
  });

  it('keeps every page interactive rather than a wall of text', () => {
    for (const { page } of pageByKey.values()) {
      const interactive = page.sections.filter(
        (section) =>
          section.kind === 'activity' ||
          section.kind === 'question' ||
          section.kind === 'aiActivity',
      );
      expect(interactive.length, page.key).toBeGreaterThanOrEqual(3);
    }
  });
});
