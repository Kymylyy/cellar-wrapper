# PSR — Propozycja Rozporządzenia COM(2023) 367: Raport z badania CELLAR

## Identyfikacja

| Pole | Wartość |
|---|---|
| **CELEX** | `52023PC0367` |
| **CELLAR URI** | `http://publications.europa.eu/resource/cellar/04cc5bd5-196f-11ee-806b-01aa75ed71a1` |
| **COM** | COM(2023) 367 final |
| **IMMC** | COM(2023)367 final |
| **Typ** | `PROP_REG` (Propozycja rozporządzenia) |
| **Sektor CELEX** | 5 (akty przygotowawcze) |
| **Wersja** | final |
| **EEA** | Tak |
| **Repertoire** | REP |

**Pełny tytuł:** Proposal for a REGULATION OF THE EUROPEAN PARLIAMENT AND OF THE COUNCIL on payment services in the internal market and amending Regulation (EU) No 1093/2010

**Klasy RDF:** `cdm:act_preparatory` > `cdm:work` (NIE `legislation_secondary` — to propozycja, nie przyjęta legislacja)

---

## Daty

| Pole | Wartość |
|---|---|
| Data dokumentu | 2023-06-28 |
| Data wysłania (dispatch) | 2023-06-28 |
| Data publikacji (legacy) | 2023-07-03 |
| Koniec ważności | 9999-12-31 (bezterminowo — propozycja aktywna) |
| Utworzone w CELLAR | 2023-07-03 |
| Ostatnia modyfikacja | 2023-09-07 |

**Uwaga:** Brak `resource_legal_date_entry-into-force` ani `directive_date_transposition` — to propozycja, nie przyjęty akt.

---

## Instytucje

| Rola | Kto |
|---|---|
| Autorzy (`work_created_by_agent`) | COM (Komisja Europejska), FISMA (DG ds. Stabilności Finansowej) |
| Serwis odpowiedzialny | FISMA |

**Brak:** `resource_legal_responsibility_of_agent`, `resource_legal_addresses_institution` — te pola istnieją tylko na przyjętej legislacji.

---

## Podstawa prawna

| Pole | Wartość |
|---|---|
| Traktat | TFEU 2016 (Traktat o Funkcjonowaniu UE) |
| Artykuł | **12016E114** — Art. 114 TFUE (harmonizacja rynku wewnętrznego) |

---

## Tematyka

### Subject-matter (3 koncepty)
- **LCC** — Free movement of capital
- **LES** — Freedom of establishment
- **MARI** — Internal market — Principles

### Directory codes (2)
- `1040` — Free movement of capital
- `06202020` — Banks

### EuroVoc (9 deskryptorów)

| Koncept | Label EN |
|---|---|
| `eurovoc:1971` | electronic money |
| `eurovoc:1452` | financial institution |
| `eurovoc:560` | financial legislation |
| `eurovoc:8469` | financial services |
| `eurovoc:2220` | intra-EU payment |
| `eurovoc:2216` | payment |
| `eurovoc:c_e749c083` | **payment system** (nowy, brak w PSD2) |
| `eurovoc:2602` | **provision of services** (nowy, brak w PSD2) |
| `eurovoc:3299` | single market |

---

## Hierarchia EuroVoc

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

## Porównanie EuroVoc: PSR vs PSD2

| EuroVoc | PSR | PSD2 |
|---|---|---|
| approximation of laws | - | **TAK** |
| electronic banking | - | **TAK** |
| electronic money | TAK | TAK |
| financial institution | TAK | TAK |
| financial legislation | TAK | TAK |
| financial services | TAK | TAK |
| intra-EU payment | TAK | TAK |
| payment | TAK | TAK |
| payment system | **TAK** | - |
| provision of services | **TAK** | - |
| service | - | **TAK** |
| single market | TAK | TAK |

**Wspólne:** 7 deskryptorów. Kluczowe różnice:
- PSD2 ma `approximation of laws` (dyrektywa harmonizująca prawo krajowe) — PSR nie (rozporządzenie, bezpośrednio stosowalne)
- PSD2 ma `electronic banking` — PSR nie (węższy fokus na systemy płatnicze)
- PSR dodaje `payment system` — odzwierciedla rozszerzony zakres na infrastrukturę (open banking, dostęp do danych)
- PSR dodaje `provision of services` zamiast ogólnego `service` z PSD2

