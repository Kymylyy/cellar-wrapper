# CELLAR API — Raport z badania

## Czym jest CELLAR

CELLAR to centralne repozytorium treści i metadanych **Urzędu Publikacji Unii Europejskiej**. Przechowuje prawo UE, orzecznictwo, Dzienniki Urzędowe i inne publikacje. Dane są otwarte i dostępne publicznie — **bez rejestracji i autentykacji**.

## Sposoby dostępu

### REST API (HTTP GET)

Pobieranie dokumentów po identyfikatorze:

```
https://publications.europa.eu/resource/celex/{CELEX_NUMBER}
https://publications.europa.eu/resource/cellar/{UUID}
```

Content negotiation przez nagłówki HTTP:
- `Accept`: `application/pdf`, `application/xhtml+xml`, `application/xml`, `application/rdf+xml`, `application/zip;mtype=...`
- `Accept-Language`: kod ISO 639-3 (`pol`, `eng`, `fra`, ...)

Przykłady:

```bash
# PDF po polsku
curl -L -H "Accept: application/pdf" -H "Accept-Language: pol" \
  "https://publications.europa.eu/resource/celex/32015L2366" -o psd2_pl.pdf

# XHTML po angielsku
curl -L -H "Accept: application/xhtml+xml" -H "Accept-Language: eng" \
  "https://publications.europa.eu/resource/celex/32015L2366" -o psd2_en.xhtml

# Metadane RDF
curl -L -H "Accept: application/rdf+xml" \
  "https://publications.europa.eu/resource/celex/32015L2366" -o psd2_metadata.rdf
```

Dostępne formaty: PDF, HTML, XHTML, Formex (XML dla Dzienników Urzędowych), RDF/XML.

### SPARQL Endpoint

```
https://publications.europa.eu/webapi/rdf/sparql
```

Kluczowe prefiksy:

```sparql
PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>
PREFIX skos: <http://www.w3.org/2004/02/skos/core#>
PREFIX dc: <http://purl.org/dc/elements/1.1/>
PREFIX xsd: <http://www.w3.org/2001/XMLSchema#>
PREFIX owl: <http://www.w3.org/2002/07/owl#>
```

### RSS/Atom Feeds

Powiadomienia o nowych/zmienionych publikacjach.

### Bulk Download

- **Data dump**: `datadump.publications.europa.eu` (wymaga EU Login)
- **data.europa.eu**: Dzienniki Urzędowe w CSV z linkami do XML Formex

## Model danych (CDM + FRBR)

Struktura danych oparta na **FRBR** (Functional Requirements for Bibliographic Records) + **RDF Schema/OWL**.

Hierarchia: **Work → Expression → Manifestation → Item**

### Work (akt prawny jako koncept)

Pojedynczy rekord z metadanymi, relacjami prawnymi, datami i statusem.

### Expression (wersja językowa)

Dla każdego Work istnieje do 23 Expressions (oficjalne języki UE). Każda zawiera:
- `expression_title` — pełny tytuł w danym języku
- `expression_title_short` — np. "Payment Services Directive, psd 2, psd II"
- `expression_uses_language` — kod języka

### Manifestation (format pliku)

Dla każdej Expression typowo 3 manifestacje:

| Typ | Format | Opis |
|---|---|---|
| `pdfa1a` | PDF/A-1a | Archiwalny PDF |
| `fmx4` | Formex 4 XML | Strukturalny XML (treść + załączniki) |
| `xhtml` | XHTML | HTML do wyświetlania w przeglądarce |

Plus metadane OJ: numer strony, tom, podsekcja, trwałość.

### Item (fizyczny plik)

Konkretne pliki do pobrania z MIME type i pełnym URI.

Dokumentacja CDM: https://op.europa.eu/en/web/eu-vocabularies/cdm

## Pola dostępne na poziomie Work

Zbadane na przykładzie PSD2 (CELEX: `32015L2366`).

### Identyfikacja

| Pole CDM | Opis | Przykład PSD2 |
|---|---|---|
| `resource_legal_id_celex` | Numer CELEX | `32015L2366` |
| `resource_legal_eli` | European Legislation Identifier | `http://data.europa.eu/eli/dir/2015/2366/oj` |
| `work_id_document` | Identyfikatory (CELEX, OJ, IMMC) | `celex:32015L2366`, `oj:JOL_2015_337_R_0002` |
| `work_has_resource-type` | Typ dokumentu | `DIR` (dyrektywa) |
| `resource_legal_type` | Typ aktu (literal) | `L` |
| `resource_legal_number_natural` | Numer aktu | `2366` |
| `resource_legal_year` | Rok | `2015` |
| `resource_legal_id_sector` | Sektor CELEX | `3` (legislacja przyjęta) |
| `work_version` | Wersja | `final` |

