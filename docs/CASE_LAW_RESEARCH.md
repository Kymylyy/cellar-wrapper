# Orzecznictwo w CELLAR — TSUE vs sądy krajowe

## Typy orzecznicze w CELLAR

| Typ | Ilość | Opis |
|---|---|---|
| **INFO_JUDICIAL** | 69,718 | Informacje sądowe (metadane proceduralne) |
| **DEC_NC** | 35,773 | **Wyroki sądów krajowych** w kontekście prawa UE |
| **DEC_ENTSCHEID** | 33,751 | Decyzje (duplikat JUDG w innym formacie?) |
| **JUDG** | 33,739 | **Wyroki TSUE** |
| **SUM_JUR** | 24,443 | Streszczenia orzeczeń |
| **CASE_LAW** | 15,252 | Raporty z orzecznictwa |
| **OPIN_AG** | 14,360 | **Opinie Rzeczników Generalnych** |
| **ORDER** | 8,260 | Postanowienia TSUE |

---

## TSUE (JUDG) — model danych

Zbadany na przykładzie **C-287/19 DenizBank** (wyrok interpretujący PSD2).

### Pola specyficzne dla wyroków TSUE

| Pole CDM | Opis | Przykład |
|---|---|---|
| `case-law_ecli` | Identyfikator ECLI | `ECLI:EU:C:2020:897` |
| `case-law_has_procjur` | Typ procedury | `REFER_PREL` (pytanie prejudycjalne) |
| `case-law_delivered_by_court-formation` | Skład sądu | `CHAMB_01_C` (Izba I) |
| `case-law_delivered_by_judge` | Sędzia sprawozdawca | (cellar URI) |
| `case-law_delivered_by_advocate-general` | Rzecznik Generalny | Campos Sánchez-Bordona |
| `case-law_interpretes_resource_legal` | **Jakie akty interpretuje** | PSD2 + Klausel-RL |
| `case-law_declares_valid_resource_legal` | Jakie akty uznaje za ważne | — |
| `case-law_originates_in_country` | Kraj pytającego sądu | AUT (Austria) |
| `case-law_uses_procedure_language` | Język postępowania | DEU (niemiecki) |
| `case-law_commented_by_agent` | Kto składał uwagi | COM, PRT, CZE |
| `case-law_published_in_erecueil` | Czy w ECR | 1 (tak) |
| `case-law_has_conclusions_opinion_advocate-general` | Link do opinii AG | (cellar URI) |
| `case-law_is_about_concept_new_case-law` | Klasyfikacja tematyczna | `4.11.12.03` |

### Pola unikalne — niedostępne na innych typach

| Pole | Wartość dla monitoringu |
|---|---|
| **`case-law_national-judgement`** | Wyroki krajowe będące follow-up (z ECLI!) |
| **`case-law_article_journal_related`** | Artykuły naukowe omawiające wyrok |

### Przykład `case-law_article_journal_related` (C-287/19 DenizBank)

6 artykułów naukowych zarejestrowanych w CELLAR:

1. Bassani: "Protection des consommateurs - Services de paiement" (Europe 2021)
2. Rodi: "Keine Haftungserleichterung für Bank beim kontaktlosen Zahlen" (EWR 2020)
3. Steennot: "Gebruik van NFC-technologie zonder geheime code" (RDCB 2021)
4. Prankl: "Zustimmungsfiktionsklauseln in Zahlungsdienste-Rahmenverträgen" (Ecolex 2021)
5. Hoffmann/Rastegar: "Kontaktlose Zahlungen im Privatrecht" (WM 2021)
6. Fornasier: "Die Anwendung der Klauselrichtlinie" (EuZW 2021)

**Odkrycie:** CELLAR przechowuje **referencje do artykułów naukowych** omawiających wyroki TSUE. To ogromna wartość dla monitoringu — daje kontekst akademicki.

### Przykład `case-law_national-judgement` (C-287/19)

```
*A9* Oberster Gerichtshof, Beschluss vom 25/01/2019 (8 Ob 24/18i)
*P1* Oberster Gerichtshof, Fünfersenat, Urteil vom 25/03/2021
     (ECLI:AT:OGH0002:2021:0080OB00105.20D.0325.000)
```

`*A9*` = sąd pytający, `*P1*` = wyrok follow-up po odpowiedzi TSUE.

### Jak monitorować nowe wyroki TSUE dot. danego aktu

