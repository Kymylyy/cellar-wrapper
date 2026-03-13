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
- `--since`: Optional lower date/time bound for supported commands. Monitoring commands require it.
- `--to`: Optional upper date/time bound for the same commands that support `--since`.
- `--lang`: Language code (default is `eng`).
- `--limit` / `--offset`: Pagination for list results.
- `--resource-type`: Filter by CELLAR resource type token.
- `--country`: ISO-3 country filter (used by `get-national-decisions`).
- `--format`: File format for `get-text` (`pdf`, `xhtml`, `xml`, `rdf`, `docx`).

## Direction cheat sheet (for relation commands)

- `incoming`: other acts point to or affect the given act.
- `outgoing`: the given act points to or affects other acts.
- `both`: command can return both `incoming` and `outgoing` rows.

## LOOKUP

- `resolve-celex` (`resolve_celex`): Finds canonical CELEX/work reference for the given CELEX value.
  Example: `cellar lookup resolve-celex --celex 32022R2554`
- `get-act` (`get_act`): Returns one detailed act card: CELEX, ELI, title, type, key dates, in-force flag, EEA relevance, responsible institutions, and signatory names.
  Notes: `addresses_institutions` is act-dependent and may legitimately be empty even when other institution-related fields are populated. For proposals, `date_end_of_validity = 9999-12-31` can appear as a placeholder max date rather than a meaningful end-of-validity signal.
  Example: `cellar lookup get-act --celex 32022R2554 --lang eng`
- `get-eurovoc` (`get_eurovoc`): Lists EuroVoc tags linked to an act.
  Example: `cellar lookup get-eurovoc --celex 32022R2554 --limit 50 --offset 0`
- `get-subject-matter` (`get_subject_matter`): Lists subject-matter tags linked to an act.
  Example: `cellar lookup get-subject-matter --celex 32022R2554 --limit 50 --offset 0`
- `get-legal-basis` (`get_legal_basis`): Lists legal-basis-style relations. Results can mix treaty basis entries, level-2 acts based on the act, and other documents based on the act such as recommendations.
  Practical note: This is also the command to use for the reverse lookup delegated act -> base act.
  Example: `cellar lookup get-legal-basis --celex 32022R2554 --limit 50 --offset 0`
- `get-directory-codes` (`get_directory_codes`): Lists directory-code concepts assigned to an act.
  Example: `cellar lookup get-directory-codes --celex 32022R2554 --limit 50 --offset 0`
- `get-expressions` (`get_expressions`): Lists language expressions/versions available for the act.
  Example: `cellar lookup get-expressions --celex 32022R2554 --limit 50 --offset 0`

## RELATIONS

These commands return relation rows with `direction`.
Commands that support `--direction` accept `incoming`, `outgoing`, or `both` (default: `both`).

- `get-amendments` (`get_amendments`): Shows amendment relations. Direction: configurable with `--direction`; default `both`.
  Limitation: For proposal acts, `incoming`/`both` may still return an empty set even when the proposal text indicates future amendments. Treat that as a current CELLAR relation-data limitation, not as proof that no planned amendment exists.
  Example: `cellar relations get-amendments --celex 32022R2554 --direction incoming --since 2024-01-01 --lang eng --limit 50`
- `get-repeals` (`get_repeals`): Shows explicit and implicit repeal relations. Direction: configurable with `--direction`; default `both`.
  Limitation: For proposal acts, `incoming`/`both` may still return an empty set even when the proposal text indicates a future repeal. Treat that as a current CELLAR relation-data limitation, not as proof that no planned repeal exists.
  Example: `cellar relations get-repeals --celex 32022R2554 --direction outgoing --since 2024-01-01 --lang eng --limit 50`
- `get-citations` (`get_citations`): Shows citation relations. Direction: configurable with `--direction`; default `both`.
  Note: Results are not limited to legal acts. Depending on the act, they can also include communications, impact assessments, staff working documents, and similar related documents.
  Example: `cellar relations get-citations --celex 32022R2554 --direction both --since 2024-01-01 --lang eng --limit 50`
- `get-based-on-acts` (`get_based_on_acts`): Shows acts and documents linked by the broad `based_on` relation from the perspective of the base act. This may include delegated acts, implementing acts, drafts, reports, resolutions, and other derived documents. Direction: `incoming`.
  Reverse lookup note: This command does not show the base act for a delegated act. For delegated act -> base act, use `lookup get-legal-basis`.
  Example: `cellar relations get-based-on-acts --celex 32022R2554 --since 2024-01-01 --lang eng --limit 50`