---

## Wersje językowe (Expressions)

24 języki (pełen komplet UE). Formaty na każdą wersję językową:
- `docx` — Word
- `pdf` — PDF
- `xhtml` — HTML

**Łącznie:** 72 manifestacje (3 formaty × 24 języków)

---

## Relacje wychodzące (PSR → inne)

### PSR proponuje zmianę 2 rozporządzeń

| CELEX | Akt |
|---|---|
| `32010R1093` | Rozporządzenie (EU) No 1093/2010 — **Rozporządzenie o EBA** (Europejski Urząd Nadzoru Bankowego) |
| `32017R2394` | Rozporządzenie (EU) 2017/2394 — **Rozporządzenie CPC** (współpraca w zakresie ochrony konsumentów) |

### PSR nie uchyla żadnego aktu

Uchylenie PSD2 leży po stronie towarzyszącej dyrektywy PSD3 (52023PC0366).

### Powiązane dokumenty (`work_related_to_work`)

| CELEX | Akt |
|---|---|
| `52023DC0365` | Komunikat Komisji towarzyszący pakietowi PSR/PSD3 |
| `52023PC0366` | **Propozycja PSD3** — towarzysząca dyrektywa |

### PSR cytuje 43 akty (`work_cites_work`)

**Traktaty:**
- TFUE (pełny tekst, art. 26, 290), TUE (art. 5), Karta Praw Podstawowych

**Dyrektywy (15):**
- PSD1 (32007L0064), **PSD2 (32015L2366)**, EMD2 (32009L0110)
- CRD IV (32013L0036), Settlement Finality (31998L0026), FICOD (32002L0087)
- Consumer Credit (32008L0048), PAD (32014L0092), ePrivacy (32002L0058)
- ADR (32013L0011), Accounting (32013L0034), DGSD (32014L0049)
- EECC (32018L1972), European Accessibility Act (32019L0882), Representative Actions (32020L1828)

**Rozporządzenia (16):**
- **GDPR (32016R0679)**, eIDAS (32014R0910), SEPA (32012R0260)
- CRR (32013R0575), SSM (32013R1024), IFR (32015R0751)
- Rome I (32008R0593), **DORA (32022R2554)**, **MiCA (32023R1114)**
- Cross-border payments (32021R1230), SCA RTS (32018R0389)
- Data protection EU institutions (32018R1725)

**Dokumenty przygotowawcze (5):**
- Digital Finance Strategy (52020DC0591), Retail Payments Strategy (52020DC0592)
- Financial system resilience (52021DC0032), Data Act proposal (52022PC0068)
- Instant credit transfers (52022PC0546)

---

## Relacje przychodzące (inne → PSR)

### Zestawienie ilościowe

| Relacja | Ile | Opis |
|---|---|---|
| `expression_belongs_to_work` | 24 | Wersje językowe samego PSR |
| `owl:annotatedSource` | 6 | Adnotacje OWL (PSR jako źródło) |
| `owl:annotatedTarget` | 6 | Adnotacje OWL (PSR jako cel) |
| `work_cites_work` | 5 | Akty cytujące PSR |
| `resource_legal_influences_resource_legal` | 3 | Opinie wpływające na PSR |
| `dossier_contains_work` | 2 | PSR w 2 dossierach |
| `resource_legal_contains_eesc_opinion_on_resource_legal` | 2 | Opinie EKES |
| `work_related_to_work` | 2 | Powiązane SWD |
| `dossier_initiated_by_act_preparatory` | 1 | PSR inicjuje dossier |
| `resource_legal_contains_ep_opinion_on_resource_legal` | 1 | Stanowisko PE |
| `event_legal_contains_work` | 1 | Wydarzenie prawne |

### Kto cytuje PSR (5 aktów)

