# CELLAR API — Research Report

## What CELLAR is

CELLAR is the central content and metadata repository of the **Publications Office of the European Union**. It stores EU law, case law, Official Journals, and other publications. The data is open and publicly available — **with no registration or authentication**.

## Access methods

### REST API (HTTP GET)

Download documents by identifier:

```
https://publications.europa.eu/resource/celex/{CELEX_NUMBER}
https://publications.europa.eu/resource/cellar/{UUID}
```

Content negotiation via HTTP headers:
- `Accept`: `application/pdf`, `application/xhtml+xml`, `application/xml`, `application/rdf+xml`, `application/zip;mtype=...`
- `Accept-Language`: ISO 639-3 code (`pol`, `eng`, `fra`, ...)

Examples:

```bash
# PDF in Polish
curl -L -H "Accept: application/pdf" -H "Accept-Language: pol" \
  "https://publications.europa.eu/resource/celex/32015L2366" -o psd2_pl.pdf

# XHTML in English
curl -L -H "Accept: application/xhtml+xml" -H "Accept-Language: eng" \
  "https://publications.europa.eu/resource/celex/32015L2366" -o psd2_en.xhtml

# RDF metadata
curl -L -H "Accept: application/rdf+xml" \
  "https://publications.europa.eu/resource/celex/32015L2366" -o psd2_metadata.rdf
```

Available formats: PDF, HTML, XHTML, Formex (XML for Official Journals), RDF/XML.

### SPARQL Endpoint

```
https://publications.europa.eu/webapi/rdf/sparql
```

Key prefixes:

```sparql
PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
```

### RSS/Atom Feeds

Notifications about new or changed publications.

### Bulk Download

- **Data dump**: `datadump.publications.europa.eu` (requires EU Login)
- **data.europa.eu**: Official Journals in CSV with links to Formex XML

## Data model (CDM + FRBR)

Data structure based on **FRBR** (Functional Requirements for Bibliographic Records) + **RDF Schema/OWL**.

Hierarchy: **Work → Expression → Manifestation → Item**

### Work (legal act as a concept)

A single record with metadata, legal relations, dates, and status.

### Expression (language version)

Each Work has up to 23 Expressions (official EU languages). Each contains:
- `expression_title` — full title in a given language
- `expression_title_short` — e.g. "Payment Services Directive, psd 2, psd II"
- `expression_uses_language` — language code

### Manifestation (file format)

Each Expression typically has 3 manifestations:

| Type | Format | Description |
|---|---|---|
| `pdfa1a` | PDF/A-1a | Archival PDF |
| `fmx4` | Formex 4 XML | Structured XML (content + annexes) |
| `xhtml` | XHTML | HTML for browser display |

Plus OJ metadata: page number, volume, subsection, permanence.

### Item (physical file)

Concrete downloadable files with MIME type and full URI.

CDM documentation: https://op.europa.eu/en/web/eu-vocabularies/cdm

## Fields available at Work level

Studied on the example of PSD2 (CELEX: `32015L2366`).

### Identification

| CDM field | Description | Example PSD2 |
|---|---|---|
| `resource_legal_id_celex` | CELEX number | `32015L2366` |
| `resource_legal_eli` | European Legislation Identifier | `http://data.europa.eu/eli/dir/2015/2366/oj` |
| `work_id_document` | Identifiers (CELEX, OJ, IMMC) | `celex:32015L2366`, `oj:JOL_2015_337_R_0002` |
| `work_has_resource-type` | Document type | `DIR` (directive) |
| `resource_legal_type` | Act type (literal) | `L` |
| `resource_legal_number_natural` | Act number | `2366` |
| `resource_legal_year` | Year | `2015` |
| `resource_legal_id_sector` | Sector CELEX | `3` (adopted legislation) |
| `work_version` | Version | `final` |

### Dates

| CDM field | Description | Example PSD2 |
|---|---|---|
| `work_date_document` | Document date | 2015-11-25 |
| `resource_legal_date_entry-into-force` | Entry into force | 2016-01-12 |
| `directive_date_transposition` | Transposition deadline | 2018-01-13 |
| `resource_legal_date_deadline` | Deadline | 2021-01-13 |
| `resource_legal_date_end-of-validity` | End of validity | 2026-06-18 |
| `work_date_creation_legacy` | OJ publication date | 2015-12-23 |

### Status

| CDM field | Description | Example PSD2 |
|---|---|---|
| `resource_legal_in-force` | In force | `true` (1) |
| `resource_legal_eea` | EEA relevance | `true` (1) |
| `resource_legal_codified_version` | Whether codified version | `false` (0) |

### Institutions

