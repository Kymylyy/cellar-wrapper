# EUROVOC

## Goal

Determine why EuroVoc queries (`search_by_eurovoc`, `new_by_eurovoc`) were
slow or timing out, and which implementation variant delivers the biggest gain
without losing business usefulness.

Research date: 2026-03-01.

## Implementation Status (as of 2026-03-01)

- Runtime `find_eurovoc_concept` uses a local index (`src/cellar_wrapper/data/eurovoc_index.json`).
- Runtime `search_by_eurovoc` and `new_by_eurovoc` use a 2-step model:
  resolve the text tag locally to `concept_uri`, then run the final query via
  `VALUES ?concept`.
- The public API stayed unchanged (`tags` as input); only the execution
  mechanics changed.

## Analysis Scope

- SPARQL builder code:
  - `src/cellar_wrapper/sparql_builders/search.py`
- Client calls:
  - `src/cellar_wrapper/client_mixins/search.py`
  - `src/cellar_wrapper/client_mixins/monitoring.py`
- HTTP transport:
  - `src/cellar_wrapper/http.py`
- Live benchmarks against the CELLAR endpoint:
  - `https://publications.europa.eu/webapi/rdf/sparql`

## How the Baseline Implementation Worked (before the change)

For `search_by_eurovoc(tags=[...])` the query did:

1. Join to EuroVoc concepts (`?work cdm:work_is_about_concept_eurovoc ?concept`)
2. Join to the label (`?concept skos:prefLabel ?conceptLabel`)
3. Text filtering on the label:
   - `FILTER(CONTAINS(LCASE(STR(?conceptLabel)), LCASE('<tag>')))`
4. More `OPTIONAL` clauses (celex/date/type/title), `ORDER BY DESC(?date)`, `LIMIT/OFFSET`

That causes an expensive text scan across labels.

## Key Finding

The main bottleneck is text filtering on `conceptLabel` (`CONTAINS`).

`LIMIT` at the end of the query does not solve the problem, because the endpoint
still executes the expensive label-matching stage before limiting the final
result set.

## Live Benchmarks (POST, matching client behavior)

### Baseline (current label-based model)

- `search_by_eurovoc("payment", limit=50)`
  - HTTP 200
  - time: **264.98 s**
  - result: 50

- `search_by_eurovoc("payment", resource_type=REG, limit=50)`
  - HTTP 200
  - time: **36.04 s**
  - result: 50

- `search_by_eurovoc("payment", resource_type=PROP_REG, limit=50)`
  - HTTP 200
  - time: **10.04 s**
  - result: 50

Conclusion: narrowing by `resource_type` helps, but it does not solve the main
bottleneck.

### Target Variant (2 steps, final filtering by concept URI)

Step A (resolve tag -> concept URIs):
- `find_eurovoc_concept("payment")`
  - 3 runs: **22.16 s**, **23.24 s**, **21.42 s**
  - concept count: 16

Step B (search via `VALUES ?concept { <uri1> ... }`):
- 1 concept (`2220`): **0.30 s**
- 16 concepts (`payment`): **0.69 s**
- 116 concepts (`law`): **0.69 s**

Conclusion: step B is very fast even for large concept sets.

## How Many Concepts Map to Common Tags

Concept counts matched by label (`CONTAINS`) as of 2026-03-01:

- `payment`: 16
- `payments`: 6
- `financial`: 47
- `service`: 46
- `digital`: 16
- `data`: 34
- `market`: 67
- `regulation`: 29
- `law`: 116

Interpretation:
- a broad tag can map to many concepts,
- but that is not a performance problem for step B (URI filtering),
- the real cost is step A (label resolution).

## Reproducing the 30s Timeout

- Current baseline label query with the client's 30s budget:
  - `curl --max-time 30 ...`
  - timeout after ~30.00 s (no payload)

This confirms that the default `read timeout = 30s` is too small for the
current query variant.

## Additional Observation: endpoint `timeout=...`

Passing `timeout=30000` to the endpoint produced:
- HTTP 206
- a shortened / stale result set (for example years 2015-2017)

Response quality should not rely on that parameter. At best it is an emergency
fail-fast lever, not a stable product strategy.

## What Changed in the Implementation

### Target Flow

1. The user provides a text tag (`payment`).
2. Resolve: tag -> list of `concept_uri`.
3. Final search/new: query via `VALUES ?concept` (exact URI matching).

### Does the Semantic Meaning Stay the Same?

Yes, we can preserve almost exactly the same business semantics:
- API input stays text-based,
- `OR` across tags stays,
- `since/resource_type/lang/limit/offset` stay,
- only the execution mechanics change (2 steps instead of 1 heavy query).

### Potential Differences / Risks

- Two requests instead of one (larger network failure surface).
- If we artificially truncate the resolved concept list, we can cut off results.
- If we cache `tag -> URIs`, we need to manage TTL (freshness vs cost).

### How to Reduce the Risks

- Do not trim concepts via an arbitrary limit, or control paging explicitly.
- Add `tag -> [URI]` cache (for example TTL 24h) for stable performance.
- Consider a direct-URI input option (skip resolve for power users).
- Raise the default `read timeout` (for example to 60s) as a safety margin for step A.

## Monitoring Per Entity (target operating model)

In practical monitoring for a specific entity (company/sector), treat resolution
as a configuration step rather than runtime work:

1. One-time preload of the EuroVoc dictionary, or resolve during setup.
2. Define a stable monitoring profile as a list of `concept_uri`.
3. Run recurring monitoring only by URI (`VALUES ?concept`) + `since`
   + optional `resource_type`.

Consequence:
- the expensive step A (label resolution) does not need to run on every cycle,
- monitoring runtime becomes fast and predictable,
- EuroVoc timeout issues are largely eliminated in day-to-day operation.

## Most Important Design Decision

Drop the single label-based query and switch to the 2-step model:
- resolve text to URIs,
- run the final query by URI.

That addresses the root cause and provides the largest performance gain.
