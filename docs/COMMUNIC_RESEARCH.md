# COMMUNIC — Komunikaty Komisji Europejskiej w CELLAR

## Czym jest COMMUNIC

Komunikat (Communication) Komisji Europejskiej to **dokument strategiczny** — nie wiążący prawnie, ale wyznaczający kierunek polityki i legislacji. W CELLAR jest ich **19 911**.

Z perspektywy monitoringu regulacyjnego komunikaty są **najwcześniejszym sygnałem** nadchodzącej legislacji — zazwyczaj 2-3 lata przed formalną propozycją.

---

## Właściwości COMMUNIC w CDM

| Pole | Opis | Przykład |
|---|---|---|
| `resource_legal_type` | `DC` | Document Commission |
| `work_has_resource-type` | `COMMUNIC` | — |
| `resource_legal_id_sector` | `5` | Akty przygotowawcze |
| `work_created_by_agent` | COM + DG | COM + FISMA |
| `resource_legal_service_responsible` | DG odpowiedzialne | FISMA |
| `resource_legal_date_dispatch` | Data wysłania | 2020-09-24 |
| `work_cites_work` | Cytowane akty | 8-14 aktów |
| `work_is_about_concept_eurovoc` | Deskryptory EuroVoc | 8-10 |
| `resource_legal_eea` | EEA relevance | 0 lub 1 |

**Kluczowa różnica vs legislacja:** Brak `resource_legal_date_entry-into-force`, `in-force`, `addresses_institution`, `based_on_resource_legal`. Komunikat nie "wchodzi w życie" — jest sygnałem politycznym.

**Manifestacje:** docx, pdf, xhtml — jak propozycje.

---

## Case Study: Pakiet Digital Finance (24 września 2020)

Tego samego dnia Komisja opublikowała **3 komunikaty + 4 propozycje legislacyjne**:

### 3 komunikaty-strategie

| CELEX | Tytuł | DG | Cytowany przez |
|---|---|---|---|
| **52020DC0591** | **Digital Finance Strategy for the EU** | FISMA | **41 aktów** |
| **52020DC0592** | **Retail Payments Strategy for the EU** | FISMA | **21 aktów** |
| **52020DC0590** | **Capital Markets Union for people and businesses** | FISMA | **73+ aktów** |

### 4 propozycje legislacyjne (tego samego dnia!)

| CELEX | Propozycja | Status 2026 |
|---|---|---|
| `52020PC0593` | **MiCA** (Markets in Crypto-Assets) | Przyjęty: `32023R1114` |
| `52020PC0594` | **DLT Pilot Regime** | Przyjęty: `32022R0858` |
| `52020PC0595` | **DORA** (Digital Operational Resilience) | Przyjęty: `32022R2554` |
| `52020PC0596` | Companion directive (DORA) | Przyjęta: `32022L2556` |

---

## Kaskada regulacyjna: Digital Finance Strategy → Legislacja

### Komunikat → Propozycje → Przyjęte akty

```
52020DC0591 (Digital Finance Strategy, 2020-09-24)
│
├── TEGO SAMEGO DNIA (2020-09-24):
│   ├── 52020PC0593 → 32023R1114  MiCA (przyjęty 2023)
│   ├── 52020PC0594 → 32022R0858  DLT Pilot (przyjęty 2022)
│   ├── 52020PC0595 → 32022R2554  DORA (przyjęty 2022)
│   └── 52020PC0596 → 32022L2556  DORA companion directive
│
├── FALA 2021 (CMU + reform):
│   ├── 52021PC0189  Corporate Sustainability Reporting (→ 32022L2464 CSRD)
│   ├── 52021PC0420  AML Regulation
│   ├── 52021PC0723  ESAP (→ 32023R2859)
│   ├── 52021PC0721  AIFMD/UCITS review
│   └── 52021DC0720  CMU update communication
│
├── FALA 2023 (payments + data):
│   ├── 52023PC0366  PSD3 (dyrektywa) — pending
│   ├── 52023PC0367  PSR (rozporządzenie) — pending
│   ├── 52023PC0368  Digital Euro services — pending
│   ├── 52023PC0369  Digital Euro establishment — pending
│   └── 52023PC0360  FIDA (Financial Data Access) — pending
│
└── FALA 2025:
    ├── 52025PC0942  AIFMD/UCITS/Solvency II amendments
    └── 52025PC0943  CCP/ESMA amendments
```

### Czas od strategii do legislacji

| Propozycja | Miesiące od komunikatu | Status |
|---|---|---|
| MiCA | 0 (tego samego dnia) | **Przyjęty** 2023 |
| DLT Pilot | 0 | **Przyjęty** 2022 |
| DORA | 0 | **Przyjęty** 2022 |
| ESAP | 14 mies. | **Przyjęty** 2023 |
| PSD3/PSR | 33 mies. | **W trilogu** |
| Digital Euro | 33 mies. | **Pending** |
| FIDA | 33 mies. | **Pending** |

---

## Kaskada: Retail Payments Strategy → Legislacja

```
52020DC0592 (Retail Payments Strategy, 2020-09-24)
│
├── 2020: Decyzja o Payment Systems Market Expert Group
├── 2021: Komunikat o europejskim systemie finansowym
├── 2022: Propozycja Instant Payments (52022PC0546 → 32024R0886)
├── 2023-06-28: PAKIET PŁATNICZY
│   ├── 52023PC0366  PSD3 — pending
│   ├── 52023PC0367  PSR — pending
│   ├── 52023PC0369  Digital Euro (services) — pending
│   └── 52023DC0365  Raport z przeglądu PSD2
├── 2024: EP stanowiska (52024AP0297, 52024AP0298)
└── Case law: Opinia AG Campos Sánchez-Bordona (62022CC0661)
```

