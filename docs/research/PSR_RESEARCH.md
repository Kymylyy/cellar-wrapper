# PSR — Proposal for a Regulation COM(2023) 367: CELLAR research report

## Identification

| Field | Value |
|---|---|
| **CELEX** | `52023PC0367` |
| **CELLAR URI** | `http://publications.europa.eu/resource/cellar/04cc5bd5-196f-11ee-806b-01aa75ed71a1` |
| **COM** | COM(2023) 367 final |
| **IMMC** | COM(2023)367 final |
| **Type** | `PROP_REG` (Regulation proposal) |
| **Sector CELEX** | 5 (acts preparatory) |
| **Version** | final |
| **EEA** | Yes |
| **Repertoire** | REP |

**Full title:** Proposal for a REGULATION OF THE EUROPEAN PARLIAMENT AND OF THE COUNCIL on payment services in the internal market and amending Regulation (EU) No 1093/2010

**RDF classes:** `cdm:act_preparatory` > `cdm:work` (NOT `legislation_secondary` — this is a proposal, not adopted legislation)

---

## Dates

| Field | Value |
|---|---|
| Document date | 2023-06-28 |
| Dispatch date (dispatch) | 2023-06-28 |
| Publication date (legacy) | 2023-07-03 |
| End of validity | 9999-12-31 (indefinitely — active proposal) |
| Created in CELLAR | 2023-07-03 |
| Last modified | 2023-09-07 |

**Note:** No `resource_legal_date_entry-into-force` or `directive_date_transposition`: this is a proposal, not an adopted act.

---

## Institutions

| Role | Entity |
|---|---|
| Authors (`work_created_by_agent`) | COM (European Commission), FISMA (DG for Financial Stability) |
| Responsible service | FISMA |

**None:** `resource_legal_responsibility_of_agent`, `resource_legal_addresses_institution` — those fields exist only on adopted legislation.

---

## Legal basis

| Field | Value |
|---|---|
| Treaty | TFEU 2016 (Treaty on the Functioning of the European Union) |
| Article | **12016E114** — Art. 114 TFEU (internal-market harmonization) |

---

## Subject matter

### Subject-matter (3 concepts)
- **LCC** — Free movement of capital
- **LES** — Freedom of establishment
- **MARI** — Internal market — Principles

### Directory codes (2)
- `1040` — Free movement of capital
- `06202020` — Banks

### EuroVoc (9 descriptors)

| Concept | Label EN |
|---|---|
| `eurovoc:1971` | electronic money |
| `eurovoc:1452` | financial institution |
| `eurovoc:560` | financial legislation |
| `eurovoc:8469` | financial services |
| `eurovoc:2220` | intra-EU payment |
| `eurovoc:2216` | payment |
| `eurovoc:c_e749c083` | **payment system** (new, not present in PSD2) |
| `eurovoc:2602` | **provision of services** (new, not present in PSD2) |
| `eurovoc:3299` | single market |

---

## EuroVoc hierarchy

```
deposit money (1975)
  └── electronic money (1971)

free movement of capital (1630)
  └── financial legislation (560)

Eurosystem (c_d1f03d01)
  └── intra-EU payment (2220)

management accounting (1155)
  └── payment (2216)

financial transaction (4491) > financial market (1804)
  └── payment system (c_e749c083)

commercial transaction (5268)
  └── provision of services (2602)

deepening of the European Union (5442)
  └── single market (3299)

financial institution (1452)    [top-level]
financial services (8469)       [top-level]
```

---

## EuroVoc comparison: PSR vs PSD2

| EuroVoc | PSR | PSD2 |
|---|---|---|
| approximation of laws | - | **YES** |
| electronic banking | - | **YES** |
| electronic money | YES | YES |
| financial institution | YES | YES |
| financial legislation | YES | YES |
| financial services | YES | YES |
| intra-EU payment | YES | YES |
| payment | YES | YES |
| payment system | **YES** | - |
| provision of services | **YES** | - |
| service | - | **YES** |
| single market | YES | YES |

**Shared:** 7 descriptors. Key differences:
- PSD2 has `approximation of laws` (a directive harmonising national law); PSR does not (it is a directly applicable regulation).
- PSD2 has `electronic banking` — PSR does not (PSR has a narrower focus on payment systems)
- PSR adds `payment system` — reflecting the broader infrastructure scope (open banking, data access)
- PSR adds `provision of services` instead of the more general `service` used in PSD2

---

## Language versions (Expressions)

24 languages (full EU set). Formats for each language version:
- `docx` — Word
- `pdf` — PDF
- `xhtml` — HTML

**Total:** 72 manifestations (3 formats × 24 languages)

---

## Outgoing relations (PSR -> others)

### PSR proposes amending 2 regulations

