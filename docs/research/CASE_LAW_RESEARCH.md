# Case Law in CELLAR — CJEU vs National Courts

## Case-law types in CELLAR

| Type | Count | Description |
|---|---|---|
| **INFO_JUDICIAL** | 69,718 | Judicial information (procedural metadata) |
| **DEC_NC** | 35,773 | **National court judgments** in the EU-law context |
| **DEC_ENTSCHEID** | 33,751 | Decisions (duplicate of JUDG in a different format?) |
| **JUDG** | 33,739 | **CJEU judgments** |
| **SUM_JUR** | 24,443 | Case-law summaries |
| **CASE_LAW** | 15,252 | Case-law reports |
| **OPIN_AG** | 14,360 | **Advocate General opinions** |
| **ORDER** | 8,260 | CJEU orders |

---

## CJEU (JUDG) — data model

Studied using **C-287/19 DenizBank** as the example (a judgment interpreting PSD2).

### Fields Specific to CJEU Judgments

| CDM field | Description | Example |
|---|---|---|
| `case-law_ecli` | ECLI identifier | `ECLI:EU:C:2020:897` |
| `case-law_has_procjur` | Procedure type | `REFER_PREL` (preliminary question) |
| `case-law_delivered_by_court-formation` | Court formation | `CHAMB_01_C` (Chamber I) |
| `case-law_delivered_by_judge` | Judge-rapporteur | (cellar URI) |
| `case-law_delivered_by_advocate-general` | Advocate General | Campos Sánchez-Bordona |
| `case-law_interpretes_resource_legal` | **Which acts it interprets** | PSD2 + Unfair Terms Directive |
| `case-law_declares_valid_resource_legal` | Which acts it considers valid | — |
| `case-law_originates_in_country` | Country of the referring court | AUT (Austria) |
| `case-law_uses_procedure_language` | Language of proceedings | DEU (German) |
| `case-law_commented_by_agent` | Who submitted observations | COM, PRT, CZE |
| `case-law_published_in_erecueil` | Whether in ECR | 1 (yes) |
| `case-law_has_conclusions_opinion_advocate-general` | Link to AG opinion | (cellar URI) |
| `case-law_is_about_concept_new_case-law` | Topical classification | `4.11.12.03` |

### Unique Fields Not Available on Other Types

| Field | Value for monitoring |
|---|---|
| **`case-law_national-judgement`** | National follow-up judgments (with ECLI) |
| **`case-law_article_journal_related`** | Academic articles discussing the judgment |

### Example `case-law_article_journal_related` (C-287/19 DenizBank)

6 scholarly articles registered in CELLAR:

1. Bassani: "Protection des consommateurs - Services de paiement" (Europe 2021)
2. Rodi: "Keine Haftungserleichterung für Bank beim konyestlosen Zahlen" (EWR 2020)
3. Steennot: "Gebruik van NFC-technologie zonder geheime code" (RDCB 2021)
4. Prankl: "Zustimmungsfiktionsklauseln in Zahlungsdienste-Rahmenverträgen" (Ecolex 2021)
5. Hoffmann/Rastegar: "Konyestlose Zahlungen im Privatrecht" (WM 2021)
6. Fornasier: "Die Anwendung der Klauselrichtlinie" (EuZW 2021)

**Finding:** CELLAR stores **references to academic articles** discussing CJEU judgments. This is highly valuable for monitoring because it adds academic context.

### Example `case-law_national-judgement` (C-287/19)

```
*A9* Oberster Gerichtshof, Beschluss vom 25/01/2019 (8 Ob 24/18i)
*P1* Oberster Gerichtshof, Fünfersenat, Urteil vom 25/03/2021
     (ECLI:AT:OGH0002:2021:0080OB00105.20D.0325.000)
```

`*A9*` = referring court, `*P1*` = follow-up judgment after the CJEU answer.

### How to Monitor New CJEU Judgments for a Given Act

