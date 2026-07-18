# Strumenti Consigliati

## Tooling necessario per sviluppo e test

- `git`
- `VS Code`
- Android Platform Tools / `adb`
- `scrcpy`

Ambiente verificato del progetto:

- `scrcpy 4.1`
- `adb 37.0.0`
- Tasker `6.6.20`
- telefono di test con Android 13

La diagnostica e' stata eseguita principalmente da terminale con `adb shell`,
`dumpsys`, `logcat` e trasferimenti `adb pull/push`. `scrcpy` resta utile per le
sole impostazioni Tasker o MIUI che richiedono un'interazione visiva.

## Tooling utile ma non obbligatorio

- `gh`
- `python`
- `git-filter-repo`
- `Codex`
- estensione VS Code `redhat.vscode-xml`
- estensione VS Code `mechatroner.rainbow-csv`
- Code Spell Checker con dizionario italiano

## Utilita' nel progetto

- `git`: versionamento e rollback
- `adb`: diagnostica, logcat, trasferimento file e verifica del dispositivo
- `scrcpy`: mirroring e controllo del telefono dal PC
- `gh`: integrazione con GitHub
- `python`: parsing CSV, validazioni e report
- `git-filter-repo`: manutenzione avanzata e bonifiche della history
- `VS Code`: editing e navigazione del progetto
- `redhat.vscode-xml`: validazione e navigazione degli export XML di Tasker
- `mechatroner.rainbow-csv`: lettura e controllo visuale dei CSV delimitati da punto e virgola
- Code Spell Checker: controllo della documentazione italiana e dei termini tecnici inglesi
- `Codex`: supporto operativo, progettuale e documentale

Android Studio, emulatori, JADX, Frida e proxy di rete possono essere utili per
analisi Android avanzate, ma non sono prerequisiti di questo progetto Tasker.
