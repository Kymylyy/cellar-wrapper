from __future__ import annotations

from datetime import date, datetime

import pytest
from pydantic import ValidationError

from cellar_wrapper.models import ActRef


def test_models_reject_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        ActRef(uri="http://publications.europa.eu/resource/cellar/work", titlee="typo")


def test_models_parse_date_fields_to_typed_values() -> None:
    model = ActRef(
        uri="http://publications.europa.eu/resource/cellar/work",
        date="2025-01-01",
    )
    assert isinstance(model.date, (date, datetime))
