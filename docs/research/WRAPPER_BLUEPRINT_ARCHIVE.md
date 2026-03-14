# CELLAR Wrapper Blueprint (ARCHIVE)

> [!WARNING]
> This document is a historical blueprint only.
> It was part of the early design process, but the API contract, examples, and
> implementation have changed since it was written.
>
> Current sources:
> - [../CONTRACT_REFERENCE.md](../CONTRACT_REFERENCE.md)
> - [../CONTRACT_EXAMPLES.md](../CONTRACT_EXAMPLES.md)
> - [../METHOD_MAPPING.md](../METHOD_MAPPING.md)
> - [README.md](README.md)

## What CELLAR Covers and What It Does Not

### Available in CELLAR (Official Journal / EUR-Lex material)
- Regulations, directives, and decisions (adopted acts)
- Legislative proposals (COM)
- Delegated and implementing acts (RTS/ITS as Commission regulations)
- Commission communications (strategies, action plans)
- CJEU case law (judgments, AG opinions, orders)
- National court decisions (`DEC_NC`, with limited completeness)
- National implementation measures (NIMs)
- Consolidated versions
- Corrigenda
- ECB guidelines and recommendations
- Legislative summaries (LegisSum)
- Full texts (PDF, XHTML, DOC)

### Not Available in CELLAR (published outside the Official Journal)
- EBA guidelines
- ESMA guidelines
- EIOPA guidelines
- ESA supervisory Q&A
- ESA opinions on supervisory practices
- ESA consultation papers

EBA, ESMA, and EIOPA exist in CELLAR only as institutional entities
(budget, recruitment, financial statements). Their soft-law output
(guidelines, recommendations, Q&A) requires separate data sources.

Exception: RTS/ITS drafted by the ESAs but formally adopted by the Commission
as delegated or implementing regulations do appear in CELLAR as Commission acts
(`REG_DEL`, `REG_IMPL`).

---

## What the Wrapper Can Expose

### 1. Act Identification

Given a CELEX number (for example `32022R2554`) we can fetch:

| Information | Example |
|---|---|
| Full title (selected language) | Regulation (EU) 2022/2554 on digital operational resilience... |
| Act type | Regulation / Directive / Proposal / Decision |
| Document date | 2022-12-14 |
| Entry into force | 2023-01-16 |
| Start of application | 2025-01-17 |
| In-force status | In force / Repealed / Expired |
| End-of-validity date | 9999-12-31 (open-ended) |
| Treaty basis | Art. 114 TFEU |
| Responsible authority | COM + FISMA |
| ELI | `eli/reg/2022/2554/oj` |
| OJ publication | L 333, 27.12.2022, p. 1 |

Applies to: regulations, directives, decisions, proposals, communications.

### 2. Amendments

Who amends a given act, and what that act amends.

| Direction | Question | Example |
|---|---|---|
| Outgoing | What does this act amend? | DORA amends Reg. 1093/2010 (EBA), Reg. 1094/2010 (EIOPA), Reg. 1095/2010 (ESMA), Dir. 2009/138 (Solvency II), Dir. 2014/65 (MiFID II) |
| Incoming | What amends this act? | As of the blueprint date: no formal amendments to DORA |

CDM property: `resource_legal_amends_resource_legal` (not `work_amends_work`).

Applies to: regulations, directives.

### 3. Repeals

| Direction | Question | Example |
|---|---|---|
| Outgoing | What does this act repeal? | PSD2 repeals PSD1 (Dir. 2007/64) |
| Incoming | Is this act repealed by anything? | PSR proposes to repeal PSD2 |

Two repeal types exist: explicit (`resource_legal_repeals_resource_legal`)
and implicit (`resource_legal_implicitly_repeals_resource_legal`).

Applies to: directives, regulations.

### 4. Delegated and Implementing Acts (RTS/ITS)

Level 2 acts drafted by the ESAs and adopted by the Commission.

| Type | CELLAR resource type | Total in CELLAR |
|---|---|---|
| Delegated regulation (RTS) | `REG_DEL` | 3,399 |
| Implementing regulation (ITS) | `REG_IMPL` | 14,644 |
| Delegated directive | `DIR_DEL` | 240 |
| Implementing directive | `DIR_IMPL` | 150 |
| Implementing decision | `DEC_IMPL` | 5,332 |
| Delegated decision | `DEC_DEL` | 111 |
| Draft acts | `REG_DEL_DRAFT`, `REG_IMPL_DRAFT` | 586 + 707 |