```sparql
PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>

# Nowe wyroki interpretujące PSD2
SELECT ?celex ?ecli ?date ?country WHERE {
  ?work cdm:case-law_interpretes_resource_legal <CELLAR_URI_AKTU> .
  ?work cdm:resource_legal_id_celex ?celex .
  ?work cdm:case-law_ecli ?ecli .
  OPTIONAL { ?work cdm:work_date_document ?date }
  OPTIONAL { ?work cdm:case-law_originates_in_country ?country }
}
ORDER BY DESC(?date)
```

```sparql
# Nowe pytania prejudycjalne dot. PSD2
SELECT ?celex ?date ?country WHERE {
  ?work cdm:communication_case_new_submits_preliminary_question_resource_legal <CELLAR_URI_AKTU> .
  ?work cdm:resource_legal_id_celex ?celex .
  OPTIONAL { ?work cdm:work_date_document ?date }
  OPTIONAL { ?work cdm:case-law_originates_in_country ?country }
}
ORDER BY DESC(?date)
```

---

## DEC_NC (sądy krajowe) — model danych

35,773 wyroków sądów krajowych w kontekście prawa UE.

### Dystrybucja geograficzna (top 15)

| Kraj | Ilość | Sądy przykładowe |
|---|---|---|
| **DEU** (Niemcy) | 7,815 | BGH, OLG Stuttgart, OLG München, LG Ulm |
| **FRA** (Francja) | 4,580 | Cour de cassation, Cour d'appel |
| **ITA** (Włochy) | 3,642 | — |
| **NLD** (Holandia) | 3,359 | — |
| **BEL** (Belgia) | 2,874 | — |
| **ESP** (Hiszpania) | 1,979 | — |
| **GBR** (UK) | 1,841 | (pre-Brexit) |
| **AUT** (Austria) | 1,574 | OGH |
| **GRC** (Grecja) | 1,062 | — |
| **LUX** (Luksemburg) | 637 | Cour d'appel Luxembourg |
| **PRT** (Portugalia) | 630 | — |
| **DNK** (Dania) | 434 | — |
| **IRL** (Irlandia) | 402 | — |
| **SWE** (Szwecja) | 392 | — |
| **CZE** (Czechy) | 327 | — |
| **POL** (Polska) | **286** | **Sąd Najwyższy** |

### Pola specyficzne DEC_NC

| Pole CDM | Pokrycie | Opis |
|---|---|---|
| `case-law_originates_in_country` | 96% | Kraj sądu |
| `work_title` | 96% | Identyfikator (np. "OLG Stuttgart; 2021-01-15; 5 U 11/20") |
| `case-law_national_keywords` | 51,278 | Słowa kluczowe (XML, wielojęzyczne) |
| `case-law_article_journal_related` | 33,075 | Artykuły naukowe omawiające wyrok |
| `resource_legal_uses_originally_language` | 86% | Język orzeczenia |
| `case-law_is_about_concept_case-law` | 29,107 | Klasyfikacja tematyczna |
| `case-law_national_decision_internal_identifier` | 81% | Krajowy numer sprawy |
| `case-law_national_act_reference_national` | 23,136 | Referencje do prawa krajowego |
| **`case-law_national_act_reference_european`** | **19,781** | **Referencje do prawa UE (z artykułem!)** |
| `case-law_national_reference_publication` | 19,154 | Gdzie opublikowany |
| `case-law_ecli` | var. | ECLI krajowego orzeczenia |
| `case-law_national_follow-up` | 8,744 | Follow-up do wyroku TSUE |
| `case-law_national_judgement_reference` | 12,270 | Referencja do wyroku TSUE |
| `case-law_national_parties` | var. | Strony (zazwyczaj anonimizowane) |

### Format `case-law_national_act_reference_european`

Referencje do prawa UE z **precyzją na artykuł**:

```
32015L2366-A04PT21     → PSD2, Art. 4 pkt 21
32007L0064-A65P2       → PSD1, Art. 65(2)
32012R0650-A21         → Succession Reg, Art. 21
32016R0679-A17         → GDPR, Art. 17
12016E267-P2           → TFUE, Art. 267(2)
```

Format: `{CELEX}-A{artykuł}P{paragraf}PT{punkt}L{ustęp}`

### Przykład pełnego rekordu DEC_NC

**82021DE0115(51)** — OLG Stuttgart, 15.01.2021, 5 U 11/20

| Pole | Wartość |
|---|---|
| ECLI | `ECLI:DE:OLGSTUT:2021:0115.5U11.20.00` |
| Kraj | Niemcy |
| Sąd | OLG Stuttgart (cellar URI) |
| Język | niemiecki |
| Temat | COJC (sądownictwo cywilne) |
| Prawo krajowe | BGB §675c(1)(2), §675f(2), §823; GlüStV §4(1) |
| **Prawo UE** | **PSD2 Art. 4 pkt 21** + 22 innych referencji (wyroki TSUE, rozporządzenia) |
| Sąd I instancji | LG Ulm, 16.12.2019, 4 O 202/18 |