| CDM field | Description | Example PSD2 |
|---|---|---|
| `work_created_by_agent` | Authors | EP (Parliament) + CONSIL (Council) |
| `resource_legal_responsibility_of_agent` | Responsible DGs | DG JUST + DG FISMA |
| `resource_legal_addresses_institution` | Addressees | EUMS (Member States) |
| `resource_legal_signatory_name2` | Signatories | M. Schulz, N. Schmit |

### Subject matter

| CDM field | Description | Example PSD2 |
|---|---|---|
| `resource_legal_is_about_subject-matter` | Subject matter (authority codes) | Free movement of capital, Freedom of establishment, Internal market |
| `resource_legal_is_about_concept_directory-code` | Directory | Free movement of capital, Banks |
| `work_is_about_concept_eurovoc` | EuroVoc descriptors | approximation of laws, single market, financial institution, service, financial services, payment, intra-EU payment, electronic money, financial legislation, electronic banking |

## Legal relations (graph)

### Outgoing relations from the act (Work → other)

| CDM field | Direction | Example PSD2 |
|---|---|---|
| `resource_legal_amends_resource_legal` | What THIS act amends | 32002L0065, 32009L0110, 32013L0036, 32010R1093 |
| `resource_legal_repeals_resource_legal` | What THIS act repeals | 32007L0064 (PSD1) |
| `resource_legal_implicitly_repeals_resource_legal` | What it implicitly repeals | 32009L0111 |
| `resource_legal_based_on_concept_treaty` | Treaty basis | Art. 114 TFUE |
| `resource_legal_based_on_resource_legal` | Legal basis | 12012E114 |
| `resource_legal_adopts_resource_legal` | What it adopts (proposal) | 52013PC0547 |
| `work_cites_work` | What it cites | 31 acts |

### Incoming relations (other → Work)

Studied for PSD2 — count of objects pointing to PSD2:

| CDM field | Count | Description |
|---|---|---|
| `work_cites_work` | 283 | Acts citing PSD2 |
| `measure_national_implementing_implements_resource_legal` | 258 | National laws implementing PSD2 |
| `act_consolidated_consolidates_resource_legal` | 22 | Consolidated texts |
| `resource_legal_based_on_resource_legal` | 14 | Acts delegated/implementing based on PSD2 |
| `act_consolidated_based_on_resource_legal` | 12 | Consolidations based on PSD2 |
| `communication_case_new_submits_preliminary_question_resource_legal` | 10 | Preliminary questions to the CJEU |
| `resource_legal_corrects_resource_legal` | 7 | Corrigenda (corrigenda) |
| `resource_legal_completes_resource_legal` | 5 | Completing acts PSD2 |
| `case-law_interpretes_resource_legal` | 5 | CJEU case law interpreting PSD2 |
| `resource_legal_proposes_to_amend_resource_legal` | 2 | Proposals to amend |
| `resource_legal_amends_resource_legal` | 2 | Acts amending PSD2 (DORA 32022L2556, IPR 32024R0886) |
| `resource_legal_implicitly_repeals_resource_legal` | 1 | PSD3 (32023L2673) implicitly repeals PSD2 |
| `dossier_contains_work` | 1 | Legislative procedure dossier |
| `summary_summarizes_work` / `summary_legislation_eu_summarizes_resource_legal` | 1 | Summary EUR-Lex |
| `case-law_declares_valid_resource_legal` | 1 | Judgment confirming validity |
| `dossier_produces_resource_legal` | 1 | Dossier -> final act |
| `work_related_to_work` | 1 | Related act |
| `work_is_logical_successor_of_work` | 1 | Logical successor (consolidated text) |
| `event_legal_contains_work` | 1 | Legal event |
| `owl:annotatedTarget` | 570 | Granular annotations (article-to-article) |

## Details of selected relations

### proposes_to_amend — PSD2 amendment proposals

| CELEX | Date | Type | Title |
|---|---|---|---|
| `52020PC0596` | 2020-09-24 | PROP_DIR | DORA proposal, amending among others PSD2, CRD IV, and MiFID II |
| `52023PC0366` | 2023-06-28 | PROP_DIR | **Proposal PSD3** — "on payment services and electronic money services... repealing Directives 2015/2366/EU and 2009/110/EC" |

### summary_summarizes — Legislative summary

Official EUR-Lex summary (Summaries of EU Legislation):
- ID: `2404020302_1`, version 7.0.1
- Validated by DG FISMA
- Drafted in English, last update: 2024-11-09
- URI: `http://publications.europa.eu/resource/legissum/2404020302_1`
- Type: `LEGIS_SUM`