- `get-completing-acts` (`get_completing_acts`): Shows acts linked by the narrower `completes` relation, i.e. acts that CELLAR marks as supplementing/completing the provisions of the given act. In practice these may overlap heavily with delegated acts for some base acts. Direction: `incoming`.
  Example: `cellar relations get-completing-acts --celex 32022R2554 --since 2024-01-01 --lang eng --limit 50`
- Practical difference: `get-based-on-acts` is the broad bucket; `get-completing-acts` is the narrower subset that CELLAR marks as completing the act.
- Live examples:
  DORA: `get-completing-acts` returns `REG_DEL` only, while `get-based-on-acts` also returns `REG_IMPL`, `REG_DEL_DRAFT`, and `OWNINI_RES`.
  PSD2: `get-completing-acts` returns `REG_DEL` only, while `get-based-on-acts` also returns `REPORT`, `RES`, `OWNINI_RES`, and `REG_IMPL`.
- `get-proposals-to-change` (`get_proposals_to_change`): Shows proposal acts that may amend, repeal, recast, or otherwise change the given act. Direction: `incoming`.
  Example: `cellar relations get-proposals-to-change --celex 32024R1689 --since 2024-01-01 --lang eng --limit 50`
- `get-adopted-act` (`get_adopted_act`): Shows adopted acts linked to the given act. Direction: `incoming`.
  Example: `cellar relations get-adopted-act --celex 32022R2554 --since 2024-01-01 --lang eng --limit 50`
- `get-related-works` (`get_related_works`): Shows generic related-work links. Direction: configurable with `--direction`; default `both`.
  Example: `cellar relations get-related-works --celex 32022R2554 --direction incoming --since 2024-01-01 --lang eng --limit 50`
- `get-other-relations` (`get_other_relations`): Shows other legal relations (for example suspend, defer, obsolete, influence). Direction: configurable with `--direction`; default `both`.
  Note: This is a sparse, catch-all bucket. In practice it is often empty for mainstream final acts and can be most useful on proposals.
  Example: `cellar relations get-other-relations --celex 52023PC0367 --direction both --lang eng --limit 50`

## LIFECYCLE

Most relation-style lifecycle commands are `incoming` (items linked to the given act).

- `get-consolidated-versions` (`get_consolidated_versions`): Lists consolidated-text relations for the act and can include related consolidated resources that may carry `celex = null` aliases.
  Example: `cellar lifecycle get-consolidated-versions --celex 32022R2554 --since 2020-01-01 --lang eng --limit 50`
- `get-corrigenda` (`get_corrigenda`): Lists corrigenda for the act.
  Default: results are constrained to `resource_type = CORRIGENDUM`. You can still override `--resource-type` explicitly for advanced inspection.
  Example: `cellar lifecycle get-corrigenda --celex 32022R2554 --since 2020-01-01 --lang eng --limit 50`
- `get-nims` (`get_nims`): Lists unique national implementing acts for the act. One directive can have multiple implementing acts in the same country. Public results are grouped by national-act URI, so raw CELLAR row inflation is hidden.
  Output note: each item exposes a preferred `celex` plus `all_celexes` and `matching_celexes` for grouped omnibus acts.
  Example: `cellar lifecycle get-nims --celex 32015L2366 --since 2020-01-01 --lang eng --limit 50`
- `get-dossier` (`get_dossier`): Returns documents that are members of the act’s dossier, with dossier/procedure metadata copied to each row.
  The input act itself is excluded; this is a dossier document feed, not a normalized legislative timeline.
  Example: `cellar lifecycle get-dossier --celex 32022R2554 --lang eng --limit 50`
- `get-opinions` (`get_opinions`): Lists opinion-like and influence-like rows connected to the act (including EP/EESC opinion resources and related legislative opinions summaries).
  Example: `cellar lifecycle get-opinions --celex 32022R2554 --since 2020-01-01 --lang eng --limit 50`
- `get-deadlines` (`get_deadlines`): Lists legal date facts attached to the act (entry into force, transposition, deadline, etc.).
  These are self-date rows on the queried act, typically `direction = outgoing`.
  Example: `cellar lifecycle get-deadlines --celex 32022R2554 --limit 50`

## CASE LAW

Case-law relation commands (`get-cjeu-judgments`, `get-ag-opinions`, `get-preliminary-questions`) are `incoming`.

- `get-cjeu-judgments` (`get_cjeu_judgments`): Lists CJEU judgments that interpret the act.
  Example: `cellar case-law get-cjeu-judgments --celex 32022R2554 --since 2020-01-01 --lang eng --limit 50`
- `get-ag-opinions` (`get_ag_opinions`): Lists Advocate General opinions linked to the act.
  Example: `cellar case-law get-ag-opinions --celex 32022R2554 --since 2020-01-01 --lang eng --limit 50`
