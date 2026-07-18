# Setup Del Telefono Android

## App necessarie

- Tasker
- un gestore file

## App opzionali ma utili

- FolderSync per sincronizzare i file con cloud storage
- un'app di mock location per i test
- Google Maps per verificare la correttezza della posizione
- MacroDroid come watchdog di avvio su dispositivi MIUI nei quali Tasker non
  ricrea autonomamente il monitor dopo un riavvio

## Strumenti desktop collegati

- `scrcpy` per il mirroring del telefono sul PC
- `adb` con debug USB per gestione e diagnostica
- client FTP o strumenti equivalenti per trasferire file di configurazione

## Ambiente Di Test Usato Nel Progetto

L'ambiente di test principale usa:

- `scrcpy 4.1`, installato in `C:\Program Files\scrcpy`
- `adb 37.0.0` tramite collegamento USB
- Xiaomi Redmi 10C NFC, model code `220333QNY`, variante EEA
- Android 13 / API 33, MIUI `V14.0.10.0.TGEEUXM`
- Tasker `6.6.20`

Con il debug USB autorizzato sul telefono, il mirroring puo' essere avviato da PowerShell con:

```powershell
& 'C:\Program Files\scrcpy\scrcpy.exe'
```

Per controllare prima che il dispositivo sia visibile tramite ADB:

```powershell
& 'C:\Program Files\scrcpy\adb.exe' devices
```

Il modello e la build, non essendo identificativi univoci, possono essere
documentati. Il seriale ADB e gli altri identificativi univoci del dispositivo
non devono invece apparire nella documentazione pubblica o nei log versionati.

## Permessi e impostazioni importanti

- permesso posizione con posizione precisa attiva per Tasker
- posizione in background consentita
- accesso ai file necessari
- esclusione di Tasker dalle ottimizzazioni batteria Android
- risparmio batteria MIUI impostato su `Nessuna restrizione`
- avvio automatico MIUI abilitato per Tasker
- `Usa Allarmi Affidabili` impostato su `Sempre`
- `Avvia Monitor all'Apertura dell'App` abilitato
- permesso MIUI `Mostra sulla schermata di blocco` consentito
- opzioni sviluppatore attive se servono test con mock location o debugging USB

## Watchdog Di Avvio Su MIUI

Test di riavvio ripetuti hanno mostrato che, su questo dispositivo, le sole
impostazioni Tasker e MIUI non garantiscono la ricreazione di `MonitorService`.
Tasker puo' rimanere visibile nelle app recenti senza avere un processo attivo.
La verifica va quindi eseguita sul processo e sul servizio, non sulle anteprime
della schermata Recenti.

La mitigazione validata usa MacroDroid `5.65.9` con la macro
`WATCHDOG_TASKER_BOOT`:

1. evento `Avvio Dispositivo`;
2. attesa di 1 minuto, senza `Usa la sveglia`;
3. azione `Lancia Tasker`, con le opzioni di avvio lasciate disattivate;
4. nessun vincolo.

Per MacroDroid sono richiesti:

- MacroDroid abilitato e macro attiva;
- avvio automatico MIUI abilitato;
- batteria impostata su `Nessuna restrizione`;
- `Sospendi l'attivita' dell'app se inutilizzata` disabilitato;
- `Mostra sulla schermata di blocco`, `Aprire nuove finestre durante
  l'esecuzione in background` e finestre pop-up consentiti.

Sul dispositivo di test e' attiva una licenza MacroDroid Premium, quindi il
watchdog non dipende dalla disponibilita' di giorni gratuiti. Dopo un riavvio,
sbloccare il telefono almeno una volta e lasciare trascorrere almeno 90 secondi
senza aprire manualmente le app.

Nel test reale del 18 luglio 2026, MacroDroid e' partito al boot, ha avviato
Tasker e `MonitorService` e' risultato attivo senza apertura manuale. Il
watchdog e' una mitigazione specifica del dispositivo, non una dipendenza della
logica Significant Places.

I risultati aggregati di sensori, GPS, schermo spento e recovery sono descritti
in [Validazione sul dispositivo di test](validazione_dispositivo_test.md).

Prima di modificare o pulire la configurazione, seguire sempre
[Backup e ripristino di Tasker](backup_ripristino_tasker.md). Il backup XML di
Tasker non sostituisce la copia separata della cartella `_SignificantPlaces`.

## Nota

Il progetto deve poter leggere la configurazione esterna e scrivere il CSV di output nel percorso configurato.