### dossier_contains — Legislative procedure 2013/0264/COD

Full dossier for the OLP (ordinary legislative procedure):

| Date | Type | CELEX | Role |
|---|---|---|---|
| 2013-07-24 | `PROP_DIR` | `52013PC0547` | Commission proposal |
| 2013-07-24 | `SWD` | `52013SC0282` | Staff Working Document (impact assessment) |
| 2013-12-05 | `NOTICE` | `52014XX0208(05)` | Notice |
| 2013-12-11 | `OPIN` | `52013AE5238` | EESC opinion |
| 2014-02-05 | `OPIN` | `52014AB0009` | ECB opinion |
| 2014-04-03 | `RES_LEGIS` | `52014AP0280` | EP position (1st reading) |
| 2015-10-08 | `RES_LEGIS` | `52015AP0346` | EP position (2nd reading) |
| 2015-10-30 | `ITEM_IA_NOTE` | — | Note to the Council (point A) x2 |
| 2015-11-10 | `ACT_LEGIS` | — | Legislative act |
| 2015-11-17 | `VOTING_RES` | — | Council voting result |
| 2015-11-25 | **`DIR`** | **`32015L2366`** | **PSD2 — adopted directive** |
| 2015-11-25 | `ACT_LEGIS` | — | Legislative act (signature) |
| 2015-12-11 | `ACT_LEGIS` | — | Legislative act (publication) |

Dossier metadata:
- `dossier_identifier`: `procedure:2013_264`
- `procedure_code_interinstitutional_reference_procedure`: `2013/0264/COD`
- `dossier_adopted-proposal`: 1
- `dossier_pending-proposal`: 0
- `dossier_withdrawn-proposal`: 0
- `dossier_initiated_by_act_preparatory`: `52013PC0547`
- `dossier_produces_resource_legal`: `32015L2366`
- `procedure_code_interinstitutional_has_type`: OLP

### is_logical_successor — Logical successor

| CELEX | Type | Date |
|---|---|---|
| `02015L2366-20240408` | `CONS_TEXT` | 2024-04-08 |

Consolidated text PSD2 as of 8 April 2024 (after DORA and IPR changes).

### annotatedTarget — Granular annotations (570 items)

Relations at article level. OWL Axiom Annotations link, for example, a specific article of a national law to a specific article of PSD2. Most are `measure_national_implementing_implements_resource_legal`: national laws indicating which PSD2 article they implement.

## CELEX Variants for a Single Act

| Prefix | Meaning | PSD2 examples |
|---|---|---|
| `3` | Adopted legislation | `32015L2366` |
| `3...R(xx)` | Corrigenda | `32015L2366R(01)` to `R(07)`: 7 corrigenda |
| `0` | Consolidated texts | `02015L2366-20151223`, `02015L2366-20240408`, `02015L2366-20250117` |
| `7` | National implementing measures | `72015L2366POL_258600`, `72015L2366DEU_253864`, ... — ~230+ |
| `5` | Preparatory documents | `52013PC0547` (proposal), `52023PC0366` (proposal PSD3) |

## Example SPARQL queries

### Find an act by CELEX and fetch its URI

```sparql
PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>

SELECT ?work WHERE {
  ?work cdm:resource_legal_id_celex '32015L2366' .
}
```

### Find acts amending a given act

```sparql
PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>

SELECT DISTINCT ?amendingWork ?celex ?date WHERE {
  ?amendingWork cdm:resource_legal_amends_resource_legal <CELLAR_URI> .
  OPTIONAL { ?amendingWork cdm:resource_legal_id_celex ?celex }
  OPTIONAL { ?amendingWork cdm:work_date_document ?date }
}
ORDER BY ?date
```

### Find acts repealing a given act (explicitly and implicitly)

```sparql
PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>

SELECT DISTINCT ?work ?celex ?date ?relType WHERE {
  {
    ?work cdm:resource_legal_repeals_resource_legal <CELLAR_URI> .
    BIND('repeals' AS ?relType)
  } UNION {
    ?work cdm:resource_legal_implicitly_repeals_resource_legal <CELLAR_URI> .
    BIND('implicitly_repeals' AS ?relType)
  }
  OPTIONAL { ?work cdm:resource_legal_id_celex ?celex }
  OPTIONAL { ?work cdm:work_date_document ?date }
}
```

### Find proposals to amend

```sparql
PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>

SELECT ?work ?celex ?date WHERE {
  ?work cdm:resource_legal_proposes_to_amend_resource_legal <CELLAR_URI> .
  OPTIONAL { ?work cdm:resource_legal_id_celex ?celex }
  OPTIONAL { ?work cdm:work_date_document ?date }
}
```

