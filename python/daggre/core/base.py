"""Minimal model base for daggre's graph domain: a stable id plus name/label.

These are plain pydantic v2 models — a `transports.Session` hosts the `Graph` and observes mutations
to it (and its nested nodes/edges) directly, so the domain carries no sync machinery of its own.
"""

from pydantic import BaseModel as PydanticBaseModel, Field, model_validator
from uuid import uuid4


class BaseModel(PydanticBaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    name: str = ""
    label: str = ""

    @model_validator(mode="after")
    def _name_defaults_to_id(self) -> "BaseModel":
        if not self.name:
            self.name = self.id
        return self
