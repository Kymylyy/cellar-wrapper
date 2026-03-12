# METHOD_MAPPING

Method-to-CDM/SPARQL mapping used by `CellarClient`.

## LOOKUP
- `resolve_celex` -> `cdm:resource_legal_id_celex` (exact then `CONTAINS` fallback)
- `get_act` -> work-level fields (`resource_legal_id_celex`, `resource_legal_eli`, `work_has_resource-type`, `resource_legal_in-force`, `resource_legal_eea`, dates) + institution metadata (`work_created_by_agent`, `resource_legal_responsibility_of_agent`, `resource_legal_addresses_institution`, `resource_legal_signatory_name2`)
- `get_eurovoc` -> `cdm:work_is_about_concept_eurovoc`
- `get_subject_matter` -> `cdm:resource_legal_is_about_subject-matter`
- `get_legal_basis` -> `cdm:resource_legal_based_on_resource_legal`, `cdm:resource_legal_based_on_concept_treaty`
- `get_directory_codes` -> `cdm:resource_legal_is_about_concept_directory-code`
- `get_expressions` -> `cdm:expression_belongs_to_work`, `cdm:expression_uses_language`, `cdm:expression_title`

## RELATIONS
- `get_amendments` -> `cdm:resource_legal_amends_resource_legal`
- `get_repeals` -> `cdm:resource_legal_repeals_resource_legal`, `cdm:resource_legal_implicitly_repeals_resource_legal`
- `get_citations` -> `cdm:work_cites_work`
- `get_delegated_acts` -> `cdm:resource_legal_based_on_resource_legal` (incoming)
- `get_completing_acts` -> `cdm:resource_legal_completes_resource_legal` (incoming)
- `get_proposals_to_amend` -> `cdm:resource_legal_proposes_to_amend_resource_legal` (incoming)
- `get_adopted_act` -> `cdm:resource_legal_adopts_resource_legal` (incoming)
- `get_related_works` -> `cdm:work_related_to_work`
- `get_other_relations` ->
  - `cdm:resource_legal_suspends_resource_legal`
  - `cdm:resource_legal_partially_suspends_resource_legal`
  - `cdm:resource_legal_defers_application_of_resource_legal`
  - `cdm:resource_legal_renders_obsolete_resource_legal`
  - `cdm:resource_legal_influences_resource_legal`

## LIFECYCLE
- `get_consolidated_versions` -> `cdm:act_consolidated_consolidates_resource_legal` (incoming)
- `get_corrigenda` -> `cdm:resource_legal_corrects_resource_legal` (incoming)
- `get_nims` -> `cdm:measure_national_implementing_implements_resource_legal` (incoming) + `cdm:measure_national_implementing_implemented_by_country`
- `get_dossier` -> 2-stage SPARQL execution:
  - stage 1 (core relation selection): `cdm:dossier_contains_work` (early paginated selection of dossier member works)
  - stage 2 (metadata enrichment): dossier procedure/status predicates (`cdm:procedure_code_interinstitutional_reference_procedure`, `cdm:procedure_code_interinstitutional_has_type`, `cdm:dossier_*`, `cdm:dossier_produces_resource_legal`) + optional work metadata (`cdm:resource_legal_id_celex`, `cdm:work_date_document`, `cdm:work_has_resource-type`, `cdm:expression_*`)
  - ordering: deterministic by `date` with resource-key tie-break (`other` URI)
- `get_opinions` ->
  - `cdm:resource_legal_contains_eesc_opinion_on_resource_legal`
  - `cdm:resource_legal_contains_ep_opinion_on_resource_legal`
  - `cdm:resource_legal_influences_resource_legal`
- `get_deadlines` ->
  - `cdm:resource_legal_date_deadline`
  - `cdm:resource_legal_date_entry-into-force`
  - `cdm:directive_date_transposition`

## CASE LAW
- `get_cjeu_judgments` -> `cdm:case-law_interpretes_resource_legal`
- `get_ag_opinions` ->
  - `cdm:case-law_interpretes_resource_legal`
  - `cdm:case-law_has_conclusions_opinion_advocate-general`
- `get_preliminary_questions` -> `cdm:communication_case_new_submits_preliminary_question_resource_legal`
- `get_national_decisions` ->
  - `cdm:work_has_resource-type` = `DEC_NC`
  - `cdm:case-law_national_act_reference_european` (`CONTAINS` CELEX)
  - optional country filter via `cdm:case-law_originates_in_country`
- `get_article_annotations` -> `owl:annotatedTarget`, `owl:annotatedSource`, `owl:annotatedProperty` + qualifier extraction (`article`, `paragraph`, `subparagraph`, `point`, `comment_on_legal_basis`) into `ArticleAnnotationItem`

## SEARCH
- `search_by_eurovoc` -> 2-step:
  - resolve `tags` through the local EuroVoc index (`find_eurovoc_concept`, `CONTAINS`-style, case-insensitive)
  - final filtering via `cdm:work_is_about_concept_eurovoc` + `VALUES ?concept { <uri...> }`
- `search_by_subject_matter` -> 2-step:
  - resolve `codes` through the local subject-matter index (`CONTAINS`-style, case-insensitive, by URI and label)
  - final filtering via `cdm:resource_legal_is_about_subject-matter` + `VALUES ?concept { <uri...> }`
- `search_by_title` -> `cdm:expression_title` + language filter
- `search_communications` ->
  - `cdm:work_has_resource-type` = `COMMUNIC`
  - `cdm:resource_legal_service_responsible`
- `find_eurovoc_concept` -> local index (`src/cellar_wrapper/data/eurovoc_index.json`)

## MONITORING
- `new_citations` -> `get_citations` + `date > since`
- `new_amendments` -> `get_amendments` + `date > since`
- `new_repeals` -> `get_repeals` + `date > since`
- `new_proposals_to_amend` -> `get_proposals_to_amend` + `date > since`
- `new_delegated_acts` -> `get_delegated_acts` + `date > since`
- `new_case_law` -> `get_cjeu_judgments` + `date > since`
- `new_preliminary_questions` -> `get_preliminary_questions` + `date > since`
- `new_corrigenda` -> `get_corrigenda` + `date > since`
- `new_consolidated` -> `get_consolidated_versions` + `date > since`
- `new_nims` -> `get_nims` + `date > since`
- `new_by_eurovoc` -> local EuroVoc resolution + final query via `VALUES ?concept` + strict `date > since`

## DOWNLOAD
- `get_text` -> REST `resource/celex/{CELEX}` with negotiated MIME and language
- `get_summary` -> summary URI via
  - `cdm:summary_summarizes_work` OR
  - `cdm:summary_legislation_eu_summarizes_resource_legal`
  then REST download with `application/xhtml+xml;type=xhtml5`