| CELEX | Typ | Opis |
|---|---|---|
| `52023PC0369` | PROP_DIR | Propozycja dyrektywy o usługach digital euro — cytuje PSR jako kontekst |
| `52023DC0715` | Komunikat | Komunikat Komisji nt. kompetencji i mobilności talentów |
| `52025DC0708` | Raport | Raport Komisji o art. 33 DSA — interakcja z innymi aktami |
| `52025SC0368` | SWD | Dokument roboczy towarzyszący raportowi DSA |
| `52025PC0941` | PROP_REG | **Propozycja rozporządzenia o rozliczeniach (Settlement Finality, 2025)** — cytuje PSR |

### Opinie instytucjonalne dotyczące PSR

| CELEX | Instytucja | Data | Opis |
|---|---|---|---|
| `52023AE3611` | **EKES** | 2023-12-14 | Opinia EKES o pakiecie FIDA+PSD3+PSR |
| `52024AB0013` | **EBC** | 2024-04-30 | Opinia EBC CON/2024/13 o PSR+PSD3 |
| `52023XX01019` | **EIOD** | 2023-11-16 | Streszczenie opinii EIOD o PSR+PSD3 |
| `52024AP0298` | **PE** | 2024-04-23 | Stanowisko PE w I czytaniu |

---

## Procedura legislacyjna — Dossier 2023/0210(COD)

### Metadane dossier

| Pole | Wartość |
|---|---|
| Procedura | **2023/0210(COD)** — OLP (zwykła procedura legislacyjna) |
| Kompetencja UE | Wspólna (SHARED) |
| Status: adopted | **false** |
| Status: pending | **true** |
| Status: withdrawn | **false** |
| Inicjator | PSR (52023PC0367) |
| Raporteur PE | **Marek Belka** (Komisja ECON) |
| Poprzedni dossier | Planning workflow z 2022-09-05 ("Payment services – revision of EU rules") |
| Ostatnia modyfikacja | **2025-11-25** |

### Oś czasu procedury

| Data | Wydarzenie |
|---|---|
| 2022-09 | Komisja otwiera dossier planistyczny (przegląd PSD2) |
| **2023-06-28** | Komisja przyjmuje propozycję PSR COM(2023)367 + PSD3 COM(2023)366 |
| 2023-07-05 | Transmisja do Rady (cover notes) |
| 2023-11-13 | Projekt raportu komisji ECON PE (sprawozdawca: Belka) |
| 2023-11-16 | Opinia EIOD o PSR+PSD3 |
| 2023-12-14 | Opinia EKES o pakiecie FIDA+PSD3+PSR |
| 2024-02-22 | Raport komisji ECON PE przyjęty |
| **2024-04-23** | **PE — I czytanie: P9_TA(2024)0298** (PSR) i P9_TA(2024)0297 (PSD3) |
| 2024-04-30 | Opinia EBC CON/2024/13 |
| 2024-07-02 | Nota Rady o wynikach I czytania PE |
| **2025-06-13** | **Rada przyjmuje mandat negocjacyjny (general approach) dla PSR i PSD3** |
| 2025-09-17 | Stanowisko PE opublikowane w Dz.U. C/2025/3725 |
| **2025-11 →** | **Trilog w toku** |
| **2026-02** (teraz) | Status: **pending, nie przyjęty, nie wycofany** |

### Dokumenty w dossier (26 szt.)

