# CELLAR Wrapper — Blueprint (DEPRECATED)

> [!WARNING]
> This document is a historical blueprint and is no longer a maintained source of truth.
> Since it was written, the API contract and implementation have changed.
>
> Current sources:
> - [API_CONTRACT.md](API_CONTRACT.md)
> - [METHOD_MAPPING.md](METHOD_MAPPING.md)
> - [research/README.md](research/README.md) (archived research notes)

## Co jest w CELLAR, a czego nie ma

### Jest (publikacje w Dzienniku Urzędowym UE + EUR-Lex)
- Rozporządzenia, dyrektywy, decyzje (przyjęte)
- Propozycje legislacyjne (COM)
- Akty delegowane i wykonawcze (RTS/ITS jako rozporządzenia Komisji)
- Komunikaty Komisji (strategie, plany działania)
- Orzeczenia TSUE (wyroki, opinie AG, postanowienia)
- Wyroki sądów krajowych (DEC_NC — ograniczona kompletność)
- Krajowe środki transpozycji (NIMs) — 196 630 dokumentów
- Wersje skonsolidowane (tekst ujednolicony po nowelizacjach)
- Sprostowania (corrigenda)
- Wytyczne i zalecenia ECB (363 wytyczne, 160 zaleceń)
- Streszczenia legislacyjne (legissum)
- Pełne teksty (PDF, XHTML, DOC)

### NIE MA (publikowane poza Dz.U.)
- **Wytyczne EBA** — publikowane na eba.europa.eu, nie w Dz.U.
- **Wytyczne ESMA** — publikowane na esma.europa.eu
- **Wytyczne EIOPA** — publikowane na eiopa.europa.eu
- **Q&A nadzorcze** ESA
- **Opinie ESA o praktykach nadzorczych**
- **Dokumenty konsultacyjne** ESA

EBA/ESMA/EIOPA w CELLAR istnieją **tylko jako podmioty instytucjonalne** (budżety, rekrutacja, sprawozdania finansowe). Ich soft-law (wytyczne, zalecenia, Q&A) wymaga osobnego źródła danych.

**Wyjątek: RTS/ITS** — standardy techniczne opracowane przez ESA, ale formalnie przyjęte przez Komisję jako rozporządzenia delegowane/wykonawcze — **te są w CELLAR** jako akty Komisji (REG_DEL, REG_IMPL).

---

## Co możemy wyciągnąć — katalog funkcji wrappera

### 1. Identyfikacja aktu

Po podaniu numeru CELEX (np. `32022R2554`) pobieramy:

| Informacja | Przykład |
|---|---|
| Pełny tytuł (w wybranym języku) | Regulation (EU) 2022/2554 on digital operational resilience... |
| Typ aktu | Rozporządzenie / Dyrektywa / Propozycja / Decyzja |
| Data dokumentu | 2022-12-14 |
| Data wejścia w życie | 2023-01-16 |
| Data rozpoczęcia stosowania | 2025-01-17 |
| Status obowiązywania | W mocy / Uchylony / Wygasł |
| Data końca obowiązywania | 9999-12-31 (bezterminowo) |
| Podstawa traktatowa | Art. 114 TFUE |
| Organ odpowiedzialny | COM + FISMA |
| ELI | eli/reg/2022/2554/oj |
| Publikacja w Dz.U. | L 333, 27.12.2022, p. 1 |

**Dotyczy:** rozporządzenia, dyrektywy, decyzje, propozycje, komunikaty

---

### 2. Nowelizacje (Amending Acts)

Kto nowelizuje dany akt i co dany akt nowelizuje.

| Kierunek | Pytanie | Przykład |
|---|---|---|
| **Wychodzące** | Co ten akt nowelizuje? | DORA nowelizuje: Reg. 1093/2010 (EBA), Reg. 1094/2010 (EIOPA), Reg. 1095/2010 (ESMA), Dir. 2009/138 (Solvency II), Dir. 2014/65 (MiFID II) |
| **Przychodzące** | Kto nowelizuje ten akt? | Na dziś: brak formalnych nowelizacji DORA |

