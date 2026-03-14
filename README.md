# tasker-significant-places

Automazione Tasker orientata all'individuazione dei luoghi significativi visitati dal dispositivo, con log minimale basato sulle soste.

## Obiettivo

Questo progetto nasce come alternativa al paradigma basato su `LEAVE / ARRIVE / MOVING`.

L'obiettivo principale e' identificare i luoghi visitati e registrare solo le soste significative. Gli spostamenti tra due luoghi non vengono loggati come eventi espliciti: sono impliciti nella successione cronologica dei luoghi registrati.

## Formato CSV

```text
TIMESTAMP;LAT;LON;PLACE_ID;NAME
2026-03-14 00.00;0.000000;0.000000;1;Luogo_1
```

## Parametri attuali del prototipo

- `LOG_DIR=/storage/emulated/0/_SignificantPlaces`
- `PLACE_RADIUS_METERS=100`
- `MIN_STOP_MINUTES=1`
- `PLACE_NAME_PREFIX=Luogo_`
- `GPS_MAX_ACCURACY_METERS=200`

## Principi di base

- il primo luogo della giornata viene scritto subito come record iniziale
- un nuovo luogo viene confermato solo dopo una permanenza minima configurabile
- il CSV contiene solo luoghi confermati
- la documentazione e' in italiano
- XML, identificatori tecnici e codice restano in inglese

## Struttura iniziale

- `config/tasker_globals.csv`
- `docs/visione_progetto.md`
- `docs/privacy_e_anonimizzazione.md`
- `docs/setup_telefono_android.md`
- `docs/convenzioni_linguistiche.md`
- `docs/precisione_dei_dati.md`
- `docs/strumenti_consigliati.md`
- `docs/specifica_logger_luoghi.md`
- `docs/mappa_variabili_tasker.md`
- `docs/configurazione_esterna.md`
- `docs/comportamento_operativo.md`

## Stato attuale

La repo contiene un primo prototipo Tasker funzionante con:

- `LOAD_CONFIG_DEFAULTS`
- `INIT_SIGNIFICANT_PLACES`
- `LOG_SIGNIFICANT_PLACE_SAMPLE`

Il prototipo attuale:

- scrive subito il primo luogo del giorno
- crea un candidato nuovo luogo quando il dispositivo esce dal raggio del luogo corrente
- conferma il candidato dopo il tempo minimo richiesto
- scrive nel CSV solo i luoghi confermati

La lettura diretta del file `config/tasker_globals.csv` non e' ancora implementata: al momento il task `LOAD_CONFIG_DEFAULTS` imposta nell'XML gli stessi valori documentati nella config.

## Prossimi passi prioritari

- leggere davvero la configurazione esterna dal telefono
- definire e implementare il comportamento operativo su cambio giorno, riavvio e recovery
- validare il prototipo con test reali in movimento