| Data | CELEX | Typ | Opis |
|---|---|---|---|
| 2023-06-28 | **52023PC0367** | PROP_REG | **Propozycja PSR** |
| 2023-06-28 | 52023SC0232 | IMPACT_ASSESS_SUM | Streszczenie oceny skutków |
| 2023-06-28 | 52023SC0231 | IMPACT_ASSESS | Pełna ocena skutków |
| 2023-06-28 | _(brak)_ | OPIN_IMPACT_ASSESS | Opinia Rady ds. Kontroli Regulacyjnej |
| 2023-07-05 | _(brak)_ | NOTE_COVER | Noty okładkowe Rady (5 szt.) |
| 2023-11-13 | _(brak)_ | REPORT_DRAFT_EP_CMT | Projekt raportu ECON |
| 2023-11-16 | 52023XX01019 | SUM | Opinia EIOD |
| 2023-12-14 | 52023AE3611 | OPIN | Opinia EKES |
| 2024-02-22 | _(brak)_ | REPORT_EP | Raport komisji ECON |
| **2024-04-23** | **52024AP0298** | **RES_LEGIS** | **Stanowisko PE (I czytanie)** |
| 2024-04-23 | _(brak)_ | ADOPT_TEXT | Tekst przyjęty |
| 2024-04-23 | _(brak)_ | PLENARY_MINUTES_EP | Protokół posiedzenia plenarnego |
| 2024-04-30 | 52024AB0013 | OPIN | Opinia EBC |
| 2024-07-02 | _(brak)_ | NOTE_INFO | Nota informacyjna Rady |
| **2025-06-13** | _(brak)_ | NOTE | **Mandat Rady do negocjacji (PSR)** |
| **2025-06-13** | _(brak)_ | NOTE | **Mandat Rady do negocjacji (PSD3)** |
| **2025-06-13** | _(brak)_ | ITEM_I_NOTE | Punkt I — pakiet PSD+PSR |
| 2025-06-18..27 | _(brak)_ | AGENDA_DRAFT_CONSIL | Porządki obrad COREPER II (4 szt.) |

---

## Pakiet legislacyjny PSR + PSD3

PSR i PSD3 to **dwa osobne dossier**, ale traktowane jako **jeden pakiet**:

| | PSR (Rozporządzenie) | PSD3 (Dyrektywa) |
|---|---|---|
| **CELEX** | 52023PC0367 | 52023PC0366 |
| **Procedura** | 2023/0210(COD) | 2023/0209(COD) |
| **Status** | Pending | Pending |
| **Raporteur PE** | Marek Belka | Ondrej Kovarik |
| **Głosowanie PE** | 52024AP0298 (23.04.2024) | 52024AP0297 (23.04.2024) |
| **Mandat Rady** | 13.06.2025 | 13.06.2025 |
| **Co zmienia** | EBA Reg (32010R1093), CPC Reg (32017R2394) | — (nowy akt) |
| **Co uchyla** | Nic | PSD2 (32015L2366) + EMD2 (32009L0110) |

**Wspólne dokumenty:**
- Ocena skutków: 52023SC0231 + 52023SC0232
- Opinia EKES: 52023AE3611
- Opinia EBC: 52024AB0013
- Mandat Rady: oba przyjęte jednocześnie 13.06.2025

---

## Adnotacje OWL (12 sztuk: 6 source + 6 target)

### PSR jako źródło (6)

| Relacja | Cel | Kwalifikator |
|---|---|---|
| `resource_legal_proposes_to_amend` | 32010R1093 (EBA) | `type_of_link_target = EA` |
| `resource_legal_proposes_to_amend` | 32017R2394 (CPC) | `type_of_link_target = EA` |
| `work_related_to_work` | 52023DC0365 (Komunikat) | `type_of_link_target = RD` |
| `work_related_to_work` | 52023PC0366 (PSD3) | `type_of_link_target = RD` |
| `resource_legal_date_dispatch` | 2023-06-28 | `comment_on_date = TRANS/CONS` (→ Rada) |
| `resource_legal_date_dispatch` | 2023-06-28 | `comment_on_date = TRANS/PARL` (→ PE) |

### PSR jako cel (6)

| Relacja | Źródło | Kwalifikator |
|---|---|---|
| `resource_legal_influences` | 52023XX01019 (opinia EIOD) | `type_of_link_target = EA` |
| `resource_legal_influences` | 52024AB0013 (opinia EBC) | `type_of_link_target = EA` |
| `work_related_to_work` | 52023SC0231 (SWD) | `type_of_link_target = RD` |
| `work_related_to_work` | 52023SC0232 (SWD) | `type_of_link_target = RD` |
| `contains_eesc_opinion_on` | 52023AE3611 (EKES) | `type_of_link_target = EA` |
| `contains_ep_opinion_on` | 52024AP0298 (PE) | `type_of_link_target = EA`, `role2 = MD` |

**Kwalifikator `role2 = MD`** na stanowisku PE oznacza "Main Document" — wyróżnia go jako główny dokument decyzyjny PE w procedurze.

---

## Legislacja o najwyższym EuroVoc overlap z PSR

