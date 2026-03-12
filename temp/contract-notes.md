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

- Acts: `AI Act`, `PSD2`, `White Paper on urban wastewater treatment and water reuse`
- Observation: Wrapper command and contract type now expose this as "proposals to change", because CELLAR’s `cdm:resource_legal_proposes_to_amend_resource_legal` includes amendment, repeal, and recast intent.
- Follow-up: Treat results as legislative-change intents, not strictly "amendment-only" intentions.
