"""In-memory view of the shared content manifest.

``backend/content/manifest.json`` is generated from the frontend's typed content
(``npm run export:manifest``) so the database, the API, and the UI cannot disagree about page keys,
question keys, or content versions. The registry is also what supplies the AI tutor with page context,
which is why context assembly happens on the server rather than being posted by the client.
"""

from __future__ import annotations

import json
from functools import cached_property
from pathlib import Path
from typing import Any

from app.core.logging import get_logger

log = get_logger("aipassport.content")

MANIFEST_PATH = Path(__file__).resolve().parents[2] / "content" / "manifest.json"


class ContentRegistry:
    def __init__(self, path: Path = MANIFEST_PATH) -> None:
        self.path = path

    @cached_property
    def manifest(self) -> dict[str, Any]:
        if not self.path.exists():
            log.warning("content_manifest_missing", path=str(self.path))
            return {"version": 0, "modules": []}
        try:
            with self.path.open(encoding="utf-8") as fh:
                return json.load(fh)
        except (OSError, json.JSONDecodeError) as exc:
            log.error("content_manifest_unreadable", error=str(exc))
            return {"version": 0, "modules": []}

    @property
    def modules(self) -> list[dict[str, Any]]:
        return list(self.manifest.get("modules", []))

    @cached_property
    def _pages_by_key(self) -> dict[str, dict[str, Any]]:
        pages: dict[str, dict[str, Any]] = {}
        for module in self.modules:
            for page in module.get("pages", []):
                pages[page["key"]] = {**page, "module": module}
        return pages

    @cached_property
    def _modules_by_key(self) -> dict[str, dict[str, Any]]:
        return {m["key"]: m for m in self.modules}

    def module(self, key: str | None) -> dict[str, Any] | None:
        return self._modules_by_key.get(key) if key else None

    def page(self, key: str | None) -> dict[str, Any] | None:
        return self._pages_by_key.get(key) if key else None

    def questions(self, page_key: str) -> list[dict[str, Any]]:
        page = self.page(page_key)
        return list(page.get("questions", [])) if page else []

    def tutor_context(
        self,
        *,
        module_key: str | None,
        page_key: str | None,
        section_id: str | None,
        activity_key: str | None,
        activity_context: dict[str, Any] | None,
    ) -> str:
        """Render a compact, PII-free context block for the tutor."""
        lines: list[str] = ["Platform: AIPassport — interactive biomedical AI course."]

        page = self.page(page_key)
        module = self.module(module_key) or (page.get("module") if page else None)

        if module:
            lines.append(f"Module: {module.get('title')}")
            if module.get("summary"):
                lines.append(f"Module focus: {module['summary']}")
        if page:
            lines.append(f"Page: {page.get('title')} ({page.get('kind')})")
            objectives = page.get("objectives") or []
            if objectives:
                lines.append("Learning objectives:")
                lines.extend(f"  - {o}" for o in objectives[:6])
            if section_id:
                section = next(
                    (s for s in page.get("sections", []) if s.get("id") == section_id), None
                )
                if section:
                    label = section.get("heading") or section.get("label") or section_id
                    lines.append(f"Current section: {label}")
                    if section.get("summary"):
                        lines.append(f"Section purpose: {section['summary']}")
        if activity_key:
            lines.append(f"Current activity: {activity_key}")
            hint = (self.manifest.get("activityGuidance") or {}).get(activity_key)
            if hint:
                lines.append(f"Activity purpose: {hint}")
        if activity_context:
            rendered = ", ".join(f"{k}={v}" for k, v in list(activity_context.items())[:20])
            lines.append(f"Learner's current activity state: {rendered[:1200]}")

        return "\n".join(lines)

    # ── Seeding helpers ─────────────────────────────────────────────────────

    def seed_rows(self) -> list[dict[str, Any]]:
        """Flattened module/page/question rows in the shape the seeder wants."""
        rows: list[dict[str, Any]] = []
        for module in self.modules:
            rows.append({"kind": "module", **{k: v for k, v in module.items() if k != "pages"}})
        return rows

    def validate(self) -> list[str]:
        """Structural checks. Returns a list of problems (empty when valid)."""
        problems: list[str] = []
        modules = self.modules
        if not modules:
            problems.append("manifest contains no modules")
        seen_module_keys: set[str] = set()
        seen_page_keys: set[str] = set()
        seen_question_keys: set[str] = set()
        for module in modules:
            key = module.get("key")
            if not key:
                problems.append("a module is missing 'key'")
                continue
            if key in seen_module_keys:
                problems.append(f"duplicate module key: {key}")
            seen_module_keys.add(key)
            pages = module.get("pages", [])
            if len(pages) != 2:
                problems.append(f"module {key} has {len(pages)} pages; exactly 2 are required")
            for index, page in enumerate(pages, start=1):
                page_key = page.get("key")
                if not page_key:
                    problems.append(f"module {key} page {index} is missing 'key'")
                    continue
                if page_key in seen_page_keys:
                    problems.append(f"duplicate page key: {page_key}")
                seen_page_keys.add(page_key)
                if page.get("position") != index:
                    problems.append(
                        f"page {page_key} has position {page.get('position')}, expected {index}"
                    )
                for question in page.get("questions", []):
                    qkey = question.get("key")
                    if not qkey:
                        problems.append(f"page {page_key} has a question without 'key'")
                        continue
                    if qkey in seen_question_keys:
                        problems.append(f"duplicate question key: {qkey}")
                    seen_question_keys.add(qkey)
        return problems

    def reload(self) -> None:
        self.__dict__.pop("manifest", None)
        self.__dict__.pop("_pages_by_key", None)
        self.__dict__.pop("_modules_by_key", None)


content_registry = ContentRegistry()