Właściwość CDM: `resource_legal_amends_resource_legal` (nie `work_amends_work`)

**Dotyczy:** rozporządzenia, dyrektywy

---

### 3. Uchylenia (Repeals)

| Kierunek | Pytanie | Przykład |
|---|---|---|
| **Wychodzące** | Co ten akt uchyla? | PSD2 uchyla PSD1 (Dir. 2007/64) |
| **Przychodzące** | Czy ktoś uchyla ten akt? | PSR proponuje uchylenie PSD2 |

Dwa typy: jawne (`resource_legal_repeals_resource_legal`) i dorozumiane (`resource_legal_implicitly_repeals_resource_legal`).

**Dotyczy:** dyrektywy, rozporządzenia

---

### 4. Akty delegowane i wykonawcze (RTS/ITS)

Akty "poziomu 2" — standardy techniczne opracowane przez ESA, przyjęte przez Komisję.

| Typ | Typ w CELLAR | Ile w CELLAR ogółem |
|---|---|---|
| Rozporządzenie delegowane (RTS) | `REG_DEL` | 3 399 |
| Rozporządzenie wykonawcze (ITS) | `REG_IMPL` | 14 644 |
| Dyrektywa delegowana | `DIR_DEL` | 240 |
| Dyrektywa wykonawcza | `DIR_IMPL` | 150 |
| Decyzja wykonawcza | `DEC_IMPL` | 5 332 |
| Decyzja delegowana | `DEC_DEL` | 111 |
| Projekty (draft) | `REG_DEL_DRAFT`, `REG_IMPL_DRAFT` | 586 + 707 |

**Uwaga:** Szukanie RTS/ITS dla konkretnego aktu przez `work_cites_work` jest zbyt szerokie (łapie akty, które tylko wspominają DORA). Lepsze podejście: szukanie przez `resource_legal_based_on_resource_legal` lub filtrowanie tytułów.

**Dotyczy:** rozporządzenia, dyrektywy (akty bazowe)

---

### 5. Cytowania (Citations)

Kto cytuje dany akt — najszersza relacja, obejmuje zarówno normatywne odwołania jak i informacyjne wzmianki.

| Pytanie | Przykład |
|---|---|
| Kto cytuje DORA? | 18 nowych aktów w ostatnich 12 miesiącach, w tym propozycja `52026PC0011` |
| Kogo cytuje DORA? | 44+ aktów (PSD2, MiFID II, GDPR, eIDAS, CRR, CRD...) |

Filtrowanie po typie aktu i dacie pozwala wyłapać np. "nowe propozycje legislacyjne cytujące DORA od stycznia 2025".

**Dotyczy:** wszystkie typy dokumentów

---

### 6. Propozycje zmian (Proposals to Amend)

Specyficzne dla propozycji legislacyjnych — co dana propozycja zamierza zmienić.

| Pytanie | Przykład |
|---|---|
| Co PSR proponuje zmienić? | Reg. 1093/2010 (EBA), Reg. 2017/2394 (CPC) |
| Jakie propozycje chcą zmienić DORA? | `52025PC0943` (CCP/ESMA amendments) |

Właściwość: `resource_legal_proposes_to_amend_resource_legal`

**Dotyczy:** propozycje (PROP_REG, PROP_DIR)

---

### 7. Wersje skonsolidowane (Consolidated Texts)

Tekst ujednolicony uwzględniający wszystkie nowelizacje i sprostowania do danego momentu.

| Pytanie | Przykład |
|---|---|
| Ile wersji skonsolidowanych ma PSD2? | 3: oryginał (2015-12-23), po nowelizacji (2024-04-08), najnowsza (2025-01-17) |
| Ile wersji ma DORA? | 1: oryginał (2022-12-27) — brak nowelizacji |
| Jakie nowelizacje uwzględnia dana konsolidacja? | `act_consolidated_consolidates_resource_legal` → lista aktów |

