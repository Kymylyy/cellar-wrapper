from __future__ import annotations

from datetime import date, datetime

import pytest
from pydantic import ValidationError

from cellar_wrapper.models import (
    ActDetail,
    ActRef,
    ArticleAnnotationItem,
    CaseLawItem,
    DossierItem,
    NIMItem,
    RelationItem,
)


def test_models_reject_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        ActRef.model_validate(
            {
                "uri": "http://publications.europa.eu/resource/cellar/work",
                "titlee": "typo",
            }
        )


def test_models_parse_date_fields_to_typed_values() -> None:
    model = ActRef.model_validate(
        {
            "uri": "http://publications.europa.eu/resource/cellar/work",
            "date": "2025-01-01",
        }
    )
    assert isinstance(model.date, (date, datetime))


def test_extended_models_accept_new_metadata_fields() -> None:
    detail = ActDetail(
        uri="http://publications.europa.eu/resource/cellar/work",
        created_by_agents=["http://publications.europa.eu/resource/authority/corporate-body/COM"],
        responsible_agents=["http://publications.europa.eu/resource/authority/corporate-body/FISMA"],
        addresses_institutions=["http://publications.europa.eu/resource/authority/corporate-body/EUMS"],
        signatory_names=["M. Schulz"],
        eea_relevant=True,
    )
    assert detail.eea_relevant is True
    assert detail.created_by_agents

    case_item = CaseLawItem(
        uri="http://publications.europa.eu/resource/cellar/case",
        origin_country="http://publications.europa.eu/resource/authority/country/DEU",
    )
    assert case_item.origin_country is not None

    dossier_item = DossierItem(
        uri="http://publications.europa.eu/resource/cellar/dossier-item",
        status_pending=True,
        procedure_code="2023/0210/COD",
    )
    assert dossier_item.status_pending is True

    nim_item = NIMItem(
        uri="http://publications.europa.eu/resource/cellar/nim-item",
        implemented_by_country="http://publications.europa.eu/resource/authority/country/POL",
    )
    assert nim_item.implemented_by_country is not None


def test_relation_item_rejects_annotation_fields() -> None:
    with pytest.raises(ValidationError):
        RelationItem.model_validate(
            {
                "uri": "http://publications.europa.eu/resource/cellar/work",
                "annotation_uri": "http://publications.europa.eu/resource/cellar/annotation",
            }
        )


def test_article_annotation_item_accepts_annotation_fields() -> None:
    item = ArticleAnnotationItem.model_validate(
        {
            "uri": "http://publications.europa.eu/resource/cellar/work",
            "annotation_uri": "http://publications.europa.eu/resource/cellar/annotation",
            "annotation_article": "5",
        }
    )
    assert item.annotation_uri is not None
    assert item.annotation_article == "5"