```sparql
PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>

# New judgments interpreting PSD2
SELECT ?celex ?ecli ?date ?country WHERE {
  ?work cdm:case-law_interpretes_resource_legal <CELLAR_URI_ACT> .
  ?work cdm:resource_legal_id_celex ?celex .
  ?work cdm:case-law_ecli ?ecli .
  OPTIONAL { ?work cdm:work_date_document ?date }
  OPTIONAL { ?work cdm:case-law_originates_in_country ?country }
}
ORDER BY DESC(?date)
```

```sparql
# New preliminary questions on PSD2
SELECT ?celex ?date ?country WHERE {
  ?work cdm:communication_case_new_submits_preliminary_question_resource_legal <CELLAR_URI_ACT> .
  ?work cdm:resource_legal_id_celex ?celex .
  OPTIONAL { ?work cdm:work_date_document ?date }
  OPTIONAL { ?work cdm:case-law_originates_in_country ?country }
}
ORDER BY DESC(?date)
```

---

## DEC_NC (national courts) — data model

35,773 national court judgments in the context of EU law.

### Geographic distribution (top 15)

| Country | Count | Example courts |
|---|---|---|
| **DEU** (Germany) | 7,815 | BGH, OLG Stuttgart, OLG München, LG Ulm |
| **FRA** (France) | 4,580 | Cour de cassation, Cour d'appel |
| **ITA** (Italy) | 3,642 | — |
| **NLD** (Netherlands) | 3,359 | — |
| **BEL** (Belgium) | 2,874 | — |
| **ESP** (Spain) | 1,979 | — |
| **GBR** (UK) | 1,841 | (pre-Brexit) |
| **AUT** (Austria) | 1,574 | OGH |
| **GRC** (Greece) | 1,062 | — |
| **LUX** (Luxembourg) | 637 | Cour d'appel Luxembourg |
| **PRT** (Portugal) | 630 | — |
| **DNK** (Denmark) | 434 | — |
| **IRL** (Ireland) | 402 | — |
| **SWE** (Sweden) | 392 | — |
| **CZE** (Czechia) | 327 | — |
| **POL** (Poland) | **286** | **Supreme Court** |

### DEC_NC-Specific Fields

| CDM field | Coverage | Description |
|---|---|---|
| `case-law_originates_in_country` | 96% | Country of the court |
| `work_title` | 96% | Identifier (e.g. "OLG Stuttgart; 2021-01-15; 5 U 11/20") |
| `case-law_national_keywords` | 51,278 | Keywords (XML, multilingual) |
| `case-law_article_journal_related` | 33,075 | Academic articles discussing the judgment |
| `resource_legal_uses_originally_language` | 86% | Language of the judgment |
| `case-law_is_about_concept_case-law` | 29,107 | Topical classification |
| `case-law_national_decision_internal_identifier` | 81% | National case number |
| `case-law_national_act_reference_national` | 23,136 | References to national law |
| **`case-law_national_act_reference_european`** | **19,781** | **References to EU law (with article granularity)** |
| `case-law_national_reference_publication` | 19,154 | Where published |
| `case-law_ecli` | var. | ECLI of the national judgment |
| `case-law_national_follow-up` | 8,744 | Follow-up to a CJEU judgment |
| `case-law_national_judgement_reference` | 12,270 | Reference to the CJEU judgment |
| `case-law_national_parties` | var. | Parties (usually anonymized) |

### Format `case-law_national_act_reference_european`

References to EU law with **article-level precision**:

```
32015L2366-A04PT21     → PSD2, Art. 4 point 21
32007L0064-A65P2       → PSD1, Art. 65(2)
32012R0650-A21         → Succession Reg, Art. 21
32016R0679-A17         → GDPR, Art. 17
12016E267-P2           → TFUE, Art. 267(2)
```

Format: `{CELEX}-A{article}P{paragraph}PT{point}L{subparagraph}`

### Example Full DEC_NC Record

**82021DE0115(51)** — OLG Stuttgart, 15.01.2021, 5 U 11/20

| Field | Value |
|---|---|
| ECLI | `ECLI:DE:OLGSTUT:2021:0115.5U11.20.00` |
| Country | Germany |
| Court | OLG Stuttgart (cellar URI) |
| Language | German |
| Topic | COJC (civil justice) |
| National law | BGB §675c(1)(2), §675f(2), §823; GlüStV §4(1) |
| **EU law** | **PSD2 Art. 4 point 21** + 22 other references (CJEU judgments, regulations) |
| Court of first instance | LG Ulm, 16.12.2019, 4 O 202/18 |

