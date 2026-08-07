"""Shared Pydantic configuration.

``StrictModel`` forbids unknown fields, which is what stops a client from smuggling a ``user_id``
into any write request: the field is not declared, so it is rejected with a 422.
"""

from __future__ import annotations

from typing import Any, TypeAlias

from pydantic import BaseModel, ConfigDict

Json: TypeAlias = dict[str, Any]


class StrictModel(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class MessageResponse(ORMModel):
    detail: str
    code: str = "ok"
