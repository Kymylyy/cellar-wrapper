# Contract Notes

Robocze notatki z testowania komend i kontraktow API.

## Jak uzywac

- Zapisujemy tu obserwacje, ktore nie powinny trafic do finalnych przykladow.
- Notatki dotycza zachowania komendy lub kontraktu, a nie statusu pojedynczego przykladu.
- Kazda notatka powinna byc krotka i konkretna.

## Template

### `group command`

- Acts: `DORA`, `MiCA`
- Observation: Krotki opis tego, co kontrakt pokazuje albo gdzie wynik jest mylacy.
- Follow-up: Co warto sprawdzic w kolejnej probie.

## Notes

### `lookup get-legal-basis`

- Acts: `MiCA`
- Observation: The result set can mix treaty legal basis entries, level-2 acts based on the act, and other documents based on the act such as recommendations.
- Follow-up: If the goal is to show treaty basis specifically, use pagination or filtering-friendly examples instead of the default first page.

- Acts: `DORA RMF`
- Observation: This contract can be used to retrieve the reverse relation for a delegated act, i.e. the base act it is based on. For `DORA RMF`, it returns `DORA` as `outgoing` `based_on_resource_legal`.
- Follow-up: Use this command when the goal is delegated act -> base act, not base act -> delegated acts.

### `relations get-repeals`

- Acts: `PSD3`
- Observation: For proposal acts, `incoming`/`both` may not show that an existing act is planned to be repealed; `get-repeals` can return an empty set even when the proposal text indicates a future repeal.
- Follow-up: Treat this as a current CELLAR relation-data limitation for proposals rather than evidence that no planned repeal exists.

### `relations get-amendments`

- Acts: `PSR`
- Observation: For proposal acts, `incoming`/`both` may not show that an existing act is planned to be amended; `get-amendments` can return an empty set even when the proposal text indicates future amendments.
- Follow-up: Treat this as a current CELLAR relation-data limitation for proposals rather than evidence that no planned amendment exists.

### `relations get-citations`

- Acts: `MiCA`
- Observation: The result set is not limited to legal acts; it can also include communications, impact assessments, and staff working documents.
- Follow-up: If the goal is to show citations from legal acts only, use examples that combine citations with resource-type filtering where possible.

### `relations get-based-on-acts`

- Acts: `DORA`, `DORA RMF`
- Observation: This contract only supports the base-act -> delegated-acts direction. For a delegated act itself, it does not show the underlying base act.
- Follow-up: Use `lookup get-legal-basis` when the goal is to retrieve the reverse relation, i.e. delegated act -> base act.

- Acts: `MiFID II`
- Observation: For some acts, this contract is not limited in practice to delegated regulations/directives. It can behave more like "acts/documents based on this act", even though it is exposed under the name `get-based-on-acts`.
- Follow-up: Treat the command name as narrower than the observed payload. Verify returned `resource_type` values when using this contract as an examples source.

### `relations get-proposals-to-change`

- Acts: `AI Act`, `PSD2`, `Urban Wastewater`
- Observation: Wrapper command and contract type now expose this as "proposals to change", because CELLAR’s `cdm:resource_legal_proposes_to_amend_resource_legal` includes amendment, repeal, and recast intent.
- Follow-up: Treat results as legislative-change intents, not strictly "amendment-only" intentions, and keep the raw `predicate` unchanged in payloads.

### `lifecycle get-corrigenda`

- Acts: `MiCA`
- Observation: The same corrigendum can appear twice with the same `uri` and `celex`, once as `CORRIGENDUM` and once as `REG`. This looks like multi-typed CELLAR data rather than parser-side duplication.
- Follow-up: If the goal is to show corrigenda only, consider filtering by `resource_types = ["CORRIGENDUM"]` or document the duplication explicitly.

### `search search-by-title`

- Acts: `Crypto-assets`
- Observation: With filtered `resource_types`, the wrapper now binds `?type` through `VALUES`, so title-search payload rows stay inside the requested type set. For `PUB_GEN`, the wrapper no longer leaks sibling `SUM_EXE` or `STU` rows from the same CELLAR family.
- Follow-up: Keep at least one accepted title-search example that proves filtered `resource_types` behave as an exact type-set constraint rather than a loose work-level filter.

### `lifecycle get-opinions`

- Acts: `DORA`, `MiCA`, `GDPR`, `PSD2`, `MiFID`, `CCD1`, `CCD2`, `FiDAR`, `PSD3`, `PSR`, `DORA RMF`, `AI Act`
- Observation: In the checked set, non-empty results appeared only for proposal acts (`FiDAR`, `PSD3`, `PSR`). The payload mixes EESC and EP opinion relations with broader `influences`-based opinion-like documents such as ECB and EDPS materials.
- Follow-up: Use proposal acts as examples for this command. Do not treat it as a generic "opinions for any act" contract.

### `lifecycle get-consolidated-versions`

- Acts: `PSD2`
- Observation: The result set is broader than "consolidated versions of this act only". For `PSD2`, CELLAR returns both consolidated versions of PSD2 itself (for example `02015L2366-20240408`, `02015L2366-20250117`) and consolidated versions of other acts linked through the same `consolidates` relation. Some rows can also appear as parallel CELLAR resources without a mapped CELEX.
- Follow-up: If the goal is to show only consolidated versions of the queried act, prefer examples where the CELEX starts with `0{base_celex}-` and treat rows with `celex: null` as non-canonical duplicates or aliases.

### `lifecycle get-nims`

- Acts: `PSD2`, `DORA`
- Observation: This command is meaningful mainly for directives. For directive acts such as `PSD2`, it returns grouped national implementing acts. For regulations such as `DORA`, the practical result is an empty set because there are no national implementing measures in this CELLAR contract.
- Follow-up: Prefer directive examples for positive `get-nims` payloads. Use regulations only as explicit zero-result boundary cases.

### `case-law get-preliminary-questions`

- Acts: `PSD2`
- Observation: On EUR-Lex WWW, preliminary questions are not shown as unique cases. The same `CN` case can appear in several rows because EUR-Lex lists multiple article-level links for one preliminary reference. The wrapper command deduplicates this at the work level and returns unique case-law rows.
- Follow-up: When comparing the wrapper payload with the EUR-Lex act page, compare unique `CN` CELEX values rather than raw row counts.