CELEX skonsolidowany: `0` + CELEX bazowy + `-` + data (np. `02015L2366-20250117`)

**Dotyczy:** rozporządzenia, dyrektywy

---

### 8. Sprostowania (Corrigenda)

Poprawki techniczne/redakcyjne do aktu.

| Pytanie | Przykład |
|---|---|
| Ile sprostowań ma DORA? | 9 (od 2023-05 do 2025-11) |
| Kiedy było ostatnie? | 2025-11-21 (`32022R2554R(09)`) |

CELEX sprostowania: CELEX bazowy + `R(nn)` (np. `32022R2554R(01)`)
Ogółem w CELLAR: 28 677 sprostowań.

**Dotyczy:** rozporządzenia, dyrektywy

---

### 9. Transpozycja krajowa (NIMs — National Implementation Measures)

Jak państwa członkowskie wdrożyły dyrektywę do prawa krajowego.

| Pytanie | Przykład |
|---|---|
| Które kraje transponowały PSD2? | 50+ aktów krajowych (LVA, CYP, HUN, AUT, POL, SVK, DEU, CZE, BGR, EST, PRT, GRC...) |
| Kiedy Polska transponowała? | `72015L2366POL_202401176` — 2023-08-29 |
| Termin transpozycji dyrektywy? | `directive_date_transposition` |

CELEX NIMs: `7` + CELEX dyrektywy + kod kraju + numer (np. `72015L2366DEU_202502012`)
Ogółem w CELLAR: 196 630 aktów transpozycyjnych.

**Dotyczy:** wyłącznie dyrektywy

---

### 10. Dossier legislacyjne (Legislative Procedure)

Pełna ścieżka proceduralna propozycji od złożenia do przyjęcia.

| Pytanie | Przykład |
|---|---|
| Numer procedury PSR? | 2023/0210(COD) |
| Jakie dokumenty są w dossier? | Propozycja COM, opinia EESC, opinia ECB, opinia EDPS, stanowisko EP, stanowisko Rady... |
| Na jakim etapie jest procedura? | Trilog / Pierwsze czytanie / Przyjęty |

Właściwość: `dossier_contains_work`

**Dotyczy:** propozycje legislacyjne

---

### 11. Komunikaty Komisji (Early Warning)

Dokumenty strategiczne zapowiadające przyszłą legislację — najwcześniejszy sygnał (2-3 lata przed propozycją).

| Pytanie | Przykład |
|---|---|
| Jakie komunikaty wydał DG FISMA? | Digital Finance Strategy, Retail Payments Strategy, CMU |
| Ile propozycji "zrodził" dany komunikat? | DFS → MiCA, DORA, DLT Pilot, PSR, PSD3, FIDA, Digital Euro (10+ aktów) |
| Jakie tagi EuroVoc ma komunikat? | → mapowanie na przyszłe obszary regulacji |

Właściwość filtrująca: `resource_legal_service_responsible` (np. `FISMA`)

**Dotyczy:** komunikaty (COMMUNIC)

---

### 12. Orzecznictwo TSUE (Case Law)

Wyroki Trybunału Sprawiedliwości UE interpretujące dany akt.

| Pytanie | Przykład |
|---|---|
| Jakie wyroki dotyczą PSD2? | 5 wyroków TSUE (m.in. C-287/19 DenizBank) |
| Które artykuły interpretuje wyrok? | `case-law_interpretes_resource_legal` |
| Kto był rzecznikiem generalnym? | `case-law_delivered_by_advocate-general` |
| Jakie opinie AG poprzedzały wyrok? | `case-law_has_conclusions_opinion_advocate-general` |
| Jakie artykuły naukowe omawiają wyrok? | `case-law_article_journal_related` |
| Z jakiego kraju pochodzi pytanie prejudycjalne? | `case-law_originates_in_country` |

