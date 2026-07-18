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

Il modello include controlli raccomandati, come gli intervalli validi di
latitudine e longitudine e la ricostruzione dal CSV, che non sono ancora
completi nella configurazione Tasker corrente. Serve quindi anche per definire
e provare il comportamento di destinazione dei prossimi batch.

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