### Daty

| Pole CDM | Opis | Przykład PSD2 |
|---|---|---|
| `work_date_document` | Data dokumentu | 2015-11-25 |
| `resource_legal_date_entry-into-force` | Wejście w życie | 2016-01-12 |
| `directive_date_transposition` | Termin transpozycji | 2018-01-13 |
| `resource_legal_date_deadline` | Deadline | 2021-01-13 |
| `resource_legal_date_end-of-validity` | Koniec ważności | 2026-06-18 |
| `work_date_creation_legacy` | Data publikacji OJ | 2015-12-23 |

### Status

| Pole CDM | Opis | Przykład PSD2 |
|---|---|---|
| `resource_legal_in-force` | Czy obowiązuje | `true` (1) |
| `resource_legal_eea` | Relevance dla EOG | `true` (1) |
| `resource_legal_codified_version` | Czy wersja skodyfikowana | `false` (0) |

### Instytucje

| Pole CDM | Opis | Przykład PSD2 |
|---|---|---|
| `work_created_by_agent` | Autorzy | EP (Parlament) + CONSIL (Rada) |
| `resource_legal_responsibility_of_agent` | DG odpowiedzialne | DG JUST + DG FISMA |
| `resource_legal_addresses_institution` | Adresaci | EUMS (Państwa Członkowskie) |
| `resource_legal_signatory_name2` | Podpisujący | M. Schulz, N. Schmit |

### Tematyka

| Pole CDM | Opis | Przykład PSD2 |
|---|---|---|
| `resource_legal_is_about_subject-matter` | Materia (authority codes) | Free movement of capital, Freedom of establishment, Internal market |
| `resource_legal_is_about_concept_directory-code` | Katalog | Free movement of capital, Banks |
| `work_is_about_concept_eurovoc` | Deskryptory EuroVoc | approximation of laws, single market, financial institution, service, financial services, payment, intra-EU payment, electronic money, financial legislation, electronic banking |

## Relacje prawne (graf)

### Relacje wychodzące z aktu (Work → inne)

| Pole CDM | Kierunek | Przykład PSD2 |
|---|---|---|
| `resource_legal_amends_resource_legal` | Co TEN akt zmienia | 32002L0065, 32009L0110, 32013L0036, 32010R1093 |
| `resource_legal_repeals_resource_legal` | Co TEN akt uchyla | 32007L0064 (PSD1) |
| `resource_legal_implicitly_repeals_resource_legal` | Co niejawnie uchyla | 32009L0111 |
| `resource_legal_based_on_concept_treaty` | Podstawa traktatowa | Art. 114 TFUE |
| `resource_legal_based_on_resource_legal` | Podstawa prawna | 12012E114 |
| `resource_legal_adopts_resource_legal` | Co przyjmuje (propozycję) | 52013PC0547 |
| `work_cites_work` | Co cytuje | 31 aktów |

### Relacje przychodzące (inne → Work)

Zbadane dla PSD2 — ilość obiektów wskazujących na PSD2:

| Pole CDM | Ile | Opis |
|---|---|---|
| `work_cites_work` | 283 | Akty cytujące PSD2 |
| `measure_national_implementing_implements_resource_legal` | 258 | Krajowe ustawy implementujące PSD2 |
| `act_consolidated_consolidates_resource_legal` | 22 | Teksty skonsolidowane |
| `resource_legal_based_on_resource_legal` | 14 | Akty delegowane/wykonawcze oparte na PSD2 |
| `act_consolidated_based_on_resource_legal` | 12 | Konsolidacje oparte na PSD2 |
| `communication_case_new_submits_preliminary_question_resource_legal` | 10 | Pytania prejudycjalne do TSUE |
| `resource_legal_corrects_resource_legal` | 7 | Sprostowania (corrigenda) |
| `resource_legal_completes_resource_legal` | 5 | Akty uzupełniające PSD2 |
| `case-law_interpretes_resource_legal` | 5 | Orzecznictwo TSUE interpretujące PSD2 |
| `resource_legal_proposes_to_amend_resource_legal` | 2 | Propozycje zmian |
| `resource_legal_amends_resource_legal` | 2 | Akty zmieniające PSD2 (DORA 32022L2556, IPR 32024R0886) |
| `resource_legal_implicitly_repeals_resource_legal` | 1 | PSD3 (32023L2673) niejawnie uchyla PSD2 |
| `dossier_contains_work` | 1 | Dossier procedury legislacyjnej |
| `summary_summarizes_work` / `summary_legislation_eu_summarizes_resource_legal` | 1 | Streszczenie EUR-Lex |
| `case-law_declares_valid_resource_legal` | 1 | Orzeczenie potwierdzające ważność |
| `dossier_produces_resource_legal` | 1 | Dossier → akt końcowy |
| `work_related_to_work` | 1 | Powiązany akt |
| `work_is_logical_successor_of_work` | 1 | Następca logiczny (tekst skonsolidowany) |
| `event_legal_contains_work` | 1 | Wydarzenie prawne |
| `owl:annotatedTarget` | 570 | Granularne adnotacje (artykuł-do-artykułu) |