### Przykład polskiego DEC_NC

**82025PL0509(51)** — Sąd Najwyższy, 09.05.2025, II CSKP 468/23

| Pole | Wartość |
|---|---|
| Kraj | Polska |
| Sąd | Sąd Najwyższy (cellar URI) |
| Język | polski |
| Prawo krajowe | Konstytucja RP art. 89-91, 241; KPC art. 13§2, 108§2, 243¹, 328§2, 385, 387§2¹, 391§1, 398³§1 pkt 2, 398¹³§2, 398¹⁵§1 |
| Prawo UE | Reg. 650/2012 (succession) — 11 artykułów, TFUE art. 288(1) |
| Strony | J. R. (anonimizowane) |

---

## Porównanie JUDG vs DEC_NC

| Aspekt | JUDG (TSUE) | DEC_NC (sądy krajowe) |
|---|---|---|
| **Ilość** | 33,739 | 35,773 |
| **Link do aktu UE** | `case-law_interpretes_resource_legal` (CELLAR URI) | `case-law_national_act_reference_european` (CELEX+artykuł string) |
| **Siła linkowania** | **Silne** — bezpośredni link URI | **Słabe** — string match, 56% pokrycie |
| **Artykuły naukowe** | Tak (6 dla DenizBank) | Tak (33k ogółem) |
| **ECLI** | Zawsze | Często |
| **Klasyfikacja** | `case-law_is_about_concept_new_case-law` | `case-law_is_about_concept_case-law` |
| **Procedura** | `case-law_has_procjur` (REFER_PREL, itp.) | Brak |
| **Follow-up** | `case-law_national-judgement` | `case-law_national_follow-up` (8,744) |
| **Kraj** | `case-law_originates_in_country` (kraj pytający) | `case-law_originates_in_country` (kraj sądu) |
| **Prawo krajowe** | Brak | `case-law_national_act_reference_national` (23k) |
| **Monitorowalność** | **Wysoka** | **Średnia** (wymaga string match na CELEX) |

---

## Wyniki wyszukiwania: PSD2 w orzecznictwie

### TSUE — 5 wyroków + 10 pytań prejudycjalnych

(Szczegóły w CELLAR_API_RESEARCH.md)

### DEC_NC referujące PSD1/PSD2 — 3 wyroki

| Data | Kraj | CELEX | Sąd | Referencja |
|---|---|---|---|---|
| 2019-12-16 | DEU | `82019DE1216(51)` | LG Ulm, 4 O 202/18 | PSD1 Art. 65(2) |
| 2021-01-15 | DEU | `82021DE0115(51)` | OLG Stuttgart, 5 U 11/20 | **PSD2 Art. 4 pkt 21** |
| 2023-03-07 | LUX | `82023LU0307(51)` | Cour d'appel, 39/23 | PSD1 Art. 59 |

**Uwaga:** Niska liczba (3) wynika z faktu, że `case-law_national_act_reference_european` jest uzupełnione tylko dla 56% DEC_NC. Wiele wyroków krajowych dot. PSD2 prawdopodobnie istnieje, ale nie ma tagowanej referencji do aktu UE.

### Porównanie z GDPR

GDPR (`32016R0679`) — 5 DEC_NC z bezpośrednią referencją. Podobny rząd wielkości — problem jest w pokryciu danych, nie w braku orzeczeń.

---

## Opinie Rzeczników Generalnych (OPIN_AG)

14,360 w CELLAR. Powiązane z wyrokami TSUE przez:
- `case-law_has_conclusions_opinion_advocate-general` (na JUDG → link do OPIN_AG)
- Wspólny numer sprawy w CELEX (np. `62019CC0287` to opinia AG w C-287/19)

### Wartość dla monitoringu

AG opinion publikowana jest **kilka miesięcy przed wyrokiem**. TSUE zgadza się z AG w ~80% spraw. Dlatego:
1. Nowa OPIN_AG cytująca Twój akt = **sygnał nadchodzącego wyroku**
2. Treść opinii AG daje wskazówki co TSUE prawdopodobnie orzeknie

### Jak monitorować nowe opinie AG dot. danego aktu