**Dotyczy:** wyroki TSUE (JUDG), opinie AG (OPIN_AG), postanowienia (ORDER)

---

### 13. Wyroki sądów krajowych (National Court Decisions)

Orzeczenia sądów krajowych odnoszące się do prawa UE.

| Pytanie | Przykład |
|---|---|
| Wyroki krajowe dot. PSD2? | 3 bezpośrednie odniesienia (ograniczona kompletność — 56%) |
| Z jakiego kraju? | Niemcy dominują (7 815), Francja (4 580), Polska (286) |
| Które artykuły? | Format: `32015L2366-A04PT21` (art. 4 pkt 21) |

**Ograniczenie:** Tylko 56% wyroków krajowych ma wypełnione pole `european_act_reference`. Nie wszystkie kraje raportują równomiernie.

**Dotyczy:** DEC_NC

---

### 14. Klasyfikacja EuroVoc

Wielojęzyczny tezaurus tematyczny UE — 7 253 konceptów w użyciu.

| Pytanie | Przykład |
|---|---|
| Jakie tagi ma DORA? | financial technology, cloud computing, information security, risk management, digitisation, outsourcing, financial services, digital single market, information technology |
| Znajdź akty o "payment system" + "data protection" | Wielotagowe wyszukiwanie |
| Znajdź koncept po nazwie | "crypto" → `eurovoc:6778` (cryptography); "fintech" → brak (użyj "financial technology" `c_79e507c2`) |
| Hierarchia konceptów | broader/narrower terms via SKOS |

**Uwaga:** EuroVoc ma dwa formaty URI: stare numeryczne (`eurovoc:5283`) i nowe hash (`eurovoc:c_e749c083`). Nie można zakładać formatu.

**Uwaga 2:** Orzeczenia TSUE **nie mają tagów EuroVoc** — mają `resource_legal_is_about_subject-matter`.

**Dotyczy:** rozporządzenia, dyrektywy, propozycje, komunikaty (NIE orzeczenia TSUE)

---

### 15. Podstawa prawna (Legal Basis)

Na jakiej podstawie traktatowej wydano akt.

| Pytanie | Przykład |
|---|---|
| Podstawa traktatowa DORA? | Art. 114 TFUE |
| Podstawa legislacyjna (akt nadrzędny)? | `resource_legal_based_on_resource_legal` |

**Dotyczy:** rozporządzenia, dyrektywy, propozycje

---

### 16. Terminy (Deadlines)

Różne daty graniczne związane z aktem — wielowartościowe pole.

| Data | Przykład DORA |
|---|---|
| Wejście w życie | 2023-01-16 |
| Rozpoczęcie stosowania | 2025-01-17 |
| Deadline przeglądu | 2028-01-17 |
| Deadline raportu | 2029-01-17 |
| Termin transpozycji (dyrektywy) | `directive_date_transposition` |

Właściwość: `resource_legal_date_deadline` (wielowartościowa)

**Dotyczy:** rozporządzenia, dyrektywy

---

### 17. Pobieranie tekstu (Full Text Download)

Pobranie pełnego tekstu aktu w wybranym formacie i języku.

| Format | Dostępność |
|---|---|
| PDF | Prawie zawsze |
| XHTML | Często |
| DOCX | Przy propozycjach |
| Streszczenie (legissum) | Dla ważniejszych aktów |

Ścieżka: Work → Expression (język) → Manifestation (format) → Item (plik)

**Dotyczy:** wszystkie typy

---

### 18. Wyszukiwanie temporalne (Monitoring)

Wykrywanie nowych dokumentów od ostatniego sprawdzenia.