### Example Polish DEC_NC

**82025PL0509(51)** — Supreme Court, 09.05.2025, II CSKP 468/23

| Field | Value |
|---|---|
| Country | Poland |
| Court | Supreme Court (cellar URI) |
| Language | Polish |
| National law | Konstytucja RP art. 89-91, 241; KPC art. 13§2, 108§2, 243¹, 328§2, 385, 387§2¹, 391§1, 398³§1 pkt 2, 398¹³§2, 398¹⁵§1 |
| EU law | Reg. 650/2012 (succession) — 11 articles, TFUE art. 288(1) |
| Parties | J. R. (anonymized) |

---

## Comparison JUDG vs DEC_NC

| Aspect | JUDG (CJEU) | DEC_NC (national courts) |
|---|---|---|
| **Count** | 33,739 | 35,773 |
| **Link to EU act** | `case-law_interpretes_resource_legal` (CELLAR URI) | `case-law_national_act_reference_european` (CELEX+article string) |
| **Link strength** | **Strong** — direct URI link | **Weak** — string match, 56% coverage |
| **Scholarly articles** | Yes (6 for DenizBank) | Yes (33k overall) |
| **ECLI** | Always | Often |
| **Classification** | `case-law_is_about_concept_new_case-law` | `case-law_is_about_concept_case-law` |
| **Procedure** | `case-law_has_procjur` (REFER_PREL, etc.) | None |
| **Follow-up** | `case-law_national-judgement` | `case-law_national_follow-up` (8,744) |
| **Country** | `case-law_originates_in_country` (referring country) | `case-law_originates_in_country` (country of the court) |
| **National law** | None | `case-law_national_act_reference_national` (23k) |
| **Monitorability** | **High** | **Medium** (requires string matching on CELEX) |

---

## Search Results: PSD2 in Case Law

### CJEU — 5 judgments + 10 preliminary questions

(Details in CELLAR_API_RESEARCH.md)

### DEC_NC referring to PSD1/PSD2 — 3 judgments

| Date | Country | CELEX | Court | Reference |
|---|---|---|---|---|
| 2019-12-16 | DEU | `82019DE1216(51)` | LG Ulm, 4 O 202/18 | PSD1 Art. 65(2) |
| 2021-01-15 | DEU | `82021DE0115(51)` | OLG Stuttgart, 5 U 11/20 | **PSD2 Art. 4 point 21** |
| 2023-03-07 | LUX | `82023LU0307(51)` | Cour d'appel, 39/23 | PSD1 Art. 59 |

**Note:** The low count (3) follows from the fact that `case-law_national_act_reference_european` is populated for only 56% of DEC_NC records. Many national judgments concerning PSD2 likely exist, but without a tagged reference to the EU act.

### Comparison with GDPR

GDPR (`32016R0679`): 5 DEC_NC with a direct reference. A similar order of magnitude; the problem is data coverage, not lack of judgments.

---

## Advocate General opinions (OPIN_AG)

14,360 in CELLAR. They are linked to CJEU judgments through:
- `case-law_has_conclusions_opinion_advocate-general` (on JUDG -> link to OPIN_AG)
- Shared case number in CELEX (e.g. `62019CC0287` to AG opinion in C-287/19)

### Value for monitoring

AG opinion is published **several months before the judgment**. The CJEU agrees with the AG in ~80% of cases. Therefore:
1. A new OPIN_AG citing your act = **signal of an upcoming judgment**
2. The AG opinion provides clues as to what the CJEU is likely to rule

### How to monitor new AG opinions on a given act

```sparql
PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>

# AG opinions in cases concerning PSD2
SELECT ?agOpinion ?celex ?date WHERE {
  ?judgment cdm:case-law_interpretes_resource_legal <CELLAR_URI_ACT> .
  ?judgment cdm:case-law_has_conclusions_opinion_advocate-general ?agOpinion .
  OPTIONAL { ?agOpinion cdm:resource_legal_id_celex ?celex }
  OPTIONAL { ?agOpinion cdm:work_date_document ?date }
}
ORDER BY DESC(?date)
```