| CELEX | Act |
|---|---|
| `32010R1093` | Regulation (EU) No 1093/2010 — **EBA Regulation** (European Banking Authority) |
| `32017R2394` | Regulation (EU) 2017/2394 — **CPC Regulation** (consumer protection cooperation) |

### PSR does not repeal any act

The repeal of PSD2 sits on the companion PSD3 directive (52023PC0366).

### Related documents (`work_related_to_work`)

| CELEX | Act |
|---|---|
| `52023DC0365` | Commission communication accompanying the PSR/PSD3 package |
| `52023PC0366` | **Proposal PSD3** — companion directive |

### PSR cites 43 acts (`work_cites_work`)

**Treaties:**
- TFEU (full text, Arts. 26, 290), TEU (Art. 5), Charter of Fundamental Rights

**Directives (15):**
- PSD1 (32007L0064), **PSD2 (32015L2366)**, EMD2 (32009L0110)
- CRD IV (32013L0036), Settlement Finality (31998L0026), FICOD (32002L0087)
- Consumer Credit (32008L0048), PAD (32014L0092), ePrivacy (32002L0058)
- ADR (32013L0011), Accounting (32013L0034), DGSD (32014L0049)
- EECC (32018L1972), European Accessibility Act (32019L0882), Representative Actions (32020L1828)

**Regulations (16):**
- **GDPR (32016R0679)**, eIDAS (32014R0910), SEPA (32012R0260)
- CRR (32013R0575), SSM (32013R1024), IFR (32015R0751)
- Rome I (32008R0593), **DORA (32022R2554)**, **MiCA (32023R1114)**
- Cross-border payments (32021R1230), SCA RTS (32018R0389)
- Data protection EU institutions (32018R1725)

**Preparatory documents (5):**
- Digital Finance Strategy (52020DC0591), Retail Payments Strategy (52020DC0592)
- Financial system resilience (52021DC0032), Data Act proposal (52022PC0068)
- Instant credit transfers (52022PC0546)

---

## Incoming relations (others -> PSR)

### Quantitative Overview

| Relation | Count | Description |
|---|---|---|
| `expression_belongs_to_work` | 24 | Language versions of PSR itself |
| `owl:annotatedSource` | 6 | OWL annotations (PSR as source) |
| `owl:annotatedTarget` | 6 | OWL annotations (PSR as target) |
| `work_cites_work` | 5 | Acts citing PSR |
| `resource_legal_influences_resource_legal` | 3 | Opinions influencing PSR |
| `dossier_contains_work` | 2 | PSR in 2 dossiers |
| `resource_legal_contains_eesc_opinion_on_resource_legal` | 2 | EESC opinions |
| `work_related_to_work` | 2 | Related SWD documents |
| `dossier_initiated_by_act_preparatory` | 1 | PSR initiates the dossier |
| `resource_legal_contains_ep_opinion_on_resource_legal` | 1 | EP position |
| `event_legal_contains_work` | 1 | Legal event |

### Who cites PSR (5 acts)

| CELEX | Type | Description |
|---|---|---|
| `52023PC0369` | PROP_DIR | Proposal for a digital euro services directive — cites PSR as context |
| `52023DC0715` | Communication | Commission communication on skills and talent mobility |
| `52025DC0708` | Report | Commission report on Article 33 DSA — interaction with other acts |
| `52025SC0368` | SWD | Staff working document accompanying the DSA report |
| `52025PC0941` | PROP_REG | **Settlement regulation proposal (Settlement Finality, 2025)** — cites PSR |

### Institutional opinions concerning PSR

| CELEX | Institution | Date | Description |
|---|---|---|---|
| `52023AE3611` | **EESC** | 2023-12-14 | EESC opinion on the FIDA+PSD3+PSR package |
| `52024AB0013` | **ECB** | 2024-04-30 | ECB opinion CON/2024/13 on PSR+PSD3 |
| `52023XX01019` | **EDPS** | 2023-11-16 | Summary of the EDPS opinion on PSR+PSD3 |
| `52024AP0298` | **EP** | 2024-04-23 | EP position at first reading |

---

## Legislative procedure — Dossier 2023/0210(COD)

### Dossier metadata

| Field | Value |
|---|---|
| Procedure | **2023/0210(COD)** — OLP (ordinary legislative procedure) |
| EU competence | Shared (`SHARED`) |
| Status: adopted | **false** |
| Status: pending | **true** |
| Status: withdrawn | **false** |
| Initiator | PSR (52023PC0367) |
| EP rapporteur | **Marek Belka** (ECON committee) |
| Previous dossier | Planning workflow from 2022-09-05 ("Payment services – revision of EU rules") |
| Last modified | **2025-11-25** |

### Procedural Timeline

