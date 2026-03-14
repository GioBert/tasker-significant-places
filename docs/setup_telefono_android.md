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

## Permessi e impostazioni importanti

- permesso posizione con posizione precisa attiva per Tasker
- accesso ai file necessari
- esclusione di Tasker dalle ottimizzazioni batteria
- eventuale avvio automatico di Tasker
- opzioni sviluppatore attive se servono test con mock location o debugging USB

## Nota

Il progetto deve poter leggere la configurazione esterna e scrivere il CSV di output nel percorso configurato.