| Pytanie | Filtr |
|---|---|
| Nowe akty w Dz.U. od daty X | `work_date_document > X` + typ |
| Nowe cytowania aktu Y od daty X | `work_cites_work = Y` + `date > X` |
| Nowe wyroki TSUE od daty X | typ JUDG + `date > X` |
| Nowe propozycje w temacie Z | EuroVoc + typ PROP_* + `date > X` |
| Nowe NIMs dla dyrektywy od daty X | CELEX `7{celex}*` + `date > X` |
| Nowe sprostowania aktu od daty X | CELEX `{celex}R(*` + `date > X` |
| Nowe wersje skonsolidowane | CELEX `0{celex}*` + `date > X` |

To jest rdzeń monitoringu — każde z powyższych zapytań z parametrem "since last check".

---

### 19. Resolucja CELEX → CELLAR URI

Tłumaczenie numeru CELEX na wewnętrzny URI CELLAR (potrzebny do wielu zapytań relacyjnych).

| Pytanie | Przykład |
|---|---|
| URI CELLAR dla CELEX `32022R2554`? | `http://publications.europa.eu/resource/cellar/...` |
| Czy CELEX istnieje w CELLAR? | Tak/Nie |

**Gotcha:** Porównanie stringowe `= '32022R2554'` nie działa — trzeba użyć `FILTER(CONTAINS(?celex, '2022R2554'))`.

**Dotyczy:** wszystkie typy dokumentów

---

### 20. Pytania prejudycjalne (Preliminary Questions)

Otwarte sprawy skierowane do TSUE przez sądy krajowe — sygnał, że dany akt jest kwestionowany lub niejasny.

| Pytanie | Przykład |
|---|---|
| Jakie pytania prejudycjalne dotyczą PSD2? | 10 spraw (w tym C-287/19 DenizBank) |
| Z jakiego kraju pochodzi pytanie? | `case-law_originates_in_country` |
| Kto złożył? | Sąd odsyłający |

Właściwość: `communication_case_new_submits_preliminary_question`

**Dotyczy:** orzecznictwo TSUE (JUDG, ORDER)

---

### 21. Opinie instytucjonalne (Institutional Opinions)

Opinie wydane w ramach procedury legislacyjnej — ECB, EESC, EDPS, EP committees.

| Pytanie | Przykład |
|---|---|
| Jakie opinie wydano ws. PSR? | Opinia ECB, opinia EESC, opinia EDPS |
| Kiedy? | Data dokumentu opinii |

Właściwość: `contains_eesc_opinion_on`, `contains_ep_opinion_on` + filtrowanie dossier

**Dotyczy:** propozycje legislacyjne

---

### 22. Akty uzupełniające (Completing Acts)

Akty, które uzupełniają (a nie nowelizują) dany akt — np. dodatkowe przepisy wykonawcze.

| Pytanie | Przykład |
|---|---|
| Co uzupełnia DORA? | Akty delegowane uzupełniające szczegóły techniczne |

Właściwość: `resource_legal_completes_resource_legal`

**Dotyczy:** rozporządzenia, dyrektywy

---

### 23. Adnotacje artykułowe (Article-Level Annotations)

Granularne powiązania na poziomie artykuł/paragraf — kto cytuje/nowelizuje konkretny artykuł, nie cały akt.

| Pytanie | Przykład |
|---|---|
| Które akty odwołują się do art. 4 PSD2? | OWL Annotation Axioms — 570 adnotacji dla PSD2 |
| Jakie artykuły DORA nowelizuje w MiFID II? | `annotatedSource` + `annotatedTarget` + qualifier |

Wzorzec: reifikacja OWL (`owl:annotatedSource`, `owl:annotatedTarget`, `owl:annotatedProperty` + `resource_legal_id_celex_of_annotated_target`)

**Dotyczy:** rozporządzenia, dyrektywy, propozycje

---

### 24. Wyrażenia i formaty (Expressions & Manifestations)

Lista dostępnych wersji językowych i formatów dokumentu.

| Pytanie | Przykład |
|---|---|
| W ilu językach jest DORA? | 24 wersje językowe |
| Jakie formaty są dostępne? | PDF, XHTML, DOC, FORMEX |
| URI do konkretnego pliku? | Manifestation → Item → URL |