---

## Kaskada: Capital Markets Union → Legislacja

```
52020DC0590 (CMU, 2020-09-24)
│
├── 73+ cytujących aktów — NAJWIĘKSZY zasięg
├── Spawned legislację w obszarach:
│   ├── Corporate sustainability (CSRD, CSDDD)
│   ├── Listing Act (2024R1623)
│   ├── ESAP (2023R2859)
│   ├── AIFMD/UCITS review
│   ├── European Green Bond Standard
│   ├── Retail Investment Strategy
│   ├── Clearing/settlement reform
│   └── AML package
└── Ostatni cytujący: 52025DC0940 (grudzień 2025)
```

---

## Case Study: FIDA (Financial Data Access)

| Pole | Wartość |
|---|---|
| **CELEX** | `52023PC0360` |
| **Typ** | PROP_REG |
| **Data** | 2023-06-28 |
| **DG** | FISMA |
| **Pełny tytuł** | Proposal for a REGULATION on a framework for Financial Data Access and amending Regulations (EU) No 1093/2010, (EU) No 1094/2010, (EU) No 1095/2010 and (EU) 2023/2854 |

### EuroVoc FIDA (10 deskryptorów)

| Koncept | Label |
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

### FIDA cytuje 53 akty

Kluczowe: Digital Finance Strategy (52020DC0591), PSD2, GDPR, eIDAS, MiFID II, Solvency II, AIFMD, IDD, CRD IV, CRR, DORA, MiCA, Data Act.

### Powiązane dokumenty (`work_related_to_work`)

| CELEX | Akt |
|---|---|
| `52023PC0278` | Propozycja zmiany Reg. PRIIPs (KID modernization) |
| `52023PC0279` | Propozycja zmiany dyrektyw UCITS, Solvency II, AIFMD, MiFID II, IDD (Retail Investment Strategy) |

**Odkrycie:** FIDA jest częścią **szerszego pakietu z 28 czerwca 2023**, który oprócz PSR/PSD3 obejmuje też Retail Investment Strategy.

---

## EuroVoc — porównanie trzech komunikatów

| EuroVoc | Digital Finance | Retail Payments | CMU |
|---|---|---|---|
| innovation | TAK | - | - |
| new technology | TAK | - | - |
| digital technology | TAK | - | - |
| digital economy | TAK | - | - |
| digital single market | TAK | - | - |
| EU strategy | TAK | TAK | - |
| financial services | TAK | - | - |
| electronic money | TAK | TAK | - |
| electronic banking | TAK | TAK | - |
| payment system | TAK | TAK | - |
| intra-EU payment | - | TAK | - |
| international payment | - | TAK | - |
| retail trade | - | TAK | - |
| consumer protection | - | TAK | - |
| paper money | - | TAK | - |
| single market | - | - | TAK |
| financial market | - | - | TAK |
| capital market | - | - | TAK |
| securities | - | - | TAK |
| stock exchange | - | - | TAK |
| sustainable finance | - | - | TAK |
| financial supervision | - | - | TAK |
| small and medium enterprises | - | - | TAK |

**Wniosek:** Trzy komunikaty mają **prawie zerowy overlap EuroVoc** — każdy pokrywa inny segment rynku finansowego. Razem tworzą kompletną mapę tematyczną reform.

---

## Wartość COMMUNIC dla monitoringu regulacyjnego

### 1. Najwcześniejszy sygnał (Early Warning)

Komunikat pojawia się **2-3 lata** przed propozycją legislacyjną. Digital Finance Strategy (wrzesień 2020) zapowiedziała MiCA, DORA, PSR i FIDA — wszystkie złożone 2022-2023.

### 2. Śledzenie łańcucha cytowań (Citation Chain)

```sparql
# Znajdź wszystkie propozycje spawned przez komunikat
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

### 3. Mapowanie EuroVoc na nadchodzącą legislację

Komunikat + EuroVoc pozwala zidentyfikować **jakie tematy** będą regulowane, zanim pojawią się konkretne propozycje.

### 4. Identyfikacja pakietów legislacyjnych

Jeden komunikat → wiele propozycji. DFS → MiCA + DORA + DLT Pilot (tego samego dnia) + PSR + PSD3 + FIDA + Digital Euro (3 lata później).

### 5. DG odpowiedzialne jako sygnał

`resource_legal_service_responsible: FISMA` na komunikacie = legislacja dot. sektora finansowego.

---

## Wzorce do monitorowania

### Nowe komunikaty w zakresie finansowym

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

### Ile propozycji spawnował dany komunikat

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

## Porównanie typu COMMUNIC vs inne zbadane typy

| Aspekt | COMMUNIC | DIR | REG | PROP_REG |
|---|---|---|---|---|
| Wiążący prawnie | **Nie** | Tak | Tak | Nie (jeszcze) |
| EuroVoc | Tak | Tak | Tak | Tak |
| Cytowany przez legislację | **Tak (kluczowe!)** | Tak | Tak | Rzadko |
| Dossier | Nie | Tak | Tak | Tak |
| Case law | Nie | Tak | Tak | Nie |
| NIMs | Nie | Tak | Nie | Nie |
| RTS/ITS | Nie | Tak | Tak | Nie |
| In-force status | Nie (N/A) | Tak | Tak | Nie |
| Predykcja legislacji | **Tak (2-3 lata)** | N/A | N/A | Tak (1-2 lata) |
