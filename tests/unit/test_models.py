from __future__ import annotations

import pytest
from pydantic import ValidationError

from cellar_wrapper.models import ActRef


def test_models_reject_unknown_fields() -> None:
    with pytest.raises(ValidationError):
        ActRef(uri="http://publications.europa.eu/resource/cellar/work", titlee="typo")