Ścieżka FRBR: Work → Expression (język) → Manifestation (format) → Item (plik)

**Dotyczy:** wszystkie typy

---

### 25. Kody klasyfikacji (Directory Codes)

Klasyfikacja tematyczna aktów wg katalogu EUR-Lex (Directory of EU legislation).

| Pytanie | Przykład |
|---|---|
| Kod klasyfikacji DORA? | np. `10.20.30` (Bankowość / Nadzór ostrożnościowy) |

Właściwość: `resource_legal_is_about_concept_directory-code`

**Dotyczy:** rozporządzenia, dyrektywy, propozycje

---

### 26. Propozycja → Przyjęty akt (Proposal to Adopted Act)

Śledzenie, czy propozycja legislacyjna została przyjęta i jaki akt z niej wynikł.

| Pytanie | Przykład |
|---|---|
| Czy propozycja PSR (52023PC0367) została przyjęta? | Jeszcze nie (pending) |
| Co wynikło z propozycji MiCA (52020PC0593)? | `32023R1114` (Regulation MiCA) |

Właściwość: `resource_legal_adopts_resource_legal` (odwrotny kierunek od adopted → proposal)

**Dotyczy:** propozycje → akty przyjęte

---

### 27. Wyszukiwanie po Subject Matter

Wyszukiwanie aktów wg kodów subject-matter — alternatywa dla EuroVoc, szczególnie przydatna dla orzecznictwa TSUE (które nie ma EuroVoc).

| Pytanie | Przykład |
|---|---|
| Wyroki TSUE dot. "Freedom of establishment"? | `resource_legal_is_about_subject-matter` + typ JUDG |
| Akty dot. konkurencji od 2024? | Subject matter code + `date > 2024` |

385 kodów subject-matter. Najczęstsze: External relations (35 153), Competition (30 201), Environment (23 800).

**Dotyczy:** wszystkie typy, w tym orzeczenia TSUE

---

### 28. Dodatkowe relacje legislacyjne

Relacje rzadsze, ale istotne dla pełnego obrazu regulacyjnego.

| Relacja | Właściwość CDM | Opis |
|---|---|---|
| **Zawieszenie** | `resource_legal_suspends_resource_legal` | Tymczasowe zawieszenie stosowania aktu |
| **Częściowe zawieszenie** | `resource_legal_partially_suspends_resource_legal` | Zawieszenie wybranych przepisów |
| **Odroczenie stosowania** | `resource_legal_defers_application_of_resource_legal` | Przesunięcie terminu stosowania |
| **Dezaktualizacja** | `resource_legal_renders_obsolete_resource_legal` | Akt staje się nieaktualny (bez formalnego uchylenia) |
| **Wpływanie** | `resource_legal_influences_resource_legal` | Luźniejsze powiązanie (wpływa na) |

**Dotyczy:** rozporządzenia, dyrektywy

---

## Podsumowanie — mapa funkcji