Note: searching RTS/ITS for a specific base act via `work_cites_work` is too
broad because it also matches acts that merely mention the target. A better
approach is `resource_legal_based_on_resource_legal` or title-level filtering.

Applies to: regulations and directives as base acts.

### 5. Citations

Who cites a given act. This is the broadest relation and includes both
normative references and informational mentions.

| Question | Example |
|---|---|
| Who cites DORA? | 18 new acts in the last 12 months, including proposal `52026PC0011` |
| What does DORA cite? | 44+ acts (PSD2, MiFID II, GDPR, eIDAS, CRR, CRD...) |

Filtering by act type and date allows use cases such as "new legislative
proposals citing DORA since January 2025".

Applies to: all document types.

### 6. Proposals to Change

Specific to legislative proposals: what a proposal intends to change.

| Question | Example |
|---|---|
| What does PSR propose to change? | Reg. 1093/2010 (EBA), Reg. 2017/2394 (CPC), PSD2 |
| Which proposals want to change DORA? | `52025PC0943` (CCP/ESMA, amendments/repeal/recast intent) |

Property: `resource_legal_proposes_to_amend_resource_legal` (wrapper-level relation type now labeled `proposes_to_change`).

Applies to: proposals (`PROP_REG`, `PROP_DIR`).

### 7. Consolidated Texts

A consolidated text reflects all amendments and corrigenda up to a point in time.

| Question | Example |
|---|---|
| How many consolidated versions does PSD2 have? | 3: original (2015-12-23), post-amendment (2024-04-08), latest (2025-01-17) |
| How many versions does DORA have? | 1: original (2022-12-27), no amendments |
| Which amendments does a consolidation include? | `act_consolidated_consolidates_resource_legal` -> list of acts |

Consolidated CELEX pattern: `0` + base CELEX + `-` + date
(for example `02015L2366-20250117`).

Applies to: regulations, directives.

### 8. Corrigenda

Technical or editorial corrections to an act.

| Question | Example |
|---|---|
| How many corrigenda does DORA have? | 9 (from 2023-05 to 2025-11) |
| When was the latest one? | 2025-11-21 (`32022R2554R(09)`) |

Corrigendum CELEX pattern: base CELEX + `R(nn)` (for example `32022R2554R(01)`).
Total in CELLAR: 28,677 corrigenda.

Applies to: regulations, directives.

### 9. National Implementation Measures (NIMs)

How Member States transposed a directive into national law.

| Question | Example |
|---|---|
| Which countries transposed PSD2? | Public `get-nims` groups results into unique national acts; one country can still have several implementing acts |
| When did Poland transpose it? | `72015L2366POL_202401176` - 2023-08-29 |
| What is the directive transposition deadline? | `directive_date_transposition` |

NIM CELEX pattern: `7` + directive CELEX + country code + sequence number.
Public wrapper contract: `get-nims` / `new-nims` return unique national implementing acts grouped by national-act `uri`, expose a preferred `celex`, and include grouped context in `all_celexes` and `matching_celexes`. Raw CELLAR row inflation from omnibus acts is intentionally hidden.
Total in CELLAR: 196,630 transposition acts.

Applies to: directives only.

### 10. Legislative Dossier

The full procedural path of a proposal from submission to adoption.

| Question | Example |
|---|---|
| What is the PSR procedure number? | `2023/0210(COD)` |
| Which documents are in the dossier? | COM proposal, EESC opinion, ECB opinion, EDPS opinion, EP position, Council position... |
| What stage is the procedure at? | Trilog / First reading / Adopted |

Property: `dossier_contains_work`.

Applies to: legislative proposals.

### 11. Commission Communications (Early Warning)

Strategic documents signaling future legislation, often the earliest signal
two to three years before a proposal.

| Question | Example |
|---|---|
| Which communications did DG FISMA issue? | Digital Finance Strategy, Retail Payments Strategy, CMU |
| How many proposals did a communication trigger? | DFS -> MiCA, DORA, DLT Pilot, PSR, PSD3, FIDA, Digital Euro (10+ acts) |
| Which EuroVoc tags does a communication have? | Mapping to future regulatory areas |