```sparql
PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>

# Opinie AG w sprawach dot. PSD2
SELECT ?agOpinion ?celex ?date WHERE {
  ?judgment cdm:case-law_interpretes_resource_legal <CELLAR_URI_AKTU> .
  ?judgment cdm:case-law_has_conclusions_opinion_advocate-general ?agOpinion .
  OPTIONAL { ?agOpinion cdm:resource_legal_id_celex ?celex }
  OPTIONAL { ?agOpinion cdm:work_date_document ?date }
}
ORDER BY DESC(?date)
```

---

## Strategia monitoringu orzecznictwa

### Warstwa 1: TSUE (najwyższa pewność)

```
Pytanie prejudycjalne (CN) → Opinia AG (CC) → Wyrok (CJ)
       ↓                        ↓                  ↓
  Najwcześniejszy          Predyktor           Wiążący
  sygnał (2-3 lata)       (~80% accuracy)     wynik
```

**Query:** `case-law_interpretes_resource_legal` + `communication_case_new_submits_preliminary_question_resource_legal`

### Warstwa 2: Sądy krajowe (niższa pewność, szerszy zasięg)

```
DEC_NC z case-law_national_act_reference_european CONTAINS '{CELEX}'
```

**Ograniczenia:**
- Tylko 56% DEC_NC ma pole `european_act_reference`
- Wymaga string match (nie URI link)
- Opóźnienie w dodawaniu nowych wyroków
- Dominacja Niemiec (22% wszystkich DEC_NC)

### Warstwa 3: Artykuły naukowe (kontekst)

Pole `case-law_article_journal_related` na JUDG i DEC_NC daje:
- Tytuł artykułu
- Autor
- Czasopismo + rok
- Język

Monitoring artykułów naukowych o wyrokach = dodatkowy kontekst interpretacyjny.

---

## Wzorce SPARQL do monitoringu

### Kompleksowy monitoring orzecznictwa dla danego aktu

```sparql
PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>

# Wszystkie typy case-law dotyczące danego aktu
SELECT ?celex ?type ?date ?source WHERE {
  {
    # TSUE wyroki interpretujące
    ?work cdm:case-law_interpretes_resource_legal <CELLAR_URI> .
    BIND('TSUE_interpret' AS ?source)
  } UNION {
    # TSUE potwierdza ważność
    ?work cdm:case-law_declares_valid_resource_legal <CELLAR_URI> .
    BIND('TSUE_valid' AS ?source)
  } UNION {
    # Pytania prejudycjalne
    ?work cdm:communication_case_new_submits_preliminary_question_resource_legal <CELLAR_URI> .
    BIND('preliminary_Q' AS ?source)
  }
  ?work cdm:resource_legal_id_celex ?celex .
  ?work cdm:work_has_resource-type ?type .
  OPTIONAL { ?work cdm:work_date_document ?date }
}
ORDER BY DESC(?date)
```

### Monitoring wyroków krajowych (DEC_NC)

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

### Nowe artykuły naukowe o wyrokach dot. danego aktu

```sparql
PREFIX cdm: <http://publications.europa.eu/ontology/cdm#>

SELECT ?celex ?article WHERE {
  ?work cdm:case-law_interpretes_resource_legal <CELLAR_URI> .
  ?work cdm:resource_legal_id_celex ?celex .
  ?work cdm:case-law_article_journal_related ?article .
}
```

---

## Kluczowe odkrycia

1. **TSUE ma silne linkowanie** — `case-law_interpretes_resource_legal` daje bezpośredni URI link do interpretowanego aktu. DEC_NC mają słabsze linkowanie (string w `european_act_reference`).

2. **DEC_NC są niedostatecznie otagowane** — tylko 56% ma referencje do prawa UE. Faktyczna liczba wyroków krajowych dot. PSD2 jest prawdopodobnie dużo wyższa niż 3.

3. **Artykuły naukowe w CELLAR** — nieoczekiwane odkrycie. 33k referencji do artykułów na DEC_NC + osobne na JUDG. Daje kontekst akademicki.

4. **AG opinii jako predyktor** — publikowane miesiące przed wyrokiem, 80% trafność. Najlepszy early warning na wynik TSUE.

5. **Trójwarstwowa strategia monitoringu**: pytania prejudycjalne (najwcześniejszy sygnał) → opinie AG (predyktor) → wyroki TSUE (wiążące) + wyroki krajowe (stosowanie w praktyce).

6. **DEC_NC z referencją do artykułu** — format `{CELEX}-A{art}P{par}PT{pkt}` pozwala na monitoring z granularnością artykuł-po-artykule.

7. **Polska: 286 DEC_NC** w CELLAR, głównie z Sądu Najwyższego. Najnowszy z maja 2025.