- `get-preliminary-questions` (`get_preliminary_questions`): Lists preliminary questions submitted about the act.
  Example: `cellar case-law get-preliminary-questions --celex 32022R2554 --since 2020-01-01 --lang eng --limit 50`
- `get-national-decisions` (`get_national_decisions`): Lists national decisions that reference the act (optionally filtered by country).
  Example: `cellar case-law get-national-decisions --celex 32022R2554 --country DEU --since 2020-01-01 --lang eng --limit 50`
- `get-article-annotations` (`get_article_annotations`): Lists article-annotation rows for the act. These rows can include annotation qualifiers such as article, paragraph, subparagraph, point, and comment on legal basis when CELLAR provides them.
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

Monitoring commands always require `--since`; `--to` is optional when you want an upper date/time bound.
Relation-based `new-*` commands are `incoming` only.

- `new-citations` (`new_citations`): New citations since the given date/time.
  Example: `cellar monitoring new-citations --celex 32022R2554 --since 2025-01-01 --lang eng --limit 50`
- `new-amendments` (`new_amendments`): New amendments since the given date/time.
  Example: `cellar monitoring new-amendments --celex 32022R2554 --since 2025-01-01 --lang eng --limit 50`
- `new-repeals` (`new_repeals`): New repeals since the given date/time.
  Example: `cellar monitoring new-repeals --celex 32022R2554 --since 2025-01-01 --lang eng --limit 50`
- `new-proposals-to-change` (`new_proposals_to_change`): New proposals that may change the given act since the given date/time.
  Example: `cellar monitoring new-proposals-to-change --celex 32024R1689 --since 2025-01-01 --lang eng --limit 50`
- `new-based-on-acts` (`new_based_on_acts`): New acts/documents linked by the broad `based_on` relation since the given date/time.
  Example: `cellar monitoring new-based-on-acts --celex 32022R2554 --since 2025-01-01 --lang eng --limit 50`
- `new-case-law` (`new_case_law`): New CJEU case-law items since the given date/time.
  Example: `cellar monitoring new-case-law --celex 32022R2554 --since 2025-01-01 --lang eng --limit 50`
- `new-preliminary-questions` (`new_preliminary_questions`): New preliminary questions since the given date/time.
  Example: `cellar monitoring new-preliminary-questions --celex 32022R2554 --since 2025-01-01 --lang eng --limit 50`
- `new-corrigenda` (`new_corrigenda`): New corrigenda since the given date/time.
  Default: results are constrained to `resource_type = CORRIGENDUM`. You can still override `--resource-type` explicitly for advanced inspection.
  Example: `cellar monitoring new-corrigenda --celex 32022R2554 --since 2025-01-01 --lang eng --limit 50`
- `new-consolidated` (`new_consolidated`): New consolidated versions since the given date/time.
  Example: `cellar monitoring new-consolidated --celex 32022R2554 --since 2025-01-01 --lang eng --limit 50`
- `new-nims` (`new_nims`): New unique national implementing acts since the given date/time. One directive can have multiple implementing acts in the same country. Public results are grouped by national-act URI, so raw CELLAR row inflation is hidden.
  Output note: each item exposes a preferred `celex` plus `all_celexes` and `matching_celexes` for grouped omnibus acts.
  Example: `cellar monitoring new-nims --celex 32015L2366 --since 2025-01-01 --lang eng --limit 50`
- `new-by-eurovoc` (`new_by_eurovoc`): New acts since the given date/time filtered by EuroVoc tags.
  Example: `cellar monitoring new-by-eurovoc --tags banking supervision --since 2025-01-01 --lang eng --limit 50`

## DOWNLOAD

- `get-text` (`get_text`): Downloads full text of an act in the selected format.
  Example: `cellar download get-text --celex 32022R2554 --lang eng --format pdf`
- `get-summary` (`get_summary`): Downloads the official act summary in the selected language.
  Example: `cellar download get-summary --celex 32022R2554 --lang eng`

## Notes for readers

- Most commands return lists; use `--limit` and `--offset` for paging.
- For `get-nims` and `new-nims`, paging applies to grouped unique national acts, not raw CELLAR relation rows.
- `get-act` and `resolve-celex` return one main record.
- Relation commands include a `direction` field (`incoming` / `outgoing`).
- `both` means one command can return rows in both directions.
- Article-annotation fields such as `annotation_article` and `annotation_paragraph` belong only to `get-article-annotations`, not to ordinary relation commands.
- CLI wraps successful data as `{"ok": true, "data": ...}`.
- CLI wraps errors as `{"ok": false, "error": {...}}`.
- Full formal behavior still lives in [API_CONTRACT.md](API_CONTRACT.md).