## Szczegóły wybranych relacji

### proposes_to_amend — Propozycje zmian PSD2

| CELEX | Data | Typ | Tytuł |
|---|---|---|---|
| `52020PC0596` | 2020-09-24 | PROP_DIR | Propozycja DORA — zmieniająca m.in. PSD2, CRD IV, MiFID II |
| `52023PC0366` | 2023-06-28 | PROP_DIR | **Propozycja PSD3** — "on payment services and electronic money services... repealing Directives 2015/2366/EU and 2009/110/EC" |

### summary_summarizes — Streszczenie legislacyjne

Oficjalne streszczenie EUR-Lex (Summaries of EU Legislation):
- ID: `2404020302_1`, wersja 7.0.1
- Zwalidowane przez DG FISMA
- Drafted in English, ostatnia aktualizacja: 2024-11-09
- URI: `http://publications.europa.eu/resource/legissum/2404020302_1`
- Typ: `LEGIS_SUM`

### dossier_contains — Procedura legislacyjna 2013/0264/COD

Pełne dossier procedury OLP (zwykła procedura legislacyjna):

| Data | Typ | CELEX | Rola |
|---|---|---|---|
| 2013-07-24 | `PROP_DIR` | `52013PC0547` | Propozycja Komisji |
| 2013-07-24 | `SWD` | `52013SC0282` | Staff Working Document (ocena skutków) |
| 2013-12-05 | `NOTICE` | `52014XX0208(05)` | Zawiadomienie |
| 2013-12-11 | `OPIN` | `52013AE5238` | Opinia EKES |
| 2014-02-05 | `OPIN` | `52014AB0009` | Opinia EBC |
| 2014-04-03 | `RES_LEGIS` | `52014AP0280` | Stanowisko PE (1. czytanie) |
| 2015-10-08 | `RES_LEGIS` | `52015AP0346` | Stanowisko PE (2. czytanie) |
| 2015-10-30 | `ITEM_IA_NOTE` | — | Nota do Rady (punkt A) ×2 |
| 2015-11-10 | `ACT_LEGIS` | — | Akt legislacyjny |
| 2015-11-17 | `VOTING_RES` | — | Wynik głosowania w Radzie |
| 2015-11-25 | **`DIR`** | **`32015L2366`** | **PSD2 — przyjęta dyrektywa** |
| 2015-11-25 | `ACT_LEGIS` | — | Akt legislacyjny (sygnatura) |
| 2015-12-11 | `ACT_LEGIS` | — | Akt legislacyjny (publikacja) |

Metadane dossier:
- `dossier_identifier`: `procedure:2013_264`
- `procedure_code_interinstitutional_reference_procedure`: `2013/0264/COD`
- `dossier_adopted-proposal`: 1
- `dossier_pending-proposal`: 0
- `dossier_withdrawn-proposal`: 0
- `dossier_initiated_by_act_preparatory`: `52013PC0547`
- `dossier_produces_resource_legal`: `32015L2366`
- `procedure_code_interinstitutional_has_type`: OLP

### is_logical_successor — Następca logiczny

| CELEX | Typ | Data |
|---|---|---|
| `02015L2366-20240408` | `CONS_TEXT` | 2024-04-08 |

Tekst skonsolidowany PSD2 na dzień 8 kwietnia 2024 (po zmianach DORA i IPR).

### annotatedTarget — Adnotacje granularne (570 sztuk)

Relacje na poziomie artykułów. OWL Axiom Annotations łączą np. konkretny artykuł ustawy krajowej z konkretnym artykułem PSD2. Większość to `measure_national_implementing_implements_resource_legal` — krajowe ustawy wskazujące który artykuł PSD2 implementują.

## Warianty CELEX dla jednego aktu

| Prefiks | Znaczenie | Przykłady PSD2 |
|---|---|---|
| `3` | Legislacja przyjęta | `32015L2366` |
| `3...R(xx)` | Sprostowania | `32015L2366R(01)` do `R(07)` — 7 sprostowań |
| `0` | Teksty skonsolidowane | `02015L2366-20151223`, `02015L2366-20240408`, `02015L2366-20250117` |
| `7` | Krajowe środki implementujące | `72015L2366POL_258600`, `72015L2366DEU_253864`, ... — ~230+ |
| `5` | Dokumenty przygotowawcze | `52013PC0547` (propozycja), `52023PC0366` (propozycja PSD3) |

## Przykładowe zapytania SPARQL