### Fetch dossier (full legislative procedure)

```sparql
PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>

SELECT ?dossier ?work ?celex ?date ?type WHERE {
  ?dossier cdm:dossier_contains_work <CELLAR_URI> .
  ?dossier cdm:dossier_contains_work ?work .
  OPTIONAL { ?work cdm:resource_legal_id_celex ?celex }
  OPTIONAL { ?work cdm:work_date_document ?date }
  OPTIONAL { ?work cdm:work_has_resource-type ?type }
}
ORDER BY ?date
```

### Fetch language versions (Expressions)

```sparql
PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>

SELECT ?expression ?lang ?title WHERE {
  ?expression cdm:expression_belongs_to_work <CELLAR_URI> .
  OPTIONAL { ?expression cdm:expression_uses_language ?lang }
  OPTIONAL { ?expression cdm:expression_title ?title }
}
ORDER BY ?lang
```

### Fetch all incoming relations (who points to a given act)

```sparql
PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>

SELECT DISTINCT ?prop (COUNT(?other) as ?count) WHERE {
  ?other ?prop <CELLAR_URI> .
}
GROUP BY ?prop
ORDER BY DESC(?count)
```

---

# DEEP DIVE: CJEU Case Law on PSD2

## Judgments Interpreting PSD2

5 CJEU judgments formally interpreting PSD2:

| CELEX | ECLI | Date | Case | Chamber |
|---|---|---|---|---|
| `62016CJ0643` | ECLI:EU:C:2018:67 | 2018-02-07 | **American Express v HM Treasury** — three-party card schemes, co-branding, validity of Art. 35 PSD2 | Chamber I |
| `62018CJ0778` | ECLI:EU:C:2020:831 | 2020-10-15 | **Association française des usagers de banques v Ministre** — termination of framework contracts (Art. 55), linkage with credit agreements | Chamber V |
| `62019CJ0287` | ECLI:EU:C:2020:897 | 2020-11-11 | **DenizBank v Verein für Konsumenteninformation** — the concept of a "payment instrument" (Art. 4(14)), NFC, implied consent | Chamber I |
| `62020CJ0484` | ECLI:EU:C:2021:975 | 2021-12-02 | **Vodafone Kabel Deutschland v Verbraucherzentralen** — transaction fees (Art. 62(4)), full harmonisation (Art. 107(1)) | Chamber IX |
| `62022CJ0661` | ECLI:EU:C:2024:148 | 2024-02-22 | **'ABC Projektai' v Lietuvos bankas** — definition of a payment service (Art. 4(3) and (5)), holding client funds | Chamber V |

## Preliminary questions (10 cases)

| CELEX | Date | Status | Case |
|---|---|---|---|
| `62016CN0643` | 2016-12-12 | Resolved | American Express (UK) |
| `62018CN0778` | 2018-12-11 | Resolved | Usagers de banques (France) |
| `62019CN0287` | 2019-04-05 | Resolved | DenizBank (Austria) |
| `62020CN0484` | 2020-10-01 | Resolved | Vodafone (Germany) |
| `62021CN0448` | 2021-07-21 | **Removed** | Portugal — Banco BPI |
| `62022CN0661` | 2022-10-20 | Resolved | Bruc Bond (Lithuania) |
| **`62025CN0051`** | 2025-01-28 | **Pending** | Betaal Garant v De Nederlandsche Bank (Netherlands) |
| **`62025CN0070`** | 2025-02-03 | **Pending** | N.O. v PKO BP S.A. (Poland!) |
| **`62025CN0274`** | 2025-04-10 | **Pending** | Alternative Payments v Lietuvos bankas (Lithuania) |
| **`62025CN0339`** | 2025-05-17 | **Pending** | Iulicris Recycling v Ibanfirst (Belgium) |

## Validity judgment

C-643/16 (American Express) — The CJEU confirmed the validity of art. 35(1) i (2)(b) PSD2.

## Advocate General opinions

| CELEX | Date | Rzecznik | Case |
|---|---|---|---|
| `62018CC0778` | 2020-02-27 | Saugmandsgaard Øe | C-778/18 |
| `62019CC0287` | 2020-04-30 | Campos Sánchez-Bordona | C-287/19 (DenizBank) |
| `62022CC0661` | 2023-10-05 | Campos Sánchez-Bordona | C-661/22 (ABC Projektai) |

## Fields available on judgments (studied on C-287/19)

