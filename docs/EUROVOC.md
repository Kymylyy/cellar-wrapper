# EUROVOC

## Cel

Ustalić, dlaczego zapytania EuroVoc (`search_by_eurovoc`, `new_by_eurovoc`) są
wolne/timeoutują, i jaki wariant implementacji daje największy zysk bez utraty
sensu biznesowego.

Data researchu: 2026-03-01.

## Status implementacji (as-of 2026-03-01)

- Obecna implementacja runtime nadal korzysta z modelu labelowego
  (`CONTAINS` po `skos:prefLabel`) w `search_by_eurovoc` / `new_by_eurovoc`.
- Opisany niżej model 2-krokowy (resolve tekstu do URI + query po URI) jest
  rekomendacją projektową, ale nie został jeszcze wdrożony.

## Zakres analizy

- Kod builderów SPARQL:
  - `src/cellar_wrapper/sparql_builders/search.py`
- Wywołania klienta:
  - `src/cellar_wrapper/client_mixins/search.py`
  - `src/cellar_wrapper/client_mixins/monitoring.py`
- Transport HTTP:
  - `src/cellar_wrapper/http.py`
- Live benchmarki na endpointzie CELLAR:
  - `https://publications.europa.eu/webapi/rdf/sparql`

## Jak działa obecna implementacja

Dla `search_by_eurovoc(tags=[...])` query robi:

1. Join do konceptów EuroVoc (`?work cdm:work_is_about_concept_eurovoc ?concept`)
2. Join do etykiety (`?concept skos:prefLabel ?conceptLabel`)
3. Filtrowanie tekstowe po etykiecie:
   - `FILTER(CONTAINS(LCASE(STR(?conceptLabel)), LCASE('<tag>')))`
4. Dalsze `OPTIONAL` (celex/date/type/title), `ORDER BY DESC(?date)`, `LIMIT/OFFSET`

To powoduje drogi skan tekstowy po etykietach.

## Kluczowe ustalenie

Największe wąskie gardło to filtrowanie tekstowe po `conceptLabel` (`CONTAINS`).

`LIMIT` na końcu query nie rozwiązuje problemu, bo endpoint i tak wykonuje ciężki
etap dopasowania labeli przed finalnym ograniczeniem wyników.

## Benchmarki live (POST, czyli zgodnie z klientem)

### Baseline (obecny model po labelu)

- `search_by_eurovoc("payment", limit=50)`
  - HTTP 200
  - czas: **264.98 s**
  - wynik: 50

- `search_by_eurovoc("payment", resource_type=REG, limit=50)`
  - HTTP 200
  - czas: **36.04 s**
  - wynik: 50

- `search_by_eurovoc("payment", resource_type=PROP_REG, limit=50)`
  - HTTP 200
  - czas: **10.04 s**
  - wynik: 50

Wniosek: zawężanie `resource_type` pomaga, ale nie rozwiązuje głównego bottlenecka.

### Wariant docelowy (2 kroki, finalne filtrowanie po URI konceptów)

Krok A (resolve tagu -> URI konceptów):
- `find_eurovoc_concept("payment")`
  - 3 powtórki: **22.16 s**, **23.24 s**, **21.42 s**
  - liczba konceptów: 16

Krok B (search po `VALUES ?concept { <uri1> ... }`):
- 1 koncept (`2220`): **0.30 s**
- 16 konceptów (`payment`): **0.69 s**
- 116 konceptów (`law`): **0.69 s**

Wniosek: krok B jest bardzo szybki nawet przy dużej liczbie konceptów.

## Ile konceptów mapuje się na popularne tagi

Liczba konceptów dopasowanych po labelu (`CONTAINS`) na 2026-03-01:

- `payment`: 16
- `payments`: 6
- `financial`: 47
- `service`: 46
- `digital`: 16
- `data`: 34
- `market`: 67
- `regulation`: 29
- `law`: 116

Interpretacja:
- szeroki tag może dać dużo konceptów,
- ale to nie jest problem wydajnościowy dla kroku B (po URI),
- realnym kosztem jest krok A (resolve labeli).

## Reprodukcja timeoutu 30s

- Obecny baseline query po labelu z klientowym budżetem 30s:
  - `curl --max-time 30 ...`
  - timeout po ~30.00 s (bez payloadu)

To potwierdza, że domyślne `read timeout = 30s` jest za małe dla obecnego
wariantu query.

## Dodatkowa obserwacja: endpoint `timeout=...`

Podanie `timeout=30000` do endpointu dało:
- HTTP 206
- skrócony/nieaktualny zestaw wyników (np. lata 2015-2017)

Nie należy opierać jakości odpowiedzi na tym parametrze. To jest co najwyżej
awaryjny fail-fast, nie stabilna strategia produktu.

## Co zmieniamy w implementacji (rekomendacja)

### Docelowy flow

1. Użytkownik podaje tag tekstowy (`payment`).
2. Resolve: tag -> lista `concept_uri` (jak dziś robi `find_eurovoc_concept`).
3. Finalne search/new: query po `VALUES ?concept` (dokładne matchowanie URI).

### Czy semantyka zostaje ta sama?

Tak, możemy zachować praktycznie tę samą semantykę biznesową:
- input API pozostaje tekstowy,
- `OR` między tagami zostaje,
- `since/resource_type/lang/limit/offset` zostają,
- zmienia się tylko mechanika wykonania (2 kroki zamiast 1 ciężkiego query).

### Potencjalne różnice/ryzyka

- Dwa requesty zamiast jednego (większa powierzchnia błędu sieciowego).
- Jeśli sztucznie zetniemy listę konceptów na resolve, można uciąć wyniki.
- Przy cache `tag -> URIs` trzeba kontrolować TTL (świeżość vs koszt).

### Jak ograniczyć ryzyka

- Nie obcinać konceptów arbitralnym limitem (lub jasno kontrolować paging).
- Dodać cache `tag -> [URI]` (TTL np. 24h) dla stabilnej wydajności.
- Rozważyć opcję wejścia bezpośrednio po URI (pomijanie resolve dla power-userów).
- Podnieść domyślny `read timeout` (np. 60s) jako bufor dla kroku A.

## Monitoring per podmiot (docelowy model operacyjny)

W praktycznym monitoringu dla konkretnego podmiotu (firma/sektor) można
traktować problem resolve jako etap konfiguracji, a nie runtime:

1. Jednorazowo preload słownika EuroVoc (lub resolve podczas konfiguracji).
2. Zdefiniowanie stałego profilu monitoringu jako lista `concept_uri`.
3. Cykliczne monitorowanie uruchamiane już tylko po URI (`VALUES ?concept`) + `since`
   + opcjonalnie `resource_type`.

Konsekwencja:
- kosztowny krok A (resolve po labelu) nie musi być wykonywany w każdym cyklu,
- runtime monitoringu staje się szybki i przewidywalny,
- problem timeoutów EuroVoc w codziennej pracy jest w dużej mierze wyeliminowany.

## Najważniejsza decyzja projektowa

Nie optymalizować dalej pojedynczego query labelowego.

Wdrożyć model 2-krokowy:
- resolve tekstu do URI,
- finalny query po URI.

To adresuje root cause i daje największy skok wydajności.