### Znajdź akt po CELEX i pobierz jego URI

```sparql
PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>

SELECT ?work WHERE {
  ?work cdm:resource_legal_id_celex '32015L2366' .
}
```

### Znajdź akty zmieniające dany akt

```sparql
PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>

SELECT DISTINCT ?amendingWork ?celex ?date WHERE {
  ?amendingWork cdm:resource_legal_amends_resource_legal <CELLAR_URI> .
  OPTIONAL { ?amendingWork cdm:resource_legal_id_celex ?celex }
  OPTIONAL { ?amendingWork cdm:work_date_document ?date }
}
ORDER BY ?date
```

### Znajdź akty uchylające (jawnie i niejawnie)

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

### Znajdź propozycje zmian

```sparql
PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>

SELECT ?work ?celex ?date WHERE {
  ?work cdm:resource_legal_proposes_to_amend_resource_legal <CELLAR_URI> .
  OPTIONAL { ?work cdm:resource_legal_id_celex ?celex }
  OPTIONAL { ?work cdm:work_date_document ?date }
}
```

### Pobierz dossier (pełną procedurę legislacyjną)

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

### Pobierz wersje językowe (Expressions)

```sparql
PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>

SELECT ?expression ?lang ?title WHERE {
  ?expression cdm:expression_belongs_to_work <CELLAR_URI> .
  OPTIONAL { ?expression cdm:expression_uses_language ?lang }
  OPTIONAL { ?expression cdm:expression_title ?title }
}
ORDER BY ?lang
```

### Pobierz wszystkie relacje przychodzące (kto wskazuje na dany akt)

```sparql
PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>

SELECT DISTINCT ?prop (COUNT(?other) as ?count) WHERE {
  ?other ?prop <CELLAR_URI> .
}
GROUP BY ?prop
ORDER BY DESC(?count)
```

---

# DEEP DIVE: Orzecznictwo TSUE dotyczące PSD2

## Wyroki interpretujące PSD2

5 wyroków TSUE formalnie interpretujących PSD2:

| CELEX | ECLI | Data | Sprawa | Izba |
|---|---|---|---|---|
| `62016CJ0643` | ECLI:EU:C:2018:67 | 2018-02-07 | **American Express v HM Treasury** — systemy kart trzystronnych, co-branding, ważność art. 35 PSD2 | Izba I |
| `62018CJ0778` | ECLI:EU:C:2020:831 | 2020-10-15 | **Association française des usagers de banques v Ministre** — wypowiedzenie umów ramowych (art. 55), wiązanie z umowami kredytowymi | Izba V |
| `62019CJ0287` | ECLI:EU:C:2020:897 | 2020-11-11 | **DenizBank v Verein für Konsumenteninformation** — pojęcie "instrumentu płatniczego" (art. 4(14)), NFC, dorozumiana zgoda | Izba I |
| `62020CJ0484` | ECLI:EU:C:2021:975 | 2021-12-02 | **Vodafone Kabel Deutschland v Verbraucherzentralen** — opłaty za transakcje (art. 62(4)), pełna harmonizacja (art. 107(1)) | Izba IX |
| `62022CJ0661` | ECLI:EU:C:2024:148 | 2024-02-22 | **'ABC Projektai' v Lietuvos bankas** — definicja usługi płatniczej (art. 4(3) i (5)), przechowywanie środków klienta | Izba V |

## Pytania prejudycjalne (10 spraw)

| CELEX | Data | Status | Sprawa |
|---|---|---|---|
| `62016CN0643` | 2016-12-12 | Rozstrzygnięta | American Express (UK) |
| `62018CN0778` | 2018-12-11 | Rozstrzygnięta | Usagers de banques (Francja) |
| `62019CN0287` | 2019-04-05 | Rozstrzygnięta | DenizBank (Austria) |
| `62020CN0484` | 2020-10-01 | Rozstrzygnięta | Vodafone (Niemcy) |
| `62021CN0448` | 2021-07-21 | **Usunięta** | Portugalia — Banco BPI |
| `62022CN0661` | 2022-10-20 | Rozstrzygnięta | Bruc Bond (Litwa) |
| **`62025CN0051`** | 2025-01-28 | **Oczekująca** | Betaal Garant v De Nederlandsche Bank (Holandia) |
| **`62025CN0070`** | 2025-02-03 | **Oczekująca** | N.O. v PKO BP S.A. (Polska!) |
| **`62025CN0274`** | 2025-04-10 | **Oczekująca** | Alternative Payments v Lietuvos bankas (Litwa) |
| **`62025CN0339`** | 2025-05-17 | **Oczekująca** | Iulicris Recycling v Ibanfirst (Belgia) |

## Orzeczenie o ważności

C-643/16 (American Express) — TSUE potwierdził ważność art. 35(1) i (2)(b) PSD2.