---

## Case-law monitoring strategy

### Layer 1: CJEU (highest certainty)

```
Preliminary question (CN) → AG opinion (CC) → Judgment (CJ)
       ↓                        ↓                  ↓
  Earliest          Predictor           Binding
  signal (2-3 years)      (~80% accuracy)     outcome
```

**Query:** `case-law_interpretes_resource_legal` + `communication_case_new_submits_preliminary_question_resource_legal`

### Layer 2: National courts (lower certainty, broader reach)

```
DEC_NC with case-law_national_act_reference_european CONTAINS '{CELEX}'
```

**Limitations:**
- Only 56% of DEC_NC records have the `european_act_reference` field
- Requires string matching (not a URI link)
- Delay in adding new judgments
- Germany dominates the dataset (22% of all DEC_NC)

### Layer 3: Academic articles (context)

Field `case-law_article_journal_related` on JUDG and DEC_NC provides:
- Article title
- Author
- Journal + year
- Language

Monitoring academic articles about judgments provides additional interpretive context.

---

## SPARQL monitoring patterns

### Comprehensive monitoring of case law for a given act

```sparql
PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>

# All case-law types concerning a given act
SELECT ?celex ?type ?date ?source WHERE {
  {
    # CJEU judgments interpreting
    ?work cdm:case-law_interpretes_resource_legal <CELLAR_URI> .
    BIND('CJEU_interpret' AS ?source)
  } UNION {
    # CJEU confirms validity
    ?work cdm:case-law_declares_valid_resource_legal <CELLAR_URI> .
    BIND('CJEU_valid' AS ?source)
  } UNION {
    # Preliminary questions
    ?work cdm:communication_case_new_submits_preliminary_question_resource_legal <CELLAR_URI> .
    BIND('preliminary_Q' AS ?source)
  }
  ?work cdm:resource_legal_id_celex ?celex .
  ?work cdm:work_has_resource-type ?type .
  OPTIONAL { ?work cdm:work_date_document ?date }
}
ORDER BY DESC(?date)
```

### Monitoring national judgments (DEC_NC)

```sparql
PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>

SELECT ?celex ?country ?date ?title WHERE {
  ?work cdm:work_has_resource-type <http://publications.europa.eu/resource/authority/resource-type/DEC_NC> .
  ?work cdm:case-law_national_act_reference_european ?ref .
  FILTER(CONTAINS(?ref, '32015L2366'))
  ?work cdm:resource_legal_id_celex ?celex .
  OPTIONAL { ?work cdm:case-law_originates_in_country ?country }
  OPTIONAL { ?work cdm:work_date_document ?date }
  OPTIONAL { ?work cdm:work_title ?title }
}
ORDER BY DESC(?date)
```

### New academic articles on judgments concerning a given act

```sparql
PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>

SELECT ?celex ?article WHERE {
  ?work cdm:case-law_interpretes_resource_legal <CELLAR_URI> .
  ?work cdm:resource_legal_id_celex ?celex .
  ?work cdm:case-law_article_journal_related ?article .
}
```

---

## Key findings

1. **The CJEU has strong linking**: `case-law_interpretes_resource_legal` provides a direct URI link to the interpreted act. DEC_NC has weaker linking (a string in `european_act_reference`).

2. **DEC_NC are under-tagged** — only 56% have references to EU law. The actual number of national judgments on PSD2 is likely much higher than 3.

3. **Academic articles in CELLAR**: an unexpected finding. There are 33k article references on DEC_NC plus separate ones on JUDG. This adds academic context.

4. **AG opinions as a predictor** — published months before the judgment, with roughly 80% hit rate. The best early warning for the CJEU outcome.

5. **Three-layer monitoring strategy**: preliminary questions (earliest signal) → AG opinions (predictor) → CJEU judgments (binding) + national judgments (practical application).

6. **DEC_NC with an article reference**: the `{CELEX}-A{art}P{par}PT{pt}` format allows article-by-article monitoring.

7. **Poland: 286 DEC_NC** in CELLAR, mostly from the Supreme Court. The latest is from May 2025.
