"""Download methods for full text and legislative summaries."""

from __future__ import annotations

import base64

from cellar_wrapper.client_mixins.protocols import ClientOpsProtocol
from cellar_wrapper.constants import DEFAULT_LANGUAGE, SUMMARY_ACCEPT, TEXT_FORMAT_ACCEPT
from cellar_wrapper.errors import (
    CellarHTTPError,
    CellarNotFoundError,
    CellarParseError,
    CellarValidationError,
)
from cellar_wrapper.models import DocumentPayload
from cellar_wrapper.parser import parse_uri_act_refs
from cellar_wrapper.sparql import build_summary_lookup_query

_FALLBACKABLE_DOWNLOAD_STATUS_CODES = frozenset({404, 406})
_EURLEX_LANGUAGE_CODES: dict[str, str] = {
    "bul": "BG",
    "ces": "CS",
    "dan": "DA",
    "deu": "DE",
    "ell": "EL",
    "eng": "EN",
    "est": "ET",
    "fin": "FI",
    "fra": "FR",
    "gle": "GA",
    "hrv": "HR",
    "hun": "HU",
    "ita": "IT",
    "lav": "LV",
    "lit": "LT",
    "mlt": "MT",
    "nld": "NL",
    "pol": "PL",
    "por": "PT",
    "ron": "RO",
    "slk": "SK",
    "slv": "SL",
    "spa": "ES",
    "swe": "SV",
}


class DownloadMixin:
    """Methods for binary/text download endpoints."""

    @staticmethod
    def _eurlex_pdf_fallback_url(*, celex: str, lang: str, format_key: str) -> str | None:
        if format_key != "pdf":
            return None
        eurlex_lang = _EURLEX_LANGUAGE_CODES.get(lang.lower())
        if eurlex_lang is None:
            return None
        return f"https://eur-lex.europa.eu/legal-content/{eurlex_lang}/TXT/PDF/?uri=CELEX:{celex}"

    @staticmethod
    def _fallback_not_found(
        *,
        celex: str,
        lang: str,
        format_key: str,
        phase: str,
        original_error: Exception | None = None,
    ) -> CellarNotFoundError:
        details: dict[str, object] = {
            "entity": "document",
            "celex": celex,
            "lang": lang,
            "format": format_key,
            "phase": phase,
        }
        if isinstance(original_error, CellarHTTPError):
            details["original_status_code"] = original_error.status_code
        if original_error is not None:
            details["original_error_type"] = type(original_error).__name__
        return CellarNotFoundError(
            "No document content found for CELEX: "
            f"{celex} (lang={lang}, format={format_key})",
            details=details,
        )

    @staticmethod
    def _should_try_text_fallback(exc: Exception) -> bool:
        if isinstance(exc, CellarHTTPError):
            return exc.status_code in _FALLBACKABLE_DOWNLOAD_STATUS_CODES
        if isinstance(exc, CellarParseError):
            return True
        return False

    def _download_text_payload(
        self: ClientOpsProtocol,
        *,
        celex: str,
        lang: str,
        format_key: str,
    ) -> tuple[bytes, str, str]:
        try:
            return self._transport.download(
                f"{self._base_url_resource}/celex/{celex}",
                accept=TEXT_FORMAT_ACCEPT[format_key],
                language=lang,
            )
        except (CellarHTTPError, CellarParseError) as exc:
            if not self._should_try_text_fallback(exc):
                raise
            original_error: Exception = exc

        fallback_url = self._eurlex_pdf_fallback_url(celex=celex, lang=lang, format_key=format_key)
        if fallback_url is None:
            raise self._fallback_not_found(
                celex=celex,
                lang=lang,
                format_key=format_key,
                phase="fallback_unavailable",
                original_error=original_error,
            )

        try:
            return self._transport.download(
                fallback_url,
                accept=TEXT_FORMAT_ACCEPT[format_key],
            )
        except CellarHTTPError as exc:
            if exc.status_code != 404:
                raise
            raise self._fallback_not_found(
                celex=celex,
                lang=lang,
                format_key=format_key,
                phase="fallback_eurlex_pdf_download",
                original_error=exc,
            ) from exc

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
        content, content_type, source_url = self._download_text_payload(
            celex=normalized_celex,
            lang=normalized_lang,
            format_key=format_key,
        )
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
        rows = self._query_rows(summary_query)
        if not rows:
            raise CellarNotFoundError(
                f"No legislative summary found for CELEX: {normalized_celex}",
                details={"entity": "summary", "celex": normalized_celex},
            )

        summary_uri = parse_uri_act_refs(rows)[0].uri
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