## Opinie Rzeczników Generalnych

| CELEX | Data | Rzecznik | Sprawa |
|---|---|---|---|
| `62018CC0778` | 2020-02-27 | Saugmandsgaard Øe | C-778/18 |
| `62019CC0287` | 2020-04-30 | Campos Sánchez-Bordona | C-287/19 (DenizBank) |
| `62022CC0661` | 2023-10-05 | Campos Sánchez-Bordona | C-661/22 (ABC Projektai) |

## Pola dostępne na orzeczeniach (zbadane na C-287/19)

Pola specyficzne dla case-law (`cdm:case-law_*`):
- `case-law_ecli` — identyfikator ECLI
- `case-law_has_procjur` — typ procedury (REFER_PREL = pytanie prejudycjalne)
- `case-law_delivered_by_court-formation` — skład sądu (izba)
- `case-law_delivered_by_judge` — sędzia sprawozdawca
- `case-law_delivered_by_advocate-general` — rzecznik generalny
- `case-law_interpretes_resource_legal` — jakie akty interpretuje
- `case-law_declares_valid_resource_legal` — jakie akty uznaje za ważne
- `case-law_originates_in_country` — kraj pytającego sądu
- `case-law_uses_procedure_language` — język postępowania
- `case-law_national-judgement` — wyrok sądu krajowego (follow-up)
- `case-law_commented_by_agent` — kto składał uwagi (Komisja, rządy)
- `case-law_article_journal_related` — artykuły naukowe omawiające wyrok
- `case-law_published_in_erecueil` — czy opublikowany w ECR

---

# DEEP DIVE: Akty delegowane i wykonawcze oparte na PSD2

## Rozporządzenia delegowane (RTS)

| CELEX | Data | Tytuł | In-force |
|---|---|---|---|
| `32017R2055` | 2017-06-23 | RTS — współpraca i wymiana informacji między organami nadzoru (art. 28(5)) | Tak |
| `32018R0389` | 2017-11-27 | **RTS SCA/CSC** — silne uwierzytelnianie klienta i bezpieczna komunikacja (art. 98(4)) | Tak |
| `32019R0411` | 2018-11-29 | RTS — elektroniczny rejestr centralny (art. 15(4)) | Tak |
| `32020R1423` | 2019-03-14 | RTS — centralne punkty kontaktowe (art. 29(7)) | Tak |
| `32021R1722` | 2021-07-18 | RTS — współpraca transgraniczna w nadzorze (art. 29(7)) | Tak |
| `32022R2360` | 2022-08-03 | Zmiana RTS SCA — zwolnienie 90-dniowe dla dostępu do konta | Tak |
| `32023R1650` | 2023-08-15 | Korekta szwedzkiej wersji RTS SCA | Tak |
| `32025R0212` | 2024-09-13 | Korekta RTS 2017/2055 | Tak |

## Rozporządzenie wykonawcze (ITS)

| CELEX | Data | Tytuł | In-force |
|---|---|---|---|
| `32019R0410` | 2018-11-29 | ITS — szczegóły i struktura informacji notyfikowanych do EBA (art. 15(5)) | Tak |

## Raport Komisji

| CELEX | Data | Tytuł |
|---|---|---|
| `52023DC0365` | 2023-06-28 | Raport z przeglądu Dyrektywy 2015/2366 (podstawa do PSD3) |

## Teksty skonsolidowane PSD2

| CELEX | Data | Opis |
|---|---|---|
| `02015L2366-20151223` | 2015-12-23 | Wersja oryginalna |
| `02015L2366-20240408` | 2024-04-08 | Po zmianach DORA i IPR |
| `02015L2366-20250117` | 2025-01-17 | **Najnowsza** wersja skonsolidowana |

## Teksty skonsolidowane aktów zmienionych przez PSD2

| CELEX | Data | Akt |
|---|---|---|
| `02010R1093-20160112` | 2016-01-12 | Rozporządzenie o EBA |
| `02013L0036-20180113` | 2018-01-13 | CRD IV |
| `02013L0036-20220101` | 2022-01-01 | CRD IV (nowsza) |
| `02009L0110-20180113` | 2018-01-13 | Dyrektywa o pieniądzu elektronicznym (EMD2) |
| `02002L0065-20180113` | 2018-01-13 | Dyrektywa o marketingu usług finansowych na odległość |

---

# DEEP DIVE: Krajowe środki implementujące PSD2

## Statystyki wdrożenia wg kraju

258 krajowych środków implementujących w 28 państwach:

