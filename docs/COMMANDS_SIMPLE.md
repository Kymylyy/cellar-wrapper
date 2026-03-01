# Commands in Plain Language

This file explains each public `cellar` command in simple words.

If you use MCP instead of CLI: MCP tool names are the same as command names below (for example `get-act`, `new-citations`).

## Quick command pattern

```bash
cellar <group> <command> [options]
```

Example:

```bash
cellar lookup get-act --celex 32022R2554 --lang eng
```

## Most common options

- `--celex`: Act ID in EU format (for example `32022R2554`).
- `--since`: Return only newer items (date or date-time).
- `--lang`: Language code (default is `eng`).
- `--limit` / `--offset`: Pagination for list results.
- `--resource-type`: Filter by CELLAR resource type token.
- `--country`: ISO-3 country filter (used by `get-national-decisions`).
- `--format`: File format for `get-text` (`pdf`, `xhtml`, `xml`, `rdf`, `docx`).

## LOOKUP

- `resolve-celex` (`resolve_celex`): Finds canonical CELEX/work reference for the given CELEX value.
  Example: `cellar lookup resolve-celex --celex 32022R2554`
- `get-act` (`get_act`): Returns one detailed act card: CELEX, ELI, title, type, key dates, in-force flag, EEA relevance, responsible institutions, and signatory names.
  Example: `cellar lookup get-act --celex 32022R2554 --lang eng`
- `get-eurovoc` (`get_eurovoc`): Lists EuroVoc tags linked to an act.
  Example: `cellar lookup get-eurovoc --celex 32022R2554 --limit 50 --offset 0`
- `get-subject-matter` (`get_subject_matter`): Lists subject-matter tags linked to an act.
  Example: `cellar lookup get-subject-matter --celex 32022R2554 --limit 50 --offset 0`
- `get-legal-basis` (`get_legal_basis`): Lists legal basis relations (acts/treaty concepts this act is based on).
  Example: `cellar lookup get-legal-basis --celex 32022R2554 --limit 50 --offset 0`
- `get-directory-codes` (`get_directory_codes`): Lists directory-code concepts assigned to an act.
  Example: `cellar lookup get-directory-codes --celex 32022R2554 --limit 50 --offset 0`
- `get-expressions` (`get_expressions`): Lists language expressions/versions available for the act.
  Example: `cellar lookup get-expressions --celex 32022R2554 --limit 50 --offset 0`

## RELATIONS

- `get-amendments` (`get_amendments`): Shows acts that amend the given act.
  Example: `cellar relations get-amendments --celex 32022R2554 --since 2024-01-01 --lang eng --limit 50`
- `get-repeals` (`get_repeals`): Shows acts that repeal (explicitly or implicitly) the given act.
  Example: `cellar relations get-repeals --celex 32022R2554 --since 2024-01-01 --lang eng --limit 50`
- `get-citations` (`get_citations`): Shows works that cite the given act.
  Example: `cellar relations get-citations --celex 32022R2554 --since 2024-01-01 --lang eng --limit 50`
- `get-delegated-acts` (`get_delegated_acts`): Shows delegated acts based on the given act.
  Example: `cellar relations get-delegated-acts --celex 32022R2554 --since 2024-01-01 --lang eng --limit 50`
- `get-completing-acts` (`get_completing_acts`): Shows acts that complete the given act.
  Example: `cellar relations get-completing-acts --celex 32022R2554 --since 2024-01-01 --lang eng --limit 50`
- `get-proposals-to-amend` (`get_proposals_to_amend`): Shows proposals to amend the given act.
  Example: `cellar relations get-proposals-to-amend --celex 32022R2554 --since 2024-01-01 --lang eng --limit 50`
- `get-adopted-act` (`get_adopted_act`): Shows adopted acts linked to the given act.
  Example: `cellar relations get-adopted-act --celex 32022R2554 --since 2024-01-01 --lang eng --limit 50`
- `get-related-works` (`get_related_works`): Shows generic related-work links.
  Example: `cellar relations get-related-works --celex 32022R2554 --since 2024-01-01 --lang eng --limit 50`
- `get-other-relations` (`get_other_relations`): Shows other legal relations (for example suspend, defer, obsolete, influence).
  Example: `cellar relations get-other-relations --celex 32022R2554 --since 2024-01-01 --lang eng --limit 50`

## LIFECYCLE

- `get-consolidated-versions` (`get_consolidated_versions`): Lists consolidated versions related to the act.
  Example: `cellar lifecycle get-consolidated-versions --celex 32022R2554 --since 2020-01-01 --lang eng --limit 50`
- `get-corrigenda` (`get_corrigenda`): Lists corrigenda for the act.
  Example: `cellar lifecycle get-corrigenda --celex 32022R2554 --since 2020-01-01 --lang eng --limit 50`
- `get-nims` (`get_nims`): Lists national implementing measures linked to the act.
  Example: `cellar lifecycle get-nims --celex 32022R2554 --since 2020-01-01 --lang eng --limit 50`
- `get-dossier` (`get_dossier`): Returns dossier items and procedure metadata linked to the act.
  Example: `cellar lifecycle get-dossier --celex 32022R2554 --lang eng --limit 50`
- `get-opinions` (`get_opinions`): Lists opinions connected to the act.
  Example: `cellar lifecycle get-opinions --celex 32022R2554 --since 2020-01-01 --lang eng --limit 50`
