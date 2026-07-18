# Setup Del Telefono Android

## App necessarie

- Tasker
- un gestore file

## App opzionali ma utili

- FolderSync per sincronizzare i file con cloud storage
- un'app di mock location per i test
- Google Maps per verificare la correttezza della posizione

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

Dopo un riavvio completo, sbloccare il telefono almeno una volta: sul dispositivo
testato `MonitorService` e gli allarmi periodici sono stati ricreati entro 30
secondi dal primo sblocco senza aprire Tasker.

I risultati aggregati di sensori, GPS, schermo spento e recovery sono descritti
in [Validazione sul dispositivo di test](validazione_dispositivo_test.md).

Prima di modificare o pulire la configurazione, seguire sempre
[Backup e ripristino di Tasker](backup_ripristino_tasker.md). Il backup XML di
Tasker non sostituisce la copia separata della cartella `_SignificantPlaces`.

## Nota

Il progetto deve poter leggere la configurazione esterna e scrivere il CSV di output nel percorso configurato.