| Kraj | Ile | Linki do stron | | Kraj | Ile | Linki |
|---|---|---|---|---|---|---|
| Czechy | 73 | 0 | | Holandia | 8 | 0 |
| Litwa | 21 | 0 | | Cypr | 7 | 0 |
| Węgry | 21 | 0 | | Polska | 7 | 0 |
| Słowacja | 14 | 0 | | Słowenia | 6 | 5 |
| Francja | 13 | 0 | | Malta | 6 | 0 |
| Estonia | 11 | **11** | | Chorwacja | 5 | 0 |
| Łotwa | 11 | **9** | | Rumunia | 4 | 0 |
| Finlandia | 10 | 0 | | Dania | 4 | 0 |
| Szwecja | 9 | 0 | | Bułgaria | 4 | 1 |

Plus: UK (4), Grecja (3), Hiszpania (3), Włochy (3), Belgia (2), Portugalia (2), Irlandia (2), Niemcy (2), Austria (2), Luksemburg (1).

**Uwaga**: Czechy (73) mają zawyżoną liczbę — ustawa omnibus Zákon č. 183/2017 Sb. deklaruje transpozycję 224 dyrektyw jednocześnie.

## Dostępne pola na NIM-ach

| Pole CDM | Pokrycie | Opis |
|---|---|---|
| `work_title` (w języku krajowym) | 100% | Tytuł ustawy krajowej |
| `measure_national_implementing_date_notification` | 100% | Data notyfikacji Komisji |
| `measure_national_implementing_type_act` | 100% | Typ aktu krajowego |
| `measure_national_implementing_name_official_journal` | 99.6% | Nazwa dziennika urzędowego |
| `measure_national_implementing_reference_member-state` | 64% | Krajowa sygnatura |
| `resource_legal_date_entry-into-force` | 46% | Data wejścia w życie |
| `measure_national_implementing_national_website_link` | **10%** | Link do tekstu |
| `resource_legal_eli` | 2.3% | Identyfikator ELI |

**Kluczowe odkrycie**: Property to `measure_national_implementing_implemented_by_country` (NIE `adopted_by_country`).

## Polskie NIM-y (7 sztuk)

| CELEX | Tytuł | Typ | Dz.U. |
|---|---|---|---|
| `72015L2366POL_258600` | Ustawa z 22.03.2018 o zmianie ustawy o usługach płatniczych | Nowelizacja | DzU 2018/864 |
| `72015L2366POL_259382` | Ustawa z 10.05.2018 o zmianie ustawy o usługach płatniczych | Nowelizacja | DzU 2018/1075 |
| `72015L2366POL_259466` | Rozporządzenie MF z 06.06.2018 ws. metody obliczania kwoty | Rozporządzenie | DzU 2018/1110 |
| `72015L2366POL_259467` | Ustawa z 19.08.2011 o usługach płatniczych (t.j.) | Ustawa | DzU 2017/2003 |
| `72015L2366POL_259472` | Ustawa z 10.05.2018 o ochronie danych osobowych | Ustawa | DzU 2018/1000 |
| `72015L2366POL_202101589` | Ustawa z 21.01.2021 o zmianie ustawy o obrocie instrumentami | Nowelizacja | DzU 2021/355 |
| `72015L2366POL_202401176` | Ustawa z 16.08.2023 o zmianie niektórych ustaw (rynek finansowy) | Nowelizacja | DzU 2023/1723 |

---

# DEEP DIVE: Porównanie typów aktów w CELLAR

## Skala danych w CELLAR

| Typ | Ilość | Opis |
|---|---|---|
| `PROCUREMENT_NOTICE` | 1,911,563 | Ogłoszenia przetargowe |
| `MEAS_NATION_IMPL` | 196,630 | Krajowe środki implementujące |
| `REG` | 144,952 | Rozporządzenia |
| `CONS_TEXT` | 73,357 | Teksty skonsolidowane |
| `JUDG` | 33,739 | Wyroki TSUE |
| `DEC` | 23,917 | Decyzje |
| `REG_IMPL` | 14,643 | Rozporządzenia wykonawcze |
| `PROP_REG` | 13,825 | Propozycje rozporządzeń |
| `DIR` | 7,733 | Dyrektywy |
| `PROP_DIR` | 3,197 | Propozycje dyrektyw |

## Hierarchia typów RDF

| Typ aktu | Klasy RDF |
|---|---|
| Rozporządzenie | `cdm:regulation` > `cdm:legislation_secondary` > `cdm:resource_legal` > `cdm:work` |
| Dyrektywa | `cdm:directive` > `cdm:legislation_secondary` > `cdm:resource_legal` > `cdm:work` |
| Wyrok | `cdm:judgement` + `cdm:case-law` + `cdm:document_cjeu` > `cdm:resource_legal` > `cdm:work` |
| Propozycja | `cdm:act_preparatory` > `cdm:work` (NIE dziedziczy z `legislation_secondary`!) |

## Porównanie pól wg typu aktu