| Date | Event |
|---|---|
| 2022-09 | The Commission opens a planning dossier (PSD2 review) |
| **2023-06-28** | The Commission adopts PSR proposal COM(2023)367 + PSD3 COM(2023)366 |
| 2023-07-05 | Transmission to the Council (cover notes) |
| 2023-11-13 | Draft ECON committee report in the EP (rapporteur: Belka) |
| 2023-11-16 | EDPS opinion on PSR+PSD3 |
| 2023-12-14 | EESC opinion on the FIDA+PSD3+PSR package |
| 2024-02-22 | ECON committee report adopted by EP |
| **2024-04-23** | **EP — first reading: P9_TA(2024)0298** (PSR) and P9_TA(2024)0297 (PSD3) |
| 2024-04-30 | ECB opinion CON/2024/13 |
| 2024-07-02 | Council note on EP first reading outcomes |
| **2025-06-13** | **The Council adopts the negotiating mandate (general approach) for PSR and PSD3** |
| 2025-09-17 | EP position published in OJ C/2025/3725 |
| **2025-11 →** | **Trilogue ongoing** |
| **2026-02** (now) | Status: **pending, not adopted, not withdrawn** |

### Documents in the dossier (26 items)

| Date | CELEX | Type | Description |
|---|---|---|---|
| 2023-06-28 | **52023PC0367** | PROP_REG | **Proposal PSR** |
| 2023-06-28 | 52023SC0232 | IMPACT_ASSESS_SUM | Impact assessment summary |
| 2023-06-28 | 52023SC0231 | IMPACT_ASSESS | Full impact assessment |
| 2023-06-28 | _(none)_ | OPIN_IMPACT_ASSESS | Regulatory Scrutiny Board opinion |
| 2023-07-05 | _(none)_ | NOTE_COVER | Council cover notes (5 items) |
| 2023-11-13 | _(none)_ | REPORT_DRAFT_EP_CMT | Draft ECON report |
| 2023-11-16 | 52023XX01019 | SUM | EDPS opinion |
| 2023-12-14 | 52023AE3611 | OPIN | EESC opinion |
| 2024-02-22 | _(none)_ | REPORT_EP | ECON committee report |
| **2024-04-23** | **52024AP0298** | **RES_LEGIS** | **EP position (first reading)** |
| 2024-04-23 | _(none)_ | ADOPT_TEXT | Adopted text |
| 2024-04-23 | _(none)_ | PLENARY_MINUTES_EP | Plenary minutes |
| 2024-04-30 | 52024AB0013 | OPIN | ECB opinion |
| 2024-07-02 | _(none)_ | NOTE_INFO | Council information note |
| **2025-06-13** | _(none)_ | NOTE | **Council negotiating mandate (PSR)** |
| **2025-06-13** | _(none)_ | NOTE | **Council negotiating mandate (PSD3)** |
| **2025-06-13** | _(none)_ | ITEM_I_NOTE | Item I: PSD+PSR package |
| 2025-06-18..27 | _(none)_ | AGENDA_DRAFT_CONSIL | COREPER II agenda drafts (4 items) |

---

## PSR + PSD3 legislative package

PSR and PSD3 are **two separate dossiers**, but they are treated as **one package**:

| | PSR (Regulation) | PSD3 (Directive) |
|---|---|---|
| **CELEX** | 52023PC0367 | 52023PC0366 |
| **Procedure** | 2023/0210(COD) | 2023/0209(COD) |
| **Status** | Pending | Pending |
| **EP rapporteur** | Marek Belka | Ondrej Kovarik |
| **EP vote** | 52024AP0298 (23.04.2024) | 52024AP0297 (23.04.2024) |
| **Council mandate** | 13.06.2025 | 13.06.2025 |
| **What it amends** | EBA Reg (32010R1093), CPC Reg (32017R2394) | — (new act) |
| **Repeals** | Nothing | PSD2 (32015L2366) + EMD2 (32009L0110) |

**Shared documents:**
- Impact assessment: 52023SC0231 + 52023SC0232
- EESC opinion: 52023AE3611
- ECB opinion: 52024AB0013
- Council mandate: both adopted on 13.06.2025

---

## OWL annotations (12 items: 6 source + 6 target)

### PSR as Source (6)

| Relation | Target | Qualifier |
|---|---|---|
| `resource_legal_proposes_to_amend` | 32010R1093 (EBA) | `type_of_link_target = EA` |
| `resource_legal_proposes_to_amend` | 32017R2394 (CPC) | `type_of_link_target = EA` |
| `work_related_to_work` | 52023DC0365 (Communication) | `type_of_link_target = RD` |
| `work_related_to_work` | 52023PC0366 (PSD3) | `type_of_link_target = RD` |
| `resource_legal_date_dispatch` | 2023-06-28 | `comment_on_date = TRANS/CONS` (-> Council) |
| `resource_legal_date_dispatch` | 2023-06-28 | `comment_on_date = TRANS/PARL` (-> EP) |

