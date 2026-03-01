"""Download methods for full text and legislative summaries."""

from __future__ import annotations

import base64

from cellar_wrapper.client_mixins.protocols import ClientOpsProtocol
from cellar_wrapper.constants import DEFAULT_LANGUAGE, SUMMARY_ACCEPT, TEXT_FORMAT_ACCEPT
from cellar_wrapper.errors import CellarHTTPError, CellarNotFoundError, CellarValidationError
from cellar_wrapper.models import DocumentPayload
from cellar_wrapper.parser import parse_act_refs, parse_bindings
from cellar_wrapper.sparql import build_summary_lookup_query


class DownloadMixin:
    """Methods for binary/text download endpoints."""

    def get_text(
        self: ClientOpsProtocol,
        celex: str,
        *,
        lang: str = DEFAULT_LANGUAGE,
        format: str = "pdf",
    ) -> DocumentPayload:
        normalized_celex = self._normalize_celex(celex)
        normalized_lang = self._normalize_lang(lang)
        format_key = format.strip().lower()
        if format_key not in TEXT_FORMAT_ACCEPT:
            raise CellarValidationError(f"Unsupported format: {format!r}")

        # Keep not-found semantics consistent with the client contract.
        _ = self._resolve_work_uri(normalized_celex)
        try:
            content, content_type, source_url = self._transport.download(
                f"{self._base_url_resource}/celex/{normalized_celex}",
                accept=TEXT_FORMAT_ACCEPT[format_key],
                language=normalized_lang,
            )
        except CellarHTTPError as exc:
            if exc.status_code != 404:
                raise
            raise CellarNotFoundError(
                "No document content found for CELEX: "
                f"{normalized_celex} (lang={normalized_lang}, format={format_key})",
                details={
                    "entity": "document",
                    "celex": normalized_celex,
                    "lang": normalized_lang,
                    "format": format_key,
                },
            ) from exc
        return DocumentPayload(
            source_url=source_url,
            content_type=content_type,
            language=normalized_lang,
            content_base64=base64.b64encode(content).decode("ascii"),
        )

    def get_summary(self: ClientOpsProtocol, celex: str, *, lang: str = DEFAULT_LANGUAGE) -> DocumentPayload:
        normalized_celex = self._normalize_celex(celex)
        normalized_lang = self._normalize_lang(lang)
        summary_query = build_summary_lookup_query(self._resolve_work_uri(normalized_celex))
        rows = parse_bindings(self._transport.query_sparql(summary_query))
        if not rows:
            raise CellarNotFoundError(
                f"No legislative summary found for CELEX: {normalized_celex}",
                details={"entity": "summary", "celex": normalized_celex},
            )

        summary_uri = parse_act_refs(rows)[0].uri
        try:
            content, content_type, source_url = self._transport.download(
                summary_uri,
                accept=SUMMARY_ACCEPT,
                language=normalized_lang,
            )
        except CellarHTTPError as exc:
            if exc.status_code != 404:
                raise
            raise CellarNotFoundError(
                "No legislative summary found for CELEX: "
                f"{normalized_celex} (lang={normalized_lang})",
                details={
                    "entity": "summary",
                    "celex": normalized_celex,
                    "lang": normalized_lang,
                },
            ) from exc
        return DocumentPayload(
            source_url=source_url,
            content_type=content_type,
            language=normalized_lang,
            content_base64=base64.b64encode(content).decode("ascii"),
        )