```
CELLAR Wrapper (~33 metody)
│
├── LOOKUP (identyfikacja)
│   ├── resolve_celex(celex)              → CELEX → CELLAR URI (z CONTAINS workaround)
│   ├── get_act(celex)                    → metadane, tytuł, daty, status
│   ├── get_eurovoc(celex)                → tagi tematyczne
│   ├── get_subject_matter(celex)         → kody subject-matter
│   ├── get_legal_basis(celex)            → podstawa traktatowa/legislacyjna
│   ├── get_directory_codes(celex)        → kody klasyfikacji EUR-Lex
│   └── get_expressions(celex)            → dostępne języki i formaty
│
├── RELATIONS (powiązania)
│   ├── get_amendments(celex)             → nowelizacje (in/out)
│   ├── get_repeals(celex)                → uchylenia (in/out)
│   ├── get_citations(celex)              → cytowania (in/out)
│   ├── get_delegated_acts(celex)         → RTS/ITS delegowane/wykonawcze
│   ├── get_completing_acts(celex)        → akty uzupełniające
│   ├── get_proposals_to_amend(celex)     → propozycje zmian
│   ├── get_adopted_act(celex)            → propozycja → przyjęty akt
│   ├── get_related_works(celex)          → powiązane dokumenty
│   └── get_other_relations(celex)        → suspends/defers/renders_obsolete/influences
│
├── LIFECYCLE (cykl życia)
│   ├── get_consolidated_versions(celex)  → wersje skonsolidowane
│   ├── get_corrigenda(celex)             → sprostowania
│   ├── get_nims(celex)                   → transpozycja krajowa (dyrektywy)
│   ├── get_dossier(celex)                → procedura legislacyjna
│   ├── get_opinions(celex)               → opinie instytucjonalne (ECB, EESC, EDPS, EP)
│   └── get_deadlines(celex)              → terminy (wejście w życie, przeglądy)
│
├── CASE LAW (orzecznictwo)
│   ├── get_cjeu_judgments(celex)         → wyroki TSUE dot. aktu
│   ├── get_ag_opinions(celex)            → opinie rzeczników generalnych
│   ├── get_preliminary_questions(celex)  → pytania prejudycjalne
│   ├── get_national_decisions(celex)     → wyroki sądów krajowych
│   └── get_article_annotations(celex)    → adnotacje artykułowe (OWL reification)
│
├── SEARCH (wyszukiwanie)
│   ├── search_by_eurovoc(tags, type, since)          → szukaj po tagach EuroVoc
│   ├── search_by_subject_matter(codes, type, since)  → szukaj po subject-matter
│   ├── search_by_title(keyword, type, since)         → szukaj po tytule
│   ├── search_communications(dg, since)              → komunikaty KE
│   └── find_eurovoc_concept(label)                   → szukaj konceptu EuroVoc
│
├── MONITORING (zmiany od daty X)
│   ├── new_citations(celex, since)       → nowe cytowania
│   ├── new_amendments(celex, since)      → nowe nowelizacje
│   ├── new_delegated_acts(celex, since)  → nowe RTS/ITS
│   ├── new_case_law(celex, since)        → nowe orzeczenia
│   ├── new_corrigenda(celex, since)      → nowe sprostowania
│   ├── new_consolidated(celex, since)    → nowe konsolidacje
│   ├── new_nims(celex, since)            → nowe transpozycje
│   └── new_by_eurovoc(tags, type, since) → nowe akty w temacie
│
└── DOWNLOAD (pobieranie)
    ├── get_text(celex, lang, format)     → pełny tekst
    └── get_summary(celex, lang)          → streszczenie legislacyjne
```

---

## Czego CELLAR nie pokrywa — potrzebne osobne źródła

| Potrzeba | Źródło |
|---|---|
| Wytyczne EBA | eba.europa.eu API |
| Wytyczne ESMA | esma.europa.eu API |
| Wytyczne EIOPA | eiopa.europa.eu API |
| Q&A nadzorcze | ESA websites |
| Konsultacje publiczne | ESA websites |
| Stanowiska nadzorcze | ESA websites |
| Rejestry (MiCA, DORA) | ESA websites |

Te źródła wymagają osobnych wrapperów — CELLAR ich nie zastąpi.

---

## Dalsze kroki

1. **Implementacja biblioteki Python** (`cellar/`) — ~33 metody w 28 kategoriach powyżej
   - `cellar/client.py` — główna klasa `CellarClient` z publicznymi metodami
   - `cellar/sparql.py` — budowanie zapytań SPARQL
   - `cellar/parser.py` — parsowanie wyników JSON
   - `cellar/http.py` — komunikacja z endpointem SPARQL + REST
2. **CLI** — cienka warstwa na bibliotece
3. **Monitoring** — osobna biblioteka korzystająca z wrappera
4. **Osobny research** — API EBA/ESMA jeśli potrzebne