Case-law-specific fields (`cdm:case-law_*`):
- `case-law_ecli` — ECLI identifier
- `case-law_has_procjur` — procedure type (REFER_PREL = preliminary question)
- `case-law_delivered_by_court-formation` — court formation (chamber)
- `case-law_delivered_by_judge` — judge-rapporteur
- `case-law_delivered_by_advocate-general` — Advocate General
- `case-law_interpretes_resource_legal` — which acts it interprets
- `case-law_declares_valid_resource_legal` — which acts it finds valid
- `case-law_originates_in_country` — country of the referring court
- `case-law_uses_procedure_language` — language of proceedings
- `case-law_national-judgement` — national court judgment (follow-up)
- `case-law_commented_by_agent` — who submitted observations (Commission, governments)
- `case-law_article_journal_related` — scholarly articles discussing the judgment
- `case-law_published_in_erecueil` — whether published in ECR

---

# DEEP DIVE: Delegated and implementing acts based on PSD2

## Delegated regulations (RTS)

| CELEX | Date | Title | In-force |
|---|---|---|---|
| `32017R2055` | 2017-06-23 | RTS — cooperation and exchange of information between supervisory authorities (art. 28(5)) | Yes |
| `32018R0389` | 2017-11-27 | **RTS SCA/CSC** — strong customer authentication and secure communication (art. 98(4)) | Yes |
| `32019R0411` | 2018-11-29 | RTS — electronic central register (art. 15(4)) | Yes |
| `32020R1423` | 2019-03-14 | RTS — centralne pointy konyestowe (art. 29(7)) | Yes |
| `32021R1722` | 2021-07-18 | RTS — cross-border supervisory cooperation (art. 29(7)) | Yes |
| `32022R2360` | 2022-08-03 | Amendment to the RTS on SCA: 90-day exemption for account access | Yes |
| `32023R1650` | 2023-08-15 | Correction of the Swedish version of the SCA RTS | Yes |
| `32025R0212` | 2024-09-13 | Correction to RTS 2017/2055 | Yes |

## Implementing regulation (ITS)

| CELEX | Date | Title | In-force |
|---|---|---|---|
| `32019R0410` | 2018-11-29 | ITS on the details and structure of information notified to the EBA (art. 15(5)) | Yes |

## Commission report

| CELEX | Date | Title |
|---|---|---|
| `52023DC0365` | 2023-06-28 | Review report on Directive 2015/2366 (basis for PSD3) |

## Consolidated texts PSD2

| CELEX | Date | Description |
|---|---|---|
| `02015L2366-20151223` | 2015-12-23 | Version oryginalna |
| `02015L2366-20240408` | 2024-04-08 | After DORA and IPR amendments |
| `02015L2366-20250117` | 2025-01-17 | **Latest** consolidated version |

## Consolidated texts of acts amended by PSD2

| CELEX | Date | Act |
|---|---|---|
| `02010R1093-20160112` | 2016-01-12 | EBA Regulation |
| `02013L0036-20180113` | 2018-01-13 | CRD IV |
| `02013L0036-20220101` | 2022-01-01 | CRD IV (nowsza) |
| `02009L0110-20180113` | 2018-01-13 | Directive on electronic money (EMD2) |
| `02002L0065-20180113` | 2018-01-13 | Directive on distance marketing of financial services |

---

# DEEP DIVE: National implementing measures PSD2

## Implementation statistics by country

258 national implementing measures across 28 countries:

| Country | Count | Links to pages | | Country | Count | Links |
|---|---|---|---|---|---|---|
| Czechia | 73 | 0 | | Netherlands | 8 | 0 |
| Lithuania | 21 | 0 | | Cyprus | 7 | 0 |
| Hungary | 21 | 0 | | Poland | 7 | 0 |
| Slovakia | 14 | 0 | | Slovenia | 6 | 5 |
| France | 13 | 0 | | Malta | 6 | 0 |
| Estonia | 11 | **11** | | Croatia | 5 | 0 |
| Latvia | 11 | **9** | | Romania | 4 | 0 |
| Finlandia | 10 | 0 | | Dania | 4 | 0 |
| Sweden | 9 | 0 | | Bulgaria | 4 | 1 |

Plus: UK (4), Greece (3), Spain (3), Italy (3), Belgium (2), Portugal (2), Ireland (2), Germany (2), Austria (2), Luxembourg (1).

**Note**: Czechia (73) has an inflated count — the omnibus law Zákon č. 183/2017 Sb. declares the transposition of 224 directives at once.

## Available fields on NIMs