| Overlap | CELEX | Akt |
|---|---|---|
| **9/9** | 52024AB0013 | Opinia EBC o PSR |
| **9/9** | 52024AP0298 | Stanowisko PE o PSR |
| 8/9 | 52023XX01019 | Opinia EIOD |
| 8/9 | 52023AE3611 | Opinia EKES |
| **7/9** | **32015L2366** | **PSD2** |
| 7/9 | 52024AP0297 | Stanowisko PE o PSD3 |
| 7/9 | 52023PC0366 | PSD3 propozycja |
| 7/9 | 32019R0518 | Rozp. o płatnościach transgranicznych |
| 7/9 | 52023SC0231, 52023SC0232 | SWD (oceny skutków) |

---

## Porównanie PSR vs PSD2 vs DORA

| Aspekt | PSR (Propozycja REG) | PSD2 (Dyrektywa) | DORA (Rozporządzenie) |
|---|---|---|---|
| CELEX | 52023PC0367 | 32015L2366 | 32022R2554 |
| Typ | PROP_REG | DIR | REG |
| Status | **Pending (trilog)** | In-force (do 2026-06-18) | In-force |
| Sektor CELEX | 5 (przygotowawcze) | 3 (przyjęte) | 3 (przyjęte) |
| Data | 2023-06-28 | 2015-11-25 | 2022-12-14 |
| Podstawa | Art. 114 TFUE | Art. 114 TFUE | Art. 114 TFUE |
| Cytuje aktów | 43 | 31 | 38+ |
| Cytowany przez | 5 | 283 | 64 |
| NIM (transpozycje) | 0 (propozycja) | 258 | 0 (rozporządzenie) |
| Orzecznictwo TSUE | 0 | 5 wyroków + 10 pytań | 0 |
| Akty delegowane/wyk. | 0 (propozycja) | 9 (RTS+ITS) | 12 (RTS+ITS) |
| Adnotacje OWL | 12 | 570+ | 74 |
| EuroVoc deskryptorów | 9 | 10 | 9 |
| EuroVoc overlap z PSD2 | 7/9 | — | 1/9 (`financial services`) |
| Companion | PSD3 (52023PC0366) | Brak | Dir 2022/2556 |
| Zmienia | EBA Reg, CPC Reg | EMD2, Commercial Agents, CRD IV, EBA Reg | CRA, EMIR, MiFIR, CSDR, Benchmarks |
| Uchyla | Nic (PSD3 uchyla PSD2) | PSD1 | Nic |

---

## Kluczowe odkrycia

1. **PSR jest w trilogu** — PE przyjął stanowisko 23.04.2024, Rada mandat negocjacyjny 13.06.2025, procedura aktywna (ostatnia aktualizacja dossier: 25.11.2025).

2. **Podwójna struktura dossier** — PSR jest w 2 dossierach: wewnętrznym Komisji (adoption workflow) i interinstytucjonalnym (2023/0210/COD). To standardowy wzorzec.

3. **Pakiet PSR+PSD3** — osobne procedury (0210/COD i 0209/COD), ale wspólne: ocena skutków, opinia EKES, opinia EBC, mandaty Rady przyjęte tego samego dnia.

4. **Predecessor dossier z 2022** — dossier planistyczny Komisji z września 2022 potwierdza, że PSR wyrosło z przeglądu PSD2.

5. **EuroVoc potwierdza charakter rozporządzenia** — brak `approximation of laws` (obecny w PSD2), co semantycznie odzwierciedla fakt, że rozporządzenie jest bezpośrednio stosowalne (nie harmonizuje prawa krajowego).

6. **PSR rozszerza zakres EBA** — zmiana Rozporządzenia 1093/2010 (EBA) oznacza rozszerzenie kompetencji nadzorczych EBA w zakresie usług płatniczych.

7. **Nowy deskryptor `payment system`** — PSR wprowadza fokus na infrastrukturę systemów płatniczych i open banking, czego nie było w PSD2.

8. **Propozycja jako typ aktu w CELLAR** — brak wielu pól typowych dla przyjętej legislacji: `date_entry-into-force`, `addresses_institution`, `in-force`, `directive_date_transposition`. Klasa RDF to `act_preparatory`, nie `legislation_secondary`.
