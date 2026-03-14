"""Public data models used by the client and CLI."""

from __future__ import annotations

from datetime import date, datetime
from typing import Any, Generic, TypeVar

from pydantic import BaseModel, ConfigDict, Field

T = TypeVar("T")


class ModelBase(BaseModel):
    """Shared model config."""

    model_config = ConfigDict(extra="forbid", populate_by_name=True)


class QueryMeta(ModelBase):
    """Execution metadata for a request."""

    query_name: str
    endpoint: str
    executed_at: datetime
    limit: int | None = None
    offset: int | None = None


class ListResult(ModelBase, Generic[T]):
    """Standard list payload for collection endpoints."""

    items: list[T] = Field(default_factory=list)
    returned_count: int = 0
    meta: QueryMeta


class ActRef(ModelBase):
    """Reference to a legal act/work."""

    uri: str
    celex: str | None = None
    title: str | None = None
    date: date | datetime | None = None
    resource_type: str | None = None


class ActDetail(ActRef):
    """Detailed work-level metadata."""

    eli: str | None = None
    in_force: bool | None = None
    eea_relevant: bool | None = None
    created_by_agents: list[str] = Field(default_factory=list)
    responsible_agents: list[str] = Field(default_factory=list)
    addresses_institutions: list[str] = Field(default_factory=list)
    signatory_names: list[str] = Field(default_factory=list)
    date_document: date | datetime | None = None
    date_entry_into_force: list[date | datetime] = Field(default_factory=list)
    date_end_of_validity: date | datetime | None = None


class RelationItem(ActRef):
    """Relation record between two works."""

    direction: str | None = None
    predicate: str | None = None
    relation_type: str | None = None


class ArticleAnnotationItem(RelationItem):
    """Article-annotation relation record."""

    annotation_uri: str | None = None
    annotation_article: str | None = None
    annotation_paragraph: str | None = None
    annotation_subparagraph: str | None = None
    annotation_point: str | None = None
    annotation_comment_on_legal_basis: str | None = None


class DossierItem(RelationItem):
    """Dossier relation record with procedure-level metadata."""

    dossier_uri: str | None = None
    procedure_code: str | None = None
    procedure_type: str | None = None
    status_adopted: bool | None = None
    status_pending: bool | None = None
    status_withdrawn: bool | None = None
    produces_act_uri: str | None = None
    produces_act_celex: str | None = None


class NIMItem(RelationItem):
    """National implementing measure relation record."""

    implemented_by_country: str | None = None
    all_celexes: list[str] = Field(default_factory=list)
    matching_celexes: list[str] = Field(default_factory=list)


class CaseLawItem(ActRef):
    """Case-law specific record."""

    ecli: str | None = None
    court_formation: str | None = None
    advocate_general: str | None = None
    origin_country: str | None = None


class EurovocTag(ModelBase):
    """EuroVoc concept assigned to a work."""

    concept_uri: str
    label: str | None = None


class SubjectMatterTag(ModelBase):
    """Subject-matter code assigned to a work."""

    concept_uri: str
    label: str | None = None


class ExpressionItem(ModelBase):
    """Language expression and available manifestations."""

    expression_uri: str
    language_uri: str | None = None
    title: str | None = None


class DocumentPayload(ModelBase):
    """Downloaded document payload."""

    source_url: str
    content_type: str
    language: str
    content_base64: str


class ErrorPayload(ModelBase):
    """Standard CLI error payload."""

    type: str
    message: str
    details: dict[str, Any] = Field(default_factory=dict)
