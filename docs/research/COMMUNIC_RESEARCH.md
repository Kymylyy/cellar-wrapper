# COMMUNIC — European Commission communications in CELLAR

## What COMMUNIC is

A Commission communication is a **strategic document**: not legally binding, but setting the direction of policy and legislation. There are **19,911** of them in CELLAR.

From a regulatory monitoring perspective, communications are the **earliest signal** of upcoming legislation, typically 2-3 years before a formal proposal.

---

## COMMUNIC properties in CDM

| Field | Description | Example |
|---|---|---|
| `resource_legal_type` | `DC` | Document Commission |
| `work_has_resource-type` | `COMMUNIC` | — |
| `resource_legal_id_sector` | `5` | Acts preparatory |
| `work_created_by_agent` | COM + DG | COM + FISMA |
| `resource_legal_service_responsible` | Responsible DG | FISMA |
| `resource_legal_date_dispatch` | Dispatch date | 2020-09-24 |
| `work_cites_work` | Cited acts | 8-14 acts |
| `work_is_about_concept_eurovoc` | EuroVoc descriptors | 8-10 |
| `resource_legal_eea` | EEA relevance | 0 or 1 |

**Key difference vs legislation:** No `resource_legal_date_entry-into-force`, `in-force`, `addresses_institution`, `based_on_resource_legal`. Communication does not "enter into force" — is a policy signal.

**Manifestations:** docx, pdf, xhtml, just like proposals.

---

## Case Study: Digital Finance package (24 September 2020)

On the same day the Commission published **3 communications + 4 legislative proposals**:

### 3 strategy communications

| CELEX | Title | DG | Cited by |
|---|---|---|---|
| **52020DC0591** | **Digital Finance Strategy for the EU** | FISMA | **41 acts** |
| **52020DC0592** | **Retail Payments Strategy for the EU** | FISMA | **21 acts** |
| **52020DC0590** | **Capital Markets Union for people and businesses** | FISMA | **73+ acts** |

### 4 legislative proposals (the same day!)

| CELEX | Proposal | Status 2026 |
|---|---|---|
| `52020PC0593` | **MiCA** (Markets in Crypto-Assets) | Adopted: `32023R1114` |
| `52020PC0594` | **DLT Pilot Regime** | Adopted: `32022R0858` |
| `52020PC0595` | **DORA** (Digital Operational Resilience) | Adopted: `32022R2554` |
| `52020PC0596` | Companion directive (DORA) | Adopted: `32022L2556` |

---

## Regulatory cascade: Digital Finance Strategy -> legislation

### Communication -> Proposals -> Adopted acts

```
52020DC0591 (Digital Finance Strategy, 2020-09-24)
│
├── THE SAME DAY (2020-09-24):
│   ├── 52020PC0593 → 32023R1114  MiCA (adopted 2023)
│   ├── 52020PC0594 → 32022R0858  DLT Pilot (adopted 2022)
│   ├── 52020PC0595 → 32022R2554  DORA (adopted 2022)
│   └── 52020PC0596 → 32022L2556  DORA companion directive
│
├── 2021 WAVE (CMU + reform):
│   ├── 52021PC0189  Corporate Sustainability Reporting (→ 32022L2464 CSRD)
│   ├── 52021PC0420  AML Regulation
│   ├── 52021PC0723  ESAP (→ 32023R2859)
│   ├── 52021PC0721  AIFMD/UCITS review
│   └── 52021DC0720  CMU update communication
│
├── 2023 WAVE (payments + data):
│   ├── 52023PC0366  PSD3 (directive) — pending
│   ├── 52023PC0367  PSR (regulation) — pending
│   ├── 52023PC0368  Digital Euro services — pending
│   ├── 52023PC0369  Digital Euro establishment — pending
│   └── 52023PC0360  FIDA (Financial Data Access) — pending
│
└── 2025 WAVE:
    ├── 52025PC0942  AIFMD/UCITS/Solvency II amendments
    └── 52025PC0943  CCP/ESMA amendments
```

### Time from strategy to legislation