| CDM field | Coverage | Description |
|---|---|---|
| `work_title` (in the national language) | 100% | Title of the national law |
| `measure_national_implementing_date_notification` | 100% | Notification date to the Commission |
| `measure_national_implementing_type_act` | 100% | Act type krajowego |
| `measure_national_implementing_name_official_journal` | 99.6% | Official journal name |
| `measure_national_implementing_reference_member-state` | 64% | Countryowa signature |
| `resource_legal_date_entry-into-force` | 46% | Entry-into-force date |
| `measure_national_implementing_national_website_link` | **10%** | Link to the text |
| `resource_legal_eli` | 2.3% | ELI identifier |

**Key finding**: The property is `measure_national_implementing_implemented_by_country` (NOT `adopted_by_country`).

## Polish NIMs (7 sztuk)

| CELEX | Title | Type | Dz.U. |
|---|---|---|---|
| `72015L2366POL_258600` | Act of 22.03.2018 amending the Payment Services Act | Amendment | DzU 2018/864 |
| `72015L2366POL_259382` | Act of 10.05.2018 amending the Payment Services Act | Amendment | DzU 2018/1075 |
| `72015L2366POL_259466` | Ministry of Finance regulation of 06.06.2018 on the method of calculating the amount | Regulation | DzU 2018/1110 |
| `72015L2366POL_259467` | Act of 19.08.2011 on payment services (consolidated text) | Act | DzU 2017/2003 |
| `72015L2366POL_259472` | Act of 10.05.2018 on personal data protection | Act | DzU 2018/1000 |
| `72015L2366POL_202101589` | Act of 21.01.2021 amending the Act on trading in instruments | Amendment | DzU 2021/355 |
| `72015L2366POL_202401176` | Act of 16.08.2023 amending certain laws (financial market) | Amendment | DzU 2023/1723 |

---

# DEEP DIVE: Comparison of act types in CELLAR

## Data scale in CELLAR

| Type | Count | Description |
|---|---|---|
| `PROCUREMENT_NOTICE` | 1,911,563 | Procurement notices |
| `MEAS_NATION_IMPL` | 196,630 | National implementing measures |
| `REG` | 144,952 | Regulations |
| `CONS_TEXT` | 73,357 | Consolidated texts |
| `JUDG` | 33,739 | CJEU judgments |
| `DEC` | 23,917 | Decisions |
| `REG_IMPL` | 14,643 | Implementing regulations |
| `PROP_REG` | 13,825 | Regulation proposals |
| `DIR` | 7,733 | Directives |
| `PROP_DIR` | 3,197 | Directive proposals |

## RDF type hierarchy

| Act type | RDF classes |
|---|---|
| Regulation | `cdm:regulation` > `cdm:legislation_secondary` > `cdm:resource_legal` > `cdm:work` |
| Directive | `cdm:directive` > `cdm:legislation_secondary` > `cdm:resource_legal` > `cdm:work` |
| Judgment | `cdm:judgement` + `cdm:case-law` + `cdm:document_cjeu` > `cdm:resource_legal` > `cdm:work` |
| Proposal | `cdm:act_preparatory` > `cdm:work` (does NOT inherit from `legislation_secondary`!) |

## Field comparison by act type

| Type | Wszystkie fields | Unikalne fields | Shared z innymi |
|---|---|---|---|
| Regulation (REG) | 121 | 16 | 31 |
| Directive (DIR) | 108 | 3 | 31 |
| Judgment (JUDG) | 72 | 38 | 31 |
| Proposal (PROP_DIR) | 74 | 12 | 31 |

### Fields unique to directives (not present on regulations)

- **`directive_date_transposition`** — transposition deadline (key difference!)
- `resource_legal_addresses_institution` → EUMS

### Fields unique to regulations (not present on directives)

`suspends`, `defers_application_of`, `reestablishes`, `incorporates`, `partially_suspends`, `renders_obsolete` — regulations have a richer operational relation vocabulary because they are directly applicable.

### Fields unique to judgments (38 `case-law_*` fields)

A completely separate model: `ecli`, `delivered_by_judge`, `delivered_by_advocate-general`, `court-formation`, `interpretes_resource_legal`, `declares_valid/void`, `originates_in_country`, `procedure_language`, `national-judgement`, `article_journal_related`.

### Fields Unique to Proposals

`proposes_to_amend_resource_legal`, `act_preparatory_initiates_dossier`, `date_dispatch`, `service_responsible`, `work_part_of_dossier`.

---

# DEEP DIVE: OWL annotations and EuroVoc

## Structure of OWL annotations

CELLAR uses **OWL Annotation Axioms** (reification) to qualify relations. Instead of a simple triple `A -> relation -> B`, it creates:

```
_:annotation  owl:annotatedSource   <source_act>
_:annotation  owl:annotatedProperty <cdm:relation>
_:annotation  owl:annotatedTarget   <PSD2>
_:annotation  <qualifier>          <value>
```

