# Command Contracts

This matrix maps the public command surface to the shared runtime return
contracts.

Runtime source-of-truth:
- commands/groups/methods: `src/cellar_wrapper/cli_specs.py`
- return contracts: `src/cellar_wrapper/contract_specs.py`
- payload models: `src/cellar_wrapper/models.py`

| group | command | method | return model | item model | notes |
| --- | --- | --- | --- | --- | --- |
| lookup | `resolve-celex` | `resolve_celex` | `ActRef` | - | single record |
| lookup | `get-act` | `get_act` | `ActDetail` | - | single record |
| lookup | `get-eurovoc` | `get_eurovoc` | `ListResult` | `EurovocTag` | list result; concept tags |
| lookup | `get-subject-matter` | `get_subject_matter` | `ListResult` | `SubjectMatterTag` | list result; subject-matter tags |
| lookup | `get-legal-basis` | `get_legal_basis` | `ListResult` | `RelationItem` | list result; relation rows |
| lookup | `get-directory-codes` | `get_directory_codes` | `ListResult` | `SubjectMatterTag` | list result; directory-code concepts |
| lookup | `get-expressions` | `get_expressions` | `ListResult` | `ExpressionItem` | list result; language expressions |
| relations | `get-amendments` | `get_amendments` | `ListResult` | `RelationItem` | list result; relation rows |
| relations | `get-repeals` | `get_repeals` | `ListResult` | `RelationItem` | list result; relation rows |
| relations | `get-citations` | `get_citations` | `ListResult` | `RelationItem` | list result; relation rows |
| relations | `get-based-on-acts` | `get_based_on_acts` | `ListResult` | `RelationItem` | list result; relation rows |
| relations | `get-completing-acts` | `get_completing_acts` | `ListResult` | `RelationItem` | list result; relation rows |
| relations | `get-proposals-to-change` | `get_proposals_to_change` | `ListResult` | `RelationItem` | list result; proposal changes to the act |
| relations | `get-adopted-act` | `get_adopted_act` | `ListResult` | `RelationItem` | list result; relation rows |
| relations | `get-related-works` | `get_related_works` | `ListResult` | `RelationItem` | list result; relation rows |
| relations | `get-other-relations` | `get_other_relations` | `ListResult` | `RelationItem` | list result; relation rows |
| lifecycle | `get-consolidated-versions` | `get_consolidated_versions` | `ListResult` | `RelationItem` | list result; relation rows |
| lifecycle | `get-corrigenda` | `get_corrigenda` | `ListResult` | `RelationItem` | list result; relation rows |
| lifecycle | `get-nims` | `get_nims` | `ListResult` | `NIMItem` | list result; grouped unique national implementing acts |
| lifecycle | `get-dossier` | `get_dossier` | `ListResult` | `DossierItem` | list result; dossier procedure rows |
| lifecycle | `get-opinions` | `get_opinions` | `ListResult` | `RelationItem` | list result; relation rows |
| lifecycle | `get-deadlines` | `get_deadlines` | `ListResult` | `RelationItem` | list result; relation rows |
| case-law | `get-cjeu-judgments` | `get_cjeu_judgments` | `ListResult` | `CaseLawItem` | list result; case-law rows |
| case-law | `get-ag-opinions` | `get_ag_opinions` | `ListResult` | `RelationItem` | list result; relation rows |
| case-law | `get-preliminary-questions` | `get_preliminary_questions` | `ListResult` | `CaseLawItem` | list result; case-law rows |
| case-law | `get-national-decisions` | `get_national_decisions` | `ListResult` | `CaseLawItem` | list result; case-law rows |
| case-law | `get-article-annotations` | `get_article_annotations` | `ListResult` | `ArticleAnnotationItem` | list result; article annotations |
| search | `search-by-eurovoc` | `search_by_eurovoc` | `ListResult` | `ActRef` | list result; act search rows |
| search | `search-by-subject-matter` | `search_by_subject_matter` | `ListResult` | `ActRef` | list result; act search rows |
| search | `search-by-title` | `search_by_title` | `ListResult` | `ActRef` | list result; act search rows |
| search | `search-communications` | `search_communications` | `ListResult` | `ActRef` | list result; act search rows |
| search | `find-eurovoc-concept` | `find_eurovoc_concept` | `ListResult` | `EurovocTag` | list result; local index concepts |
| monitoring | `new-citations` | `new_citations` | `ListResult` | `RelationItem` | list result; relation rows |
| monitoring | `new-amendments` | `new_amendments` | `ListResult` | `RelationItem` | list result; relation rows |
| monitoring | `new-repeals` | `new_repeals` | `ListResult` | `RelationItem` | list result; relation rows |
| monitoring | `new-proposals-to-change` | `new_proposals_to_change` | `ListResult` | `RelationItem` | list result; new proposal changes to the act |
| monitoring | `new-based-on-acts` | `new_based_on_acts` | `ListResult` | `RelationItem` | list result; relation rows |
| monitoring | `new-case-law` | `new_case_law` | `ListResult` | `CaseLawItem` | list result; case-law rows |
| monitoring | `new-preliminary-questions` | `new_preliminary_questions` | `ListResult` | `CaseLawItem` | list result; case-law rows |
| monitoring | `new-corrigenda` | `new_corrigenda` | `ListResult` | `RelationItem` | list result; relation rows |
| monitoring | `new-consolidated` | `new_consolidated` | `ListResult` | `RelationItem` | list result; relation rows |
| monitoring | `new-nims` | `new_nims` | `ListResult` | `NIMItem` | list result; grouped unique national implementing acts |
| monitoring | `new-by-eurovoc` | `new_by_eurovoc` | `ListResult` | `ActRef` | list result; act search rows |
| download | `get-text` | `get_text` | `DocumentPayload` | - | download payload |
| download | `get-summary` | `get_summary` | `DocumentPayload` | - | download payload |