| Proposal | Months since communication | Status |
|---|---|---|
| MiCA | 0 (the same day) | **Adopted** 2023 |
| DLT Pilot | 0 | **Adopted** 2022 |
| DORA | 0 | **Adopted** 2022 |
| ESAP | 14 months | **Adopted** 2023 |
| PSD3/PSR | 33 months | **In trilogue** |
| Digital Euro | 33 months | **Pending** |
| FIDA | 33 months | **Pending** |

---

## Cascade: Retail Payments Strategy -> legislation

```
52020DC0592 (Retail Payments Strategy, 2020-09-24)
│
├── 2020: Decision on the Payment Systems Market Expert Group
├── 2021: Communication on the European financial system
├── 2022: Instant Payments proposal (52022PC0546 → 32024R0886)
├── 2023-06-28: PAYMENTS PACKAGE
│   ├── 52023PC0366  PSD3 — pending
│   ├── 52023PC0367  PSR — pending
│   ├── 52023PC0369  Digital Euro (services) — pending
│   └── 52023DC0365  Review report PSD2
├── 2024: EP positions (52024AP0297, 52024AP0298)
└── Case law: AG opinion Campos Sánchez-Bordona (62022CC0661)
```

---

## Cascade: Capital Markets Union -> legislation

```
52020DC0590 (CMU, 2020-09-24)
│
├── 73+ citing acts: the broadest reach
├── Spawned legislation in the areas of:
│   ├── Corporate sustainability (CSRD, CSDDD)
│   ├── Listing Act (2024R1623)
│   ├── ESAP (2023R2859)
│   ├── AIFMD/UCITS review
│   ├── European Green Bond Standard
│   ├── Retail Investment Strategy
│   ├── Clearing/settlement reform
│   └── AML package
└── Latest citing act: 52025DC0940 (December 2025)
```

---

## Case Study: FIDA (Financial Data Access)

| Field | Value |
|---|---|
| **CELEX** | `52023PC0360` |
| **Type** | PROP_REG |
| **Date** | 2023-06-28 |
| **DG** | FISMA |
| **Full title** | Proposal for a REGULATION on a framework for Financial Data Access and amending Regulations (EU) No 1093/2010, (EU) No 1094/2010, (EU) No 1095/2010 and (EU) 2023/2854 |

### EuroVoc FIDA (10 descriptors)

| Concept | Label |
|---|---|
| `eurovoc:453` | access to information |
| `eurovoc:5334` | disclosure of information |
| `eurovoc:616` | exchange of information |
| `eurovoc:1452` | financial institution |
| `eurovoc:5181` | data protection |
| `eurovoc:5595` | personal data |
| `eurovoc:8469` | financial services |
| `eurovoc:560` | financial legislation |
| `eurovoc:4366` | information service |
| `eurovoc:c_eaccd9f4` | **data sharing** |

### FIDA cites 53 acts

Key items: Digital Finance Strategy (52020DC0591), PSD2, GDPR, eIDAS, MiFID II, Solvency II, AIFMD, IDD, CRD IV, CRR, DORA, MiCA, Data Act.

### Related documents (`work_related_to_work`)

| CELEX | Act |
|---|---|
| `52023PC0278` | Proposal amending the PRIIPs Regulation (KID modernization) |
| `52023PC0279` | Proposal amending UCITS, Solvency II, AIFMD, MiFID II, and IDD directives (Retail Investment Strategy) |

**Finding:** FIDA is part of the **broader package of 28 June 2023**, which besides PSR/PSD3 also includes the Retail Investment Strategy.

---

## EuroVoc — comparison of three communications

| EuroVoc | Digital Finance | Retail Payments | CMU |
|---|---|---|---|
| innovation | YES | - | - |
| new technology | YES | - | - |
| digital technology | YES | - | - |
| digital economy | YES | - | - |
| digital single market | YES | - | - |
| EU strategy | YES | YES | - |
| financial services | YES | - | - |
| electronic money | YES | YES | - |
| electronic banking | YES | YES | - |
| payment system | YES | YES | - |
| intra-EU payment | - | YES | - |
| international payment | - | YES | - |
| retail trade | - | YES | - |
| consumer protection | - | YES | - |
| paper money | - | YES | - |
| single market | - | - | YES |
| financial market | - | - | YES |
| capital market | - | - | YES |
| securities | - | - | YES |
| stock exchange | - | - | YES |
| sustainable finance | - | - | YES |
| financial supervision | - | - | YES |
| small and medium enterprises | - | - | YES |