Filter property: `resource_legal_service_responsible` (for example `FISMA`).

Applies to: communications (`COMMUNIC`).

### 12. CJEU Case Law

Judgments of the Court of Justice of the EU interpreting a given act.

| Question | Example |
|---|---|
| Which judgments concern PSD2? | 5 CJEU judgments (including C-287/19 DenizBank) |
| Which articles does a judgment interpret? | `case-law_interpretes_resource_legal` |
| Who was the Advocate General? | `case-law_delivered_by_advocate-general` |
| Which AG opinions preceded the judgment? | `case-law_has_conclusions_opinion_advocate-general` |
| Which academic articles discuss the judgment? | `case-law_article_journal_related` |
| Which country sent the preliminary question? | `case-law_originates_in_country` |

Applies to: judgments (`JUDG`), AG opinions (`OPIN_AG`), orders (`ORDER`).

### 13. National Court Decisions

National court decisions referring to EU law.

| Question | Example |
|---|---|
| National decisions on PSD2? | 3 direct references (limited completeness: 56%) |
| From which country? | Germany dominates (7,815), France (4,580), Poland (286) |
| Which articles? | Format such as `32015L2366-A04PT21` (Art. 4 point 21) |

Limitation: only 56% of national court decisions populate
`european_act_reference`. Country coverage is uneven.

Applies to: `DEC_NC`.

### 14. EuroVoc Classification

The multilingual EU subject thesaurus, with 7,253 concepts in use.

| Question | Example |
|---|---|
| Which tags does DORA have? | financial technology, cloud computing, information security, risk management, digitisation, outsourcing, financial services, digital single market, information technology |
| Find acts about "payment system" + "data protection" | Multi-tag search |
| Find a concept by name | `"crypto"` -> `eurovoc:6778` (cryptography); `"fintech"` -> no direct concept, use `"financial technology"` / `c_79e507c2` |
| Concept hierarchy | broader/narrower terms via SKOS |

Note: EuroVoc uses two URI formats, old numeric (`eurovoc:5283`) and newer hash
(`eurovoc:c_e749c083`). Code must not assume one format.

Note: CJEU decisions do not use EuroVoc. They use
`resource_legal_is_about_subject-matter`.

Applies to: regulations, directives, proposals, communications
(not CJEU case law).

### 15. Legal Basis

Treaty or legislative basis on which the act was adopted.

| Question | Example |
|---|---|
| DORA treaty basis? | Art. 114 TFEU |
| Legislative basis (parent act)? | `resource_legal_based_on_resource_legal` |

Applies to: regulations, directives, proposals.

### 16. Deadlines

Multiple dates associated with an act.

| Date | DORA example |
|---|---|
| Entry into force | 2023-01-16 |
| Start of application | 2025-01-17 |
| Review deadline | 2028-01-17 |
| Reporting deadline | 2029-01-17 |
| Directive transposition deadline | `directive_date_transposition` |

Property: `resource_legal_date_deadline` (multi-valued).

Applies to: regulations, directives.

### 17. Full Text Download

Download the full text of an act in a selected format and language.

| Format | Availability |
|---|---|
| PDF | Almost always |
| XHTML | Often |
| DOCX | For some proposals |
| Summary (LegisSum) | For more important acts |

Path: Work -> Expression (language) -> Manifestation (format) -> Item (file).

Applies to: all types.

### 18. Temporal Search / Monitoring

Detect new documents since the last check.

| Question | Filter |
|---|---|
| New OJ acts since date X | `work_date_document > X` + type |
| New citations of act Y since date X | `work_cites_work = Y` + `date > X` |
| New CJEU judgments since date X | type `JUDG` + `date > X` |
| New proposals in topic Z | EuroVoc + type `PROP_*` + `date > X` |
| New NIMs for a directive since date X | CELEX `7{celex}*` + `date > X` |
| New corrigenda for an act since date X | CELEX `{celex}R(*` + `date > X` |
| New consolidated versions | CELEX `0{celex}*` + `date > X` |

This is the core monitoring surface: each of the above queries with a
"since last check" parameter.

### 19. CELEX -> CELLAR URI Resolution

Translate a CELEX number into the internal CELLAR URI required by many
relational queries.