- `get-deadlines` (`get_deadlines`): Lists legal dates/deadlines linked to the act.
  Example: `cellar lifecycle get-deadlines --celex 32022R2554 --limit 50`

## CASE LAW

- `get-cjeu-judgments` (`get_cjeu_judgments`): Lists CJEU judgments that interpret the act.
  Example: `cellar case-law get-cjeu-judgments --celex 32022R2554 --since 2020-01-01 --lang eng --limit 50`
- `get-ag-opinions` (`get_ag_opinions`): Lists Advocate General opinions linked to the act.
  Example: `cellar case-law get-ag-opinions --celex 32022R2554 --since 2020-01-01 --lang eng --limit 50`
- `get-preliminary-questions` (`get_preliminary_questions`): Lists preliminary questions submitted about the act.
  Example: `cellar case-law get-preliminary-questions --celex 32022R2554 --since 2020-01-01 --lang eng --limit 50`
- `get-national-decisions` (`get_national_decisions`): Lists national decisions that reference the act (optionally filtered by country).
  Example: `cellar case-law get-national-decisions --celex 32022R2554 --country DEU --since 2020-01-01 --lang eng --limit 50`
- `get-article-annotations` (`get_article_annotations`): Lists article-level legal-basis annotations for the act.
  Example: `cellar case-law get-article-annotations --celex 32022R2554 --limit 50`

## SEARCH

- `search-by-eurovoc` (`search_by_eurovoc`): Finds acts by EuroVoc tags.
  Example: `cellar search search-by-eurovoc --tags banking supervision --since 2024-01-01 --lang eng --limit 50`
- `search-by-subject-matter` (`search_by_subject_matter`): Finds acts by subject-matter codes/labels.
  Example: `cellar search search-by-subject-matter --codes financial services --since 2024-01-01 --lang eng --limit 50`
- `search-by-title` (`search_by_title`): Finds acts by title keyword.
  Example: `cellar search search-by-title --keyword resilience --since 2024-01-01 --lang eng --limit 50`
- `search-communications` (`search_communications`): Finds communication documents by DG code.
  Example: `cellar search search-communications --dg FISMA --since 2024-01-01 --lang eng --limit 50`
- `find-eurovoc-concept` (`find_eurovoc_concept`): Finds EuroVoc concepts by label (from the local packaged index).
  Example: `cellar search find-eurovoc-concept --label banking --limit 20 --offset 0`

## MONITORING

Monitoring commands always require `--since` and return only newer items.

- `new-citations` (`new_citations`): New citations since the given date/time.
  Example: `cellar monitoring new-citations --celex 32022R2554 --since 2025-01-01 --lang eng --limit 50`
- `new-amendments` (`new_amendments`): New amendments since the given date/time.
  Example: `cellar monitoring new-amendments --celex 32022R2554 --since 2025-01-01 --lang eng --limit 50`
- `new-repeals` (`new_repeals`): New repeals since the given date/time.
  Example: `cellar monitoring new-repeals --celex 32022R2554 --since 2025-01-01 --lang eng --limit 50`
- `new-proposals-to-amend` (`new_proposals_to_amend`): New proposals to amend since the given date/time.
  Example: `cellar monitoring new-proposals-to-amend --celex 32022R2554 --since 2025-01-01 --lang eng --limit 50`
- `new-delegated-acts` (`new_delegated_acts`): New delegated acts since the given date/time.
  Example: `cellar monitoring new-delegated-acts --celex 32022R2554 --since 2025-01-01 --lang eng --limit 50`
- `new-case-law` (`new_case_law`): New CJEU case-law items since the given date/time.
  Example: `cellar monitoring new-case-law --celex 32022R2554 --since 2025-01-01 --lang eng --limit 50`
- `new-preliminary-questions` (`new_preliminary_questions`): New preliminary questions since the given date/time.
  Example: `cellar monitoring new-preliminary-questions --celex 32022R2554 --since 2025-01-01 --lang eng --limit 50`
- `new-corrigenda` (`new_corrigenda`): New corrigenda since the given date/time.
  Example: `cellar monitoring new-corrigenda --celex 32022R2554 --since 2025-01-01 --lang eng --limit 50`
- `new-consolidated` (`new_consolidated`): New consolidated versions since the given date/time.
  Example: `cellar monitoring new-consolidated --celex 32022R2554 --since 2025-01-01 --lang eng --limit 50`
- `new-nims` (`new_nims`): New national implementing measures since the given date/time.
  Example: `cellar monitoring new-nims --celex 32022R2554 --since 2025-01-01 --lang eng --limit 50`
- `new-by-eurovoc` (`new_by_eurovoc`): New acts since the given date/time filtered by EuroVoc tags.
  Example: `cellar monitoring new-by-eurovoc --tags banking supervision --since 2025-01-01 --lang eng --limit 50`

## DOWNLOAD

- `get-text` (`get_text`): Downloads full text of an act in the selected format.
  Example: `cellar download get-text --celex 32022R2554 --lang eng --format pdf`
- `get-summary` (`get_summary`): Downloads the official act summary in the selected language.
  Example: `cellar download get-summary --celex 32022R2554 --lang eng`

## Notes for readers

- Most commands return lists; use `--limit` and `--offset` for paging.
- `get-act` and `resolve-celex` return one main record.
- CLI wraps successful data as `{"ok": true, "data": ...}`.
- CLI wraps errors as `{"ok": false, "error": {...}}`.
- Full formal behavior still lives in [API_CONTRACT.md](API_CONTRACT.md).