### PSR as Target (6)

| Relation | Source | Qualifier |
|---|---|---|
| `resource_legal_influences` | 52023XX01019 (EDPS opinion) | `type_of_link_target = EA` |
| `resource_legal_influences` | 52024AB0013 (ECB opinion) | `type_of_link_target = EA` |
| `work_related_to_work` | 52023SC0231 (SWD) | `type_of_link_target = RD` |
| `work_related_to_work` | 52023SC0232 (SWD) | `type_of_link_target = RD` |
| `contains_eesc_opinion_on` | 52023AE3611 (EESC) | `type_of_link_target = EA` |
| `contains_ep_opinion_on` | 52024AP0298 (EP) | `type_of_link_target = EA`, `role2 = MD` |

**The qualifier `role2 = MD`** on the EP position means "Main Document" — marking it as the EP's main decision document in the procedure.

---

## Legislation with the Highest EuroVoc Overlap with PSR

| Overlap | CELEX | Act |
|---|---|---|
| **9/9** | 52024AB0013 | ECB opinion o PSR |
| **9/9** | 52024AP0298 | EP position o PSR |
| 8/9 | 52023XX01019 | EDPS opinion |
| 8/9 | 52023AE3611 | EESC opinion |
| **7/9** | **32015L2366** | **PSD2** |
| 7/9 | 52024AP0297 | EP position o PSD3 |
| 7/9 | 52023PC0366 | PSD3 proposal |
| 7/9 | 32019R0518 | Cross-border payments regulation |
| 7/9 | 52023SC0231, 52023SC0232 | SWD (impact assessments) |

---

## Comparison PSR vs PSD2 vs DORA

| Aspect | PSR (Proposal REG) | PSD2 (Directive) | DORA (Regulation) |
|---|---|---|---|
| CELEX | 52023PC0367 | 32015L2366 | 32022R2554 |
| Type | PROP_REG | DIR | REG |
| Status | **Pending (trilogue)** | In-force (until 2026-06-18) | In-force |
| Sector CELEX | 5 (preparatory) | 3 (adopted) | 3 (adopted) |
| Date | 2023-06-28 | 2015-11-25 | 2022-12-14 |
| Basis | Art. 114 TFEU | Art. 114 TFEU | Art. 114 TFEU |
| Cites acts | 43 | 31 | 38+ |
| Cited by | 5 | 283 | 64 |
| NIM (transposition) | 0 (proposal) | 258 | 0 (regulation) |
| CJEU case law | 0 | 5 judgments + 10 questions | 0 |
| Acts delegated / implementing | 0 (proposal) | 9 (RTS+ITS) | 12 (RTS+ITS) |
| Adnotacje OWL | 12 | 570+ | 74 |
| EuroVoc descriptors | 9 | 10 | 9 |
| EuroVoc overlap with PSD2 | 7/9 | — | 1/9 (`financial services`) |
| Companion | PSD3 (52023PC0366) | None | Dir 2022/2556 |
| Amends | EBA Reg, CPC Reg | EMD2, Commercial Agents, CRD IV, EBA Reg | CRA, EMIR, MiFIR, CSDR, Benchmarks |
| Repeals | Nothing (PSD3 repeals PSD2) | PSD1 | Nothing |

---

## Key findings

1. **PSR is in trilogueue** — the EP adopted its position 23.04.2024, the Council adopted its negotiating mandate 13.06.2025, the procedure is active (ostatnia aktualizacja dossier: 25.11.2025).

2. **Dual dossier structure** — PSR is in 2 dossiers: internal Commission (adoption workflow) and an interinstitutional one (2023/0210/COD). This is the standard pattern.

3. **PSR+PSD3 package** — separate procedures (0210/COD i 0209/COD), ale shared: impact assessment, EESC opinion, ECB opinion, Council mandates adopted on the same day.

4. **Predecessor dossier from 2022** — Commission planning dossier z September 2022 confirms that PSR grew out of the PSD2 review.

5. **EuroVoc confirms the regulation character** — none `approximation of laws` (present in PSD2), which semantically reflects the fact that a regulation is directly applicable (it does not harmonise national law).

6. **PSR expands the EBA scope** — amending Regulation 1093/2010 (EBA) expands EBA supervisory competences in payment services.

7. **New descriptor `payment system`** — PSR introduces a focus on payment-system infrastructure and open banking, which PSD2 did not have.

8. **Proposal as an act type in CELLAR** — absence of many fields typical of adopted legislation: `date_entry-into-force`, `addresses_institution`, `in-force`, `directive_date_transposition`. The RDF class is `act_preparatory`, not `legislation_secondary`.
