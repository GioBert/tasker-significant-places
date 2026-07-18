# Simulazione Locale E Validazione

## Obiettivo

Gli strumenti locali riducono i test ripetitivi sul telefono e permettono di
verificare un batch prima di applicarlo in Tasker. Non sostituiscono il test
finale su Android, necessario per GPS, background, allarmi, MIUI e consumi.

Gli scenari inclusi sono sintetici e non contengono luoghi reali.

## Simulatore Della Logica

Il simulatore Python riproduce:

- validazione di coordinate e accuratezza;
- inizializzazione giornaliera;
- permanenza nel luogo corrente;
- apertura, sostituzione e conferma del candidato;
- timestamp di arrivo del candidato confermato;
- cambio giorno;
- naming automatico e matching del luogo noto piu' vicino;
- ricostruzione dello stato dall'ultimo record di un CSV esistente.

Esecuzione dello scenario di esempio:

```powershell
python tools\simulate_significant_places.py `
  tests\fixtures\basic_route.csv `
  --config config\tasker_globals.csv `
  --known-places config\known_places.example.csv
```

Per creare un CSV simulato aggiungere:

```text
--output TestData/simulated.csv
```

Gli output di test e i replay di dati reali devono restare fuori dal
repository. Un CSV operativo esistente puo' essere usato localmente con
`--resume-csv` per verificare la futura recovery senza pubblicarne il
contenuto.

Il modello e la configurazione B005 applicano entrambi intervalli validi di
latitudine e longitudine e recovery dal CSV. Il modello locale aggiunge casi
fail-closed per file vuoti, header errati, date incoerenti, ordinamento dei
timestamp, ID e nomi non validi.

## Validatore Dell'Export Tasker

Il validatore e' di sola lettura:

```powershell
python tools\validate_tasker_xml.py `
  significant_places_tasker.xml `
  --config config\tasker_globals.csv
```

Controlla almeno:

- XML leggibile;
- presenza dei tre task;
- profilo collegato al task principale;
- variazioni nel numero di azioni rispetto alla baseline;
- condizioni iniziali su latitudine e longitudine;
- fallback interni differenti dalla config esterna;
- aggiornamento dello stato prima della scrittura CSV;
- intervalli GPS non controllati;
- conteggio candidato incrementato ma non usato come condizione.

Gli `ERROR` sono bloccanti. I `WARN` descrivono rischi da valutare nel batch.
L'opzione `--strict` restituisce un errore anche in presenza di warning ed e'
utile quando tutti i warning previsti per una release sono stati risolti.

## Test Automatici

```powershell
python -m unittest discover -s tests -v
```

I test devono essere eseguiti prima di applicare un batch al telefono e prima
di versionare un nuovo export Tasker.

Per generare o verificare in modo idempotente B005:

```powershell
python tools\build_b005_csv_recovery_backup.py `
  percorso\backup-pre-B005.xml `
  TestData\B005.xml
```

Il test manuale di INIT deve riprodurre l'ordine reale:
`LOAD_CONFIG_DEFAULTS` e solo dopo `INIT_SIGNIFICANT_PLACES`.

## Candidato Con Posizione Sintetica

Per collaudare sul telefono la logica successiva all'acquisizione senza usare
coordinate reali e' disponibile:

```powershell
python tools\build_injected_location_test_backup.py `
  percorso\backup-nativo.xml `
  TestData\INJ.xml
```

Il generatore e' destinato esclusivamente a backup completi conservati in area
privata. Non funziona sull'export pubblico sanitizzato, che non contiene le
variabili globali radice necessarie.

Il candidato prodotto:

- reindirizza `%LOG_DIR` sotto `TestData/injected-B004`;
- imposta temporaneamente `%MIN_STOP_MINUTES` a un minuto;
- sostituisce la sola `Ottieni Posizione v2` del task principale con tre
  assegnazioni sintetiche;
- lascia invariati validazione, candidato, scrittura CSV e commit B004;
- verifica che i commit globali restino successivi a `Scrivi File`.

Prima dell'import servono checkpoint, manifest degli hash e validazione XML.
Dopo il test bisogna ripristinare il checkpoint e verificare che nessun file
operativo preesistente sia cambiato. Il file generato puo' contenere variabili
private ereditate dal backup sorgente e non deve mai entrare in Git.

## Confine Della Simulazione

La simulazione non dimostra:

- corretta esecuzione delle azioni Tasker;
- concessione dei permessi Android;
- affidabilita' di `MonitorService` e degli allarmi;
- comportamento con schermo spento o Doze;
- precisione e tempi del GNSS reale;
- consumo energetico.

Questi aspetti richiedono uno smoke test e, quando necessario, osservazione sul
telefono fisico.
