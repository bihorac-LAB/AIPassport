"""Seed curriculum tables from the shared content manifest.

Idempotent and non-destructive: modules, pages, and questions are matched by their stable key and
updated in place. A question that disappears from the manifest is marked ``is_active = false`` rather
than deleted, so historical ``question_responses`` stay interpretable.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.logging import get_logger
from app.models import Module, ModulePage, Question
from app.services.content_registry import content_registry

log = get_logger("aipassport.seed")


class SeedReport:
    def __init__(self) -> None:
        self.modules_created = 0
        self.modules_updated = 0
        self.pages_created = 0
        self.pages_updated = 0
        self.questions_created = 0
        self.questions_updated = 0
        self.questions_deactivated = 0

    def __str__(self) -> str:
        return (
            f"modules +{self.modules_created}/~{self.modules_updated}  "
            f"pages +{self.pages_created}/~{self.pages_updated}  "
            f"questions +{self.questions_created}/~{self.questions_updated}"
            f"/-{self.questions_deactivated}"
        )


async def seed_content(db: AsyncSession, *, manifest: dict[str, Any] | None = None) -> SeedReport:
    data = manifest or content_registry.manifest
    modules = data.get("modules", [])
    if not modules:
        raise RuntimeError(
            "Content manifest is empty. Run `npm run export:manifest` in frontend/ first."
        )

    problems = content_registry.validate() if manifest is None else []
    if problems:
        raise RuntimeError("Content manifest is invalid: " + "; ".join(problems))

    report = SeedReport()
    seen_question_keys: set[str] = set()

    for module_data in modules:
        pages_data = module_data.get("pages", [])
        if len(pages_data) != 2:
            raise RuntimeError(
                f"Module {module_data.get('key')} has {len(pages_data)} pages; "
                "exactly two learner-facing pages are required."
            )

        module = (
            await db.execute(select(Module).where(Module.key == module_data["key"]))
        ).scalar_one_or_none()
        if module is None:
            module = Module(key=module_data["key"], position=module_data["position"])
            db.add(module)
            report.modules_created += 1
        else:
            report.modules_updated += 1

        module.position = module_data["position"]
        module.title = module_data["title"]
        module.subtitle = module_data.get("subtitle", "")
        module.summary = module_data.get("summary", "")
        module.accent = module_data.get("accent", "blue")
        module.content_version = module_data.get("contentVersion", 1)
        module.is_published = True
        await db.flush()

        for page_data in pages_data:
            page = (
                await db.execute(select(ModulePage).where(ModulePage.key == page_data["key"]))
            ).scalar_one_or_none()
            if page is None:
                page = ModulePage(key=page_data["key"], module_id=module.id)
                db.add(page)
                report.pages_created += 1
            else:
                report.pages_updated += 1

            page.module_id = module.id
            page.module_key = module.key
            page.position = page_data["position"]
            page.slug = page_data["slug"]
            page.title = page_data["title"]
            page.kicker = page_data.get("kicker", "")
            page.kind = page_data["kind"]
            page.objectives = page_data.get("objectives", [])
            page.required_sections = page_data.get("requiredSections", [])
            page.estimated_minutes = page_data.get("estimatedMinutes", 15)
            page.content_version = page_data.get("contentVersion", 1)
            await db.flush()

            for question_data in page_data.get("questions", []):
                key = question_data["key"]
                seen_question_keys.add(key)
                question = (
                    await db.execute(select(Question).where(Question.key == key))
                ).scalar_one_or_none()
                if question is None:
                    question = Question(key=key, page_id=page.id)
                    db.add(question)
                    report.questions_created += 1
                else:
                    report.questions_updated += 1

                question.page_id = page.id
                question.module_key = module.key
                question.page_key = page.key
                question.position = question_data["position"]
                question.type = question_data["type"]
                question.prompt = question_data["prompt"]
                question.spec = question_data.get("spec", {})
                question.version = question_data.get("version", 1)
                question.is_graded = bool(question_data.get("isGraded", False))
                question.is_active = True
                await db.flush()

    # Retire questions no longer in the manifest instead of deleting their responses.
    stale = (
        (await db.execute(select(Question).where(Question.is_active.is_(True))))
        .scalars()
        .all()
    )
    for question in stale:
        if question.key not in seen_question_keys:
            question.is_active = False
            report.questions_deactivated += 1

    await db.commit()
    log.info("content_seeded", summary=str(report))
    return report
