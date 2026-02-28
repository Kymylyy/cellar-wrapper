"""Public CELLAR client composed from focused mixins."""

from __future__ import annotations

from cellar_wrapper.client_mixins.base import ClientBase
from cellar_wrapper.client_mixins.case_law import CaseLawMixin
from cellar_wrapper.client_mixins.download import DownloadMixin
from cellar_wrapper.client_mixins.lifecycle import LifecycleMixin
from cellar_wrapper.client_mixins.lookup import LookupMixin
from cellar_wrapper.client_mixins.monitoring import MonitoringMixin
from cellar_wrapper.client_mixins.relations import RelationsMixin
from cellar_wrapper.client_mixins.search import SearchMixin


class CellarClient(
    DownloadMixin,
    MonitoringMixin,
    SearchMixin,
    CaseLawMixin,
    LifecycleMixin,
    RelationsMixin,
    LookupMixin,
    ClientBase,
):
    """Sync-first API client for CELLAR.

    A single instance is not meant to be shared across threads.
    Use one ``CellarClient`` per thread.
    """

    pass
