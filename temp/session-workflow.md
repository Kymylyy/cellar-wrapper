# Session Workflow

Ten katalog `temp/` sluzy do roboczej pracy nad przykladami komend i kontraktow API.

## Jak pracujemy

1. Uzytkownik podaje komende i akt, na przyklad: `lookup get-act dla DORA`.
2. Codex znajduje odpowiedni CELEX w `acts-to-celex.md`.
3. Codex uruchamia komende i pokazuje wynik.
4. Uzytkownik ocenia, czy wynik nadaje sie jako przyklad.
5. Jesli tak, uzytkownik pisze, zeby dopisac run do `examples/accepted.json`.
6. Jesli podczas testu wychodzi ciekawa obserwacja o komendzie lub kontrakcie, zapisujemy ja w `contract-notes.md`.

## Role plikow

- `acts-to-celex.md`: robocza mapa nazw aktow do CELEX-ow.
- `examples/accepted.json`: tylko zaakceptowane przyklady, zapisane jako pretty JSON.
- `examples/accepted.generated.md`: wygenerowany markdown render calosci `accepted.json` do czytania i dalszej pracy nad docs.
- `contract-notes.md`: obserwacje o zachowaniu komend i kontraktow.

## Zasady

- Do `accepted.json` trafiaja tylko zaakceptowane przyklady.
- Nie trzymamy tam odrzuconych ani roboczych runow.
- `output` zapisujemy jako pretty JSON, nie w jednej linii.
- `accepted.generated.md` jest artefaktem wtornym; nie edytujemy go recznie, tylko regenerujemy z `accepted.json`.
- Jesli skrot aktu jest niejednoznaczny, trzeba to doprecyzowac w mapowaniu albo notatce.