| Typ | Wszystkie pola | Unikalne pola | Wspólne z innymi |
|---|---|---|---|
| Rozporządzenie (REG) | 121 | 16 | 31 |
| Dyrektywa (DIR) | 108 | 3 | 31 |
| Wyrok (JUDG) | 72 | 38 | 31 |
| Propozycja (PROP_DIR) | 74 | 12 | 31 |

### Pola unikalne dla dyrektyw (nie ma ich na rozporządzeniach)

- **`directive_date_transposition`** — termin transpozycji (kluczowa różnica!)
- `resource_legal_addresses_institution` → EUMS

### Pola unikalne dla rozporządzeń (nie ma ich na dyrektywach)

`suspends`, `defers_application_of`, `reestablishes`, `incorporates`, `partially_suspends`, `renders_obsolete` — rozporządzenia mają bogatszy słownik relacji operacyjnych (bo są bezpośrednio stosowalne).

### Pola unikalne dla wyroków (38 pól `case-law_*`)

Zupełnie osobny model: `ecli`, `delivered_by_judge`, `delivered_by_advocate-general`, `court-formation`, `interpretes_resource_legal`, `declares_valid/void`, `originates_in_country`, `procedure_language`, `national-judgement`, `article_journal_related`.

### Pola unikalne dla propozycji

`proposes_to_amend_resource_legal`, `act_preparatory_initiates_dossier`, `date_dispatch`, `service_responsible`, `work_part_of_dossier`.

---

# DEEP DIVE: Adnotacje OWL i EuroVoc

## Struktura adnotacji OWL

CELLAR używa **OWL Annotation Axioms** (reifikacja) do kwalifikowania relacji. Zamiast prostego trójkowego `A → relacja → B`, tworzy:

```
_:annotation  owl:annotatedSource   <akt_źródłowy>
_:annotation  owl:annotatedProperty <cdm:relacja>
_:annotation  owl:annotatedTarget   <PSD2>
_:annotation  <kwalifikator>        <wartość>
```

## Typy adnotacji (570 sztuk dla PSD2)

| Relacja | Ile | Opis |
|---|---|---|
| `measure_national_implementing_implements` | 258 | Transpozycja krajowa |
| `work_cites_work` | 233 | Cytowania |
| `communication_case_new_submits_preliminary_question` | 30 | Pytania prejudycjalne |
| `resource_legal_amends` | 13 | Zmiany legislacyjne |
| `case-law_interpretes` | 10 | Interpretacje TSUE |
| `resource_legal_based_on` | 9 | Akty delegowane/wykonawcze |
| `resource_legal_corrects` | 7 | Sprostowania |
| `resource_legal_completes` | 5 | Akty uzupełniające |
| `resource_legal_proposes_to_amend` | 2 | Propozycje zmian |
| `case-law_declares_valid` | 1 | Potwierdzenie ważności |
| `resource_legal_implicitly_repeals` | 1 | Niejawne uchylenie |
| `work_related_to_work` | 1 | Powiązanie ogólne |

## Kwalifikatory (granularność artykuł-po-artykule)

| Kwalifikator | Opis | Przykład |
|---|---|---|
| `annotation:article` | Numer artykułu PSD2 | `"98"`, `"15"` |
| `annotation:paragraph` | Paragraf | `"4"`, `"5"` |
| `annotation:subparagraph` | Ustęp | `"2"`, `"3"` |
| `annotation:comment_on_legal_basis` | Zakodowana lokalizacja | `"A98P4L2"` |
| `annotation:fragment_cited_target` | Fragment docelowy | `"A24P1"` |
| `annotation:fragment_citing_source` | Fragment źródłowy | `"N 53"` |
| `annotation:start_of_validity` | Początek obowiązywania zmiany | `"2023-01-16"` |
| `annotation:transposition_deadline_transmitted` | Termin transpozycji | `"2018-01-13"` |
| `annotation:transposition_notification` | Data notyfikacji | `"2019-04-08"` |

### Artykuły PSD2 kwestionowane przez sądy krajowe

Art. 4(3), 4(5), 4(14), 35(1), 35(2)(b), 52(6)(a), 54(1), 55, 61(1), 62(4), 63(1)(b), 71, 72, 73, 73(1), 74, Załącznik I(3)(c).

### Artykuły PSD2 będące podstawą aktów delegowanych

| Akt delegowany | Artykuł PSD2 | Kod |
|---|---|---|
| RTS SCA (32018R0389) | Art. 98(4) ust. 2 | `A98P4L2` |
| RTS rejestr (32019R0411) | Art. 15(4) ust. 3 | `A15P4L3` |
| ITS (32019R0410) | Art. 15(5) ust. 3 | `A15P5L3` |
| RTS współpraca (32017R2055) | Art. 28(5) | `A28P5` |
| RTS punkty kontaktowe (32020R1423) | Art. 29(7) | `A29P7` |
| RTS nadzór transgraniczny (32021R1722) | Art. 29(7) | `A29P7` |