## Annotation Types (570 items for PSD2)

| Relation | Count | Description |
|---|---|---|
| `measure_national_implementing_implements` | 258 | Transposition krajowa |
| `work_cites_work` | 233 | Citations |
| `communication_case_new_submits_preliminary_question` | 30 | Preliminary questions |
| `resource_legal_amends` | 13 | Zmiany legislacyjne |
| `case-law_interpretes` | 10 | CJEU interpretations |
| `resource_legal_based_on` | 9 | Acts delegated/implementing |
| `resource_legal_corrects` | 7 | Corrigenda |
| `resource_legal_completes` | 5 | Completing acts |
| `resource_legal_proposes_to_amend` | 2 | Proposals to amend |
| `case-law_declares_valid` | 1 | Confirmation of validity |
| `resource_legal_implicitly_repeals` | 1 | Nojawne repeal |
| `work_related_to_work` | 1 | General related-work link |

## Qualifiers (article-by-article granularity)

| Qualifier | Description | Example |
|---|---|---|
| `annotation:article` | PSD2 article number | `"98"`, `"15"` |
| `annotation:paragraph` | Paragraph | `"4"`, `"5"` |
| `annotation:subparagraph` | Subparagraph | `"2"`, `"3"` |
| `annotation:comment_on_legal_basis` | Encoded location | `"A98P4L2"` |
| `annotation:fragment_cited_target` | Target fragment | `"A24P1"` |
| `annotation:fragment_citing_source` | Source fragment | `"N 53"` |
| `annotation:start_of_validity` | Start of amendment validity | `"2023-01-16"` |
| `annotation:transposition_deadline_transmitted` | Transposition deadline | `"2018-01-13"` |
| `annotation:transposition_notification` | Notification date | `"2019-04-08"` |

### PSD2 articles challenged by national courts

Art. 4(3), 4(5), 4(14), 35(1), 35(2)(b), 52(6)(a), 54(1), 55, 61(1), 62(4), 63(1)(b), 71, 72, 73, 73(1), 74, Annex I(3)(c).

### PSD2 articles serving as the basis for delegated acts

| Delegated act | Article PSD2 | Kod |
|---|---|---|
| RTS SCA (32018R0389) | Art. 98(4) subparagraph 2 | `A98P4L2` |
| Register RTS (32019R0411) | Art. 15(4) subparagraph 3 | `A15P4L3` |
| ITS (32019R0410) | Art. 15(5) subparagraph 3 | `A15P5L3` |
| RTS on cooperation (32017R2055) | Art. 28(5) | `A28P5` |
| RTS pointy konyestowe (32020R1423) | Art. 29(7) | `A29P7` |
| RTS on cross-border supervision (32021R1722) | Art. 29(7) | `A29P7` |

### PSD2 articles amended by DORA and IPR

- **DORA** (32022L2556, from 2023-01-16): Art. 3(j), 5(1), 19(6), 95(1), 96(7), 98(5)
- **IPR** (32024R0886, from 2024-04-08): Art. 35(2), 35(3), 35a

## Hierarchy EuroVoc

PSD2 has 10 EuroVoc descriptors:

```
EU law
  └── approximation of laws (2897)

deepening of the European Union
  └── single market (3299)

free movement of capital
  └── financial legislation (560)

banking
  └── electronic banking (3248)

deposit money
  └── electronic money (1971)

management accounting
  └── payment (2216)

Eurosystem
  └── intra-EU payment (2220)

goods and services
  └── service (4099)

financial institution (1452)  [top-level]
financial services (8469)     [top-level]
```

## Thematically similar legislation (by EuroVoc overlap)

| Overlap | CELEX | Act |
|---|---|---|
| 8/10 | `52023PC0367` | **Proposal PSD3** |
| 7/10 | `32019R0518` | Regulation on cross-border payments |
| 7/10 | `52024AB0013` | ECB opinion o PSD3/PSR |
| 7/10 | `52023AE3611` | EESC opinion o PSD3 |
| 7/10 | `22024D0126` | EEA Decision on including PSD2 in Annex IX |

---

## Existing client tools