| Question | Example |
|---|---|
| CELLAR URI for CELEX `32022R2554`? | `http://publications.europa.eu/resource/cellar/...` |
| Does the CELEX exist in CELLAR? | Yes / No |

Gotcha: string comparison `= '32022R2554'` does not work. Use
`FILTER(CONTAINS(?celex, '2022R2554'))`.

Applies to: all document types.

### 20. Preliminary Questions

Open cases referred to the CJEU by national courts. They can signal that an act
is contested or unclear.

| Question | Example |
|---|---|
| Which preliminary questions concern PSD2? | 10 cases (including C-287/19 DenizBank) |
| Which country did the question come from? | `case-law_originates_in_country` |
| Who referred it? | The referring court |

Property: `communication_case_new_submits_preliminary_question`.

Applies to: CJEU case-law flow (`JUDG`, `ORDER`).

### 21. Institutional Opinions

Opinions issued during the legislative procedure: ECB, EESC, EDPS, EP committees.

| Question | Example |
|---|---|
| Which opinions were issued on PSR? | ECB opinion, EESC opinion, EDPS opinion |
| When? | Opinion document date |

Property: `contains_eesc_opinion_on`, `contains_ep_opinion_on`,
plus dossier-based filtering.

Applies to: legislative proposals.

### 22. Completing Acts

Acts that complement, rather than amend, a base act.

| Question | Example |
|---|---|
| What completes DORA? | Delegated acts supplementing technical details |

Property: `resource_legal_completes_resource_legal`.

Applies to: regulations, directives.

### 23. Article-Level Annotations

Granular links at article / paragraph level: who cites or amends a specific
article instead of the whole act.

| Question | Example |
|---|---|
| Which acts refer to Art. 4 PSD2? | OWL Annotation Axioms - 570 annotations for PSD2 |
| Which DORA articles amend MiFID II provisions? | `annotatedSource` + `annotatedTarget` + qualifier |

Pattern: OWL reification
(`owl:annotatedSource`, `owl:annotatedTarget`, `owl:annotatedProperty`).

Applies to: regulations, directives, proposals.

### 24. Expressions and Formats

List available language versions and file formats.

| Question | Example |
|---|---|
| In how many languages is DORA available? | 24 language versions |
| Which formats are available? | PDF, XHTML, DOC, FORMEX |
| URI for a specific file? | Manifestation -> Item -> URL |

FRBR path: Work -> Expression (language) -> Manifestation (format) -> Item (file).

Applies to: all types.

### 25. Directory Codes

Thematic classification according to the EUR-Lex Directory of EU legislation.

| Question | Example |
|---|---|
| DORA directory code? | for example `10.20.30` (banking / prudential supervision) |

Property: `resource_legal_is_about_concept_directory-code`.

Applies to: regulations, directives, proposals.

### 26. Proposal -> Adopted Act

Track whether a legislative proposal was adopted and which final act resulted.

| Question | Example |
|---|---|
| Was the PSR proposal (`52023PC0367`) adopted? | Not yet (pending) |
| What came out of the MiCA proposal (`52020PC0593`)? | `32023R1114` (MiCA Regulation) |

Property: `resource_legal_adopts_resource_legal`
(reverse direction from adopted act -> proposal).

Applies to: proposals and adopted acts.

### 27. Search by Subject Matter

Search acts by subject-matter codes. This is an alternative to EuroVoc and is
especially useful for CJEU case law, which does not use EuroVoc.

| Question | Example |
|---|---|
| CJEU judgments on "Freedom of establishment"? | `resource_legal_is_about_subject-matter` + type `JUDG` |
| Competition acts since 2024? | Subject-matter code + `date > 2024` |

There are 385 subject-matter codes. The largest buckets include External
relations, Competition, and Environment.

Applies to: all types, including CJEU case law.

### 28. Additional Legislative Relations

Less common but still important relationships for a full regulatory graph.

| Relation | CDM property | Meaning |
|---|---|---|
| Suspension | `resource_legal_suspends_resource_legal` | Temporary suspension of application |
| Partial suspension | `resource_legal_partially_suspends_resource_legal` | Suspension of selected provisions |
| Deferral of application | `resource_legal_defers_application_of_resource_legal` | Delayed application date |
| Obsolescence | `resource_legal_renders_obsolete_resource_legal` | Act becomes obsolete without formal repeal |
| Influence | `resource_legal_influences_resource_legal` | Looser "influences" relation |