### Artykuły PSD2 zmienione przez DORA i IPR

- **DORA** (32022L2556, od 2023-01-16): Art. 3(j), 5(1), 19(6), 95(1), 96(7), 98(5)
- **IPR** (32024R0886, od 2024-04-08): Art. 35(2), 35(3), 35a

## Hierarchia EuroVoc

PSD2 ma 10 deskryptorów EuroVoc:

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

## Legislacja tematycznie podobna (wg EuroVoc overlap)

| Overlap | CELEX | Akt |
|---|---|---|
| 8/10 | `52023PC0367` | **Propozycja PSD3** |
| 7/10 | `32019R0518` | Rozporządzenie o płatnościach transgranicznych |
| 7/10 | `52024AB0013` | Opinia EBC o PSD3/PSR |
| 7/10 | `52023AE3611` | Opinia EKES o PSD3 |
| 7/10 | `22024D0126` | Decyzja EOG dot. włączenia PSD2 do Aneksu IX |

---

## Istniejące narzędzia klienckie

- **R**: pakiet [`eurlex`](https://michalovadek.github.io/eurlex/) — `elx_make_query()`, `elx_run_query()`, `elx_fetch_data()`. Pokrywa płaskie listy aktów i podstawowe metadane, ale **nie** obsługuje nawigacji po grafie relacji (amends, repeals, based_on itp.).
- **SPARQL editor**: https://op.europa.eu/en/advanced-sparql-query-editor

---

# Streszczenie legislacyjne (Summary) PSD2

## Metadane streszczenia

| Pole | Wartość |
|---|---|
| **Legissum ID** | `2404020302_1` |
| **CELLAR URI** | `http://publications.europa.eu/resource/cellar/cfa37481-8548-4f70-8d8e-713ac6dfb151` |
| **Typ** | `LEGIS_SUM` (Summary of EU Legislation) |
| **Wersja** | 7.0.1 |
| **Drafted in** | English |
| **Zwalidowane przez** | DG FISMA |
| **Utworzone** | 2016-06-28 |
| **Ostatnia aktualizacja** | 2024-11-09 |
| **Obsolete** | Nie |
| **Klasyfikacja** | `090406`, `14090302` |
| **Autor** | PUBL (Urząd Publikacji) |

## Wersje językowe streszczenia (24 języki)

| Język | Tytuł |
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

## Pobieranie treści streszczenia

Streszczenia mają manifestacje `fmx4` (XML) i `xhtml5` (HTML). Pobranie wymaga **dokładnego MIME type** `application/xhtml+xml;type=xhtml5`:

```bash
# Pobierz streszczenie PSD2 w HTML (angielski)
curl -L -H "Accept: application/xhtml+xml;type=xhtml5" \
  "http://publications.europa.eu/resource/cellar/cfa37481-8548-4f70-8d8e-713ac6dfb151.0006.04/DOC_1" \
  -o psd2_summary_en.html
```

**Uwaga**: Standardowe `Accept: application/xhtml+xml` zwraca błąd 406. Trzeba użyć `application/xhtml+xml;type=xhtml5`.

Treść (~11 000 znaków) zawiera sekcje: SUMMARY OF, WHAT IS THE AIM, KEY POINTS, FROM WHEN DOES THE DIRECTIVE APPLY, BACKGROUND, KEY TERMS, MAIN DOCUMENT, RELATED DOCUMENTS.

---

# Wydarzenie prawne (event_legal) PSD2

| Pole | Wartość |
|---|---|
| **Typ** | `PUB_OJ` (Publikacja w Dzienniku Urzędowym) |
| **Data** | 2015-12-23 |
| **Dossier** | `http://publications.europa.eu/resource/cellar/900c24d5-f5ca-11e2-a22e-01aa75ed71a1` (procedura 2013/0264/COD) |
| **Identyfikator** | `procedure-event/2013_264.2015-12-23_PUB_OJ` |
| **Utworzone w systemie** | 2020-08-21 |
| **Ostatnia modyfikacja** | 2025-03-17 |

---

## Źródła

- https://op.europa.eu/en/web/cellar/cellar-data
- https://publications.europa.eu/webapi/rdf/sparql
- https://eur-lex.europa.eu/content/help/data-reuse/reuse-contents-eurlex-details.html
- https://michalovadek.github.io/eurlex/
- https://cran.r-project.org/web/packages/eurlex/vignettes/sparql-queries.html
- https://op.europa.eu/en/web/eu-vocabularies/cdm
- https://data.europa.eu/data/datasets/sparql-cellar-of-the-publications-office?locale=en
