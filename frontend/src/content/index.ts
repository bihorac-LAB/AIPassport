import { module1 } from './module-1';
import { module2 } from './module-2';
import { module3 } from './module-3';
import { module4 } from './module-4';
import { module5 } from './module-5';
import { module6 } from './module-6';
import { module7 } from './module-7';
import type { Module, ModulePage, Question } from './types';

/** Every module has exactly two learner-facing pages. */
export const modules: Module[] = [module1, module2, module3, module4, module5, module6, module7];

export const moduleByKey = new Map(modules.map((module) => [module.key, module]));

export const pageByKey = new Map<string, { module: Module; page: ModulePage }>(
  modules.flatMap((module) => module.pages.map((page) => [page.key, { module, page }] as const)),
);

export const questionByKey = new Map<string, Question>(
  modules.flatMap((module) =>
    module.pages.flatMap((page) =>
      page.sections.flatMap((section) =>
        section.kind === 'question' ? [[section.question.key, section.question] as const] : [],
      ),
    ),
  ),
);

export function findPage(moduleKey: string, pageKey: string): ModulePage | undefined {
  const entry = pageByKey.get(pageKey);
  return entry && entry.module.key === moduleKey ? entry.page : undefined;
}

export function siblingPage(moduleKey: string, pageKey: string): ModulePage | undefined {
  const module = moduleByKey.get(moduleKey);
  return module?.pages.find((page) => page.key !== pageKey);
}

export function nextModule(moduleKey: string): Module | undefined {
  const module = moduleByKey.get(moduleKey);
  if (!module) return undefined;
  return modules.find((candidate) => candidate.position === module.position + 1);
}

export type { Module, ModulePage, Question, Section, Tone } from './types';
export { completableSections, pageQuestions } from './types';