- **R**: the [`eurlex`](https://michalovadek.github.io/eurlex/) package with `elx_make_query()`, `elx_run_query()`, and `elx_fetch_data()`. It covers flat lists of acts and basic metadata, but **does not** support navigation through the relation graph (amends, repeals, based_on, etc.).
- **SPARQL editor**: https://op.europa.eu/en/advanced-sparql-query-editor

---

# Legislative summary (Summary) PSD2

## Summary Metadata

| Field | Value |
|---|---|
| **Legissum ID** | `2404020302_1` |
| **CELLAR URI** | `http://publications.europa.eu/resource/cellar/cfa37481-8548-4f70-8d8e-713ac6dfb151` |
| **Type** | `LEGIS_SUM` (Summary of EU Legislation) |
| **Version** | 7.0.1 |
| **Drafted in** | English |
| **Validated by** | DG FISMA |
| **Created** | 2016-06-28 |
| **Last updated** | 2024-11-09 |
| **Obsolete** | No |
| **Classification** | `090406`, `14090302` |
| **Author** | PUBL (Publications Office) |

## Summary language versions (24 languages)

| Language | Title |
|---|---|
| BUL | Ревизирани правила за платежни услуги в ЕС |
| CES | Přepracovaná pravidla pro platební služby v EU |
| DAN | Reviderede regler for betalingstjenester i EU |
| DEU | Überarbeitete Vorschriften für Zahlungsdienste in der EU |
| ELL | Αναθεωρημένοι κανόνες για τις υπηρεσίες πληρωμών στην ΕΕ |
| **ENG** | **Revised rules for payment services in the EU** |
| EST | Läbivaadatud eeskirjad makseteenuste kohta ELis |
| FIN | Maksupalveluja EU:ssa koskevat tarkistetut säännöt |
| FRA | Nouvelles règles relatives aux services de paiement dans l'Union européenne |
| GLE | Rialacha leasaithe le haghaidh seirbhísí íocaíochta in AE |
| HRV | Revidirana pravila za platne usluge u EU-u |
| HUN | Az EU-n belüli pénzforgalmi szolgáltatásokra vonatkozó módosított szabályok |
| ITA | Norme riviste per i servizi di pagamento nell'Unione europea |
| LAV | Pārskatīti noteikumi par maksājumu pakalpojumiem ES |
| LIT | Peržiūrėtos mokėjimo paslaugų ES taisyklės |
| MLT | Regoli riveduti għas-servizzi ta' pagament fl-UE |
| NLD | Herziene voorschriften voor betalingsdiensten in de EU |
| **POL** | **Zmiana przepisów dotyczących usług płatniczych w UE** |
| POR | Regras revistas relativas aos serviços de pagamento na União Europeia |
| RON | Norme revizuite pentru serviciile de plată în UE |
| SLK | Revidované pravidlá platobných služieb v EÚ |
| SLV | Spremenjena pravila za plačilne storitve v EU |
| SPA | Normas revisadas sobre servicios de pago en la Unión Europea |
| SWE | Reviderade regler för betaltjänster i EU |

## Downloading summary content

Summaries have `fmx4` (XML) and `xhtml5` (HTML) manifestations. Downloading them requires the **exact MIME type** `application/xhtml+xml;type=xhtml5`:

```bash
# Fetch the PSD2 summary in HTML (English)
curl -L -H "Accept: application/xhtml+xml;type=xhtml5" \
  "http://publications.europa.eu/resource/cellar/cfa37481-8548-4f70-8d8e-713ac6dfb151.0006.04/DOC_1" \
  -o psd2_summary_en.html
```

**Note**: Standard `Accept: application/xhtml+xml` returns a 406 error. You must use `application/xhtml+xml;type=xhtml5`.

The content (~11,000 characters) includes sections: SUMMARY OF, WHAT IS THE AIM, KEY POINTS, FROM WHEN DOES THE DIRECTIVE APPLY, BACKGROUND, KEY TERMS, MAIN DOCUMENT, RELATED DOCUMENTS.

---

# Legal event (event_legal) PSD2

| Field | Value |
|---|---|
| **Type** | `PUB_OJ` (Official Journal publication) |
| **Date** | 2015-12-23 |
| **Dossier** | `http://publications.europa.eu/resource/cellar/900c24d5-f5ca-11e2-a22e-01aa75ed71a1` (procedure 2013/0264/COD) |
| **Identyfikator** | `procedure-event/2013_264.2015-12-23_PUB_OJ` |
| **Created w systemie** | 2020-08-21 |
| **Ostatnia modyfikacja** | 2025-03-17 |

---

## Sources

- https://op.europa.eu/en/web/cellar/cellar-data
- https://publications.europa.eu/webapi/rdf/sparql
- https://eur-lex.europa.eu/content/help/data-reuse/reuse-contents-eurlex-details.html
- https://michalovadek.github.io/eurlex/
- https://cran.r-project.org/web/packages/eurlex/vignettes/sparql-queries.html
- https://op.europa.eu/en/web/eu-vocabularies/cdm
- https://data.europa.eu/data/datasets/sparql-cellar-of-the-publications-office?locale=en