Applies to: regulations, directives.

---

## Summary Function Map

```text
CELLAR Wrapper (~33 methods)
│
├── LOOKUP (identification)
│   ├── resolve_celex(celex)              -> CELEX -> CELLAR URI (with CONTAINS workaround)
│   ├── get_act(celex)                    -> metadata, title, dates, status
│   ├── get_eurovoc(celex)                -> subject tags
│   ├── get_subject_matter(celex)         -> subject-matter codes
│   ├── get_legal_basis(celex)            -> treaty / legislative basis
│   ├── get_directory_codes(celex)        -> EUR-Lex classification codes
│   └── get_expressions(celex)            -> available languages and formats
│
├── RELATIONS (legal links)
│   ├── get_amendments(celex)             -> amendments (in / out)
│   ├── get_repeals(celex)                -> repeals (in / out)
│   ├── get_citations(celex)              -> citations (in / out)
│   ├── get_based_on_acts(celex)          -> broad "based on" acts / documents
│   ├── get_completing_acts(celex)        -> completing acts
│   ├── get_proposals_to_change(celex)     -> proposals to change
│   ├── get_adopted_act(celex)            -> proposal -> adopted act
│   ├── get_related_works(celex)          -> related documents
│   └── get_other_relations(celex)        -> suspends / defers / obsolete / influences
│
├── LIFECYCLE
│   ├── get_consolidated_versions(celex)  -> consolidated versions
│   ├── get_corrigenda(celex)             -> corrigenda
│   ├── get_nims(celex)                   -> national implementation measures
│   ├── get_dossier(celex)                -> legislative procedure
│   ├── get_opinions(celex)               -> institutional opinions
│   └── get_deadlines(celex)              -> deadlines and effective dates
│
├── CASE LAW
│   ├── get_cjeu_judgments(celex)         -> CJEU judgments concerning the act
│   ├── get_ag_opinions(celex)            -> Advocate General opinions
│   ├── get_preliminary_questions(celex)  -> preliminary questions
│   ├── get_national_decisions(celex)     -> national court decisions
│   └── get_article_annotations(celex)    -> article-level annotations
│
├── SEARCH
│   ├── search_by_eurovoc(tags, type, since)          -> search by EuroVoc tags
│   ├── search_by_subject_matter(codes, type, since)  -> search by subject matter
│   ├── search_by_title(keyword, type, since)         -> search by title
│   ├── search_communications(dg, since)              -> Commission communications
│   └── find_eurovoc_concept(label)                   -> find EuroVoc concept
│
├── MONITORING
│   ├── new_citations(celex, since)       -> new citations
│   ├── new_amendments(celex, since)      -> new amendments
│   ├── new_proposals_to_change(celex, since) -> proposals that may amend, repeal, or recast
│   ├── new_based_on_acts(celex, since)   -> new "based on" acts / documents
│   ├── new_case_law(celex, since)        -> new case law
│   ├── new_corrigenda(celex, since)      -> new corrigenda
│   ├── new_consolidated(celex, since)    -> new consolidations
│   ├── new_nims(celex, since)            -> new transposition measures
│   └── new_by_eurovoc(tags, type, since) -> new acts in a topic
│
└── DOWNLOAD
    ├── get_text(celex, lang, format)     -> full text
    └── get_summary(celex, lang)          -> legislative summary
```

---

## What CELLAR Does Not Cover

| Need | Source |
|---|---|
| EBA guidelines | `eba.europa.eu` |
| ESMA guidelines | `esma.europa.eu` |
| EIOPA guidelines | `eiopa.europa.eu` |
| Supervisory Q&A | ESA websites |
| Public consultations | ESA websites |
| Supervisory positions | ESA websites |
| Registers (MiCA, DORA) | ESA websites |

These require separate wrappers. CELLAR does not replace them.

## Next Steps

1. Implement the Python library surface (`cellar/`) around the methods above.
2. Keep CLI as a thin layer on top of the library.
3. Build monitoring on top of the wrapper rather than in the core client.
4. Add separate ESA data-source research and wrappers where needed.
