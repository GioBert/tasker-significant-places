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

- `scrcpy 3.3.4`, installato in `C:\Program Files\scrcpy`
- collegamento USB tramite `adb`
- telefono di test con Android 13

Con il debug USB autorizzato sul telefono, il mirroring puo' essere avviato da PowerShell con:

```powershell
& 'C:\Program Files\scrcpy\scrcpy.exe'
```

Per controllare prima che il dispositivo sia visibile tramite ADB:

```powershell
& 'C:\Program Files\scrcpy\adb.exe' devices
```

Il modello, il seriale ADB e gli altri identificativi del dispositivo non devono essere inseriti nella documentazione pubblica o nei log versionati.

## Permessi e impostazioni importanti

- permesso posizione con posizione precisa attiva per Tasker
- accesso ai file necessari
- esclusione di Tasker dalle ottimizzazioni batteria
- eventuale avvio automatico di Tasker
- opzioni sviluppatore attive se servono test con mock location o debugging USB

## Nota

Il progetto deve poter leggere la configurazione esterna e scrivere il CSV di output nel percorso configurato.