**Conclusion:** The three communications have **almost zero EuroVoc overlap**: each covers a different segment of the financial market. Together they form a complete thematic map of the reforms.

---

## Value of COMMUNIC for regulatory monitoring

### 1. Earliest signal (Early Warning)

A communication appears **2-3 years** before the legislative proposal. The Digital Finance Strategy (September 2020) foreshadowed MiCA, DORA, PSR, and FIDA, all tabled in 2022-2023.

### 2. Tracking the citation chain (Citation Chain)

```sparql
# Find all proposals spawned by a communication
PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>
SELECT ?celex ?type ?date ?title WHERE {
  ?work cdm:work_cites_work <COMMUNICATION_CELLAR_URI> .
  ?work cdm:work_has_resource-type ?type .
  FILTER(
    ?type = <http://publications.europa.eu/resource/authority/resource-type/PROP_REG> ||
    ?type = <http://publications.europa.eu/resource/authority/resource-type/PROP_DIR>
  )
  ?work cdm:resource_legal_id_celex ?celex .
  OPTIONAL { ?work cdm:work_date_document ?date }
  OPTIONAL {
    ?expr cdm:expression_belongs_to_work ?work .
    ?expr cdm:expression_uses_language <http://publications.europa.eu/resource/authority/language/ENG> .
    ?expr cdm:expression_title ?title .
  }
} ORDER BY ?date
```

### 3. Mapping EuroVoc to upcoming legislation

A communication plus EuroVoc makes it possible to identify **which topics** will be regulated before concrete proposals appear.

### 4. Identification of legislative packages

One communication -> many proposals. DFS -> MiCA + DORA + DLT Pilot (the same day) + PSR + PSD3 + FIDA + Digital Euro (3 years later).

### 5. Responsible DG as a signal

`resource_legal_service_responsible: FISMA` on the communication = legislation concerning the financial sector.

---

## Monitoring patterns

### New communications in the financial domain

```sparql
PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>
SELECT ?celex ?date ?title WHERE {
  ?work cdm:work_has_resource-type <http://publications.europa.eu/resource/authority/resource-type/COMMUNIC> .
  ?work cdm:resource_legal_service_responsible 'FISMA' .
  ?work cdm:resource_legal_id_celex ?celex .
  ?work cdm:work_date_document ?date .
  OPTIONAL {
    ?expr cdm:expression_belongs_to_work ?work .
    ?expr cdm:expression_uses_language <http://publications.europa.eu/resource/authority/language/ENG> .
    ?expr cdm:expression_title ?title .
  }
  FILTER(?date > '2025-01-01'^^xsd:date)
} ORDER BY DESC(?date)
```

### How many proposals a given communication spawned

```sparql
PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>
SELECT ?commCelex (COUNT(DISTINCT ?prop) as ?proposals) WHERE {
  ?comm cdm:work_has_resource-type <http://publications.europa.eu/resource/authority/resource-type/COMMUNIC> .
  ?comm cdm:resource_legal_id_celex ?commCelex .
  ?prop cdm:work_cites_work ?comm .
  ?prop cdm:work_has_resource-type ?type .
  FILTER(
    ?type = <http://publications.europa.eu/resource/authority/resource-type/PROP_REG> ||
    ?type = <http://publications.europa.eu/resource/authority/resource-type/PROP_DIR>
  )
} GROUP BY ?commCelex ORDER BY DESC(?proposals) LIMIT 20
```

---

## Comparison of COMMUNIC vs other studied types

| Aspect | COMMUNIC | DIR | REG | PROP_REG |
|---|---|---|---|---|
| Legally binding | **No** | Yes | Yes | No (not yet) |
| EuroVoc | Yes | Yes | Yes | Yes |
| Cited by legislation | **Yes (key!)** | Yes | Yes | Rarely |
| Dossier | No | Yes | Yes | Yes |
| Case law | No | Yes | Yes | No |
| NIMs | No | Yes | No | No |
| RTS/ITS | No | Yes | Yes | No |
| In-force status | No (N/A) | Yes | Yes | No |
| Legislation prediction | **Yes (2-3 years)** | N/A | N/A | Yes (1-2 years) |
