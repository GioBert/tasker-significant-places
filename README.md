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

Nel prototipo attuale il campo `TIMESTAMP` ha questo significato:

- per il primo record del giorno, rappresenta il momento in cui `INIT_SIGNIFICANT_PLACES` ottiene un fix valido
- per i luoghi successivi confermati, rappresenta il momento di nascita del candidato luogo, non il momento finale di conferma

Questo rende il log piu' vicino all'orario reale di arrivo, pur mantenendo la scrittura del record solo dopo la conferma della sosta significativa.

## Parametri attuali del prototipo

- `LOG_DIR=/storage/emulated/0/_SignificantPlaces`
- `PLACE_RADIUS_METERS=100`
- `MIN_STOP_MINUTES=5`
- `PLACE_NAME_PREFIX=Luogo_`
- `GPS_MAX_ACCURACY_METERS=50`

## Principi di base

- il primo luogo della giornata viene scritto subito come record iniziale
- un nuovo luogo viene confermato solo dopo una permanenza minima configurabile
- il CSV contiene solo luoghi confermati
- per i luoghi successivi al primo, il timestamp rappresenta la nascita del candidato confermato
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

La repo contiene un prototipo Tasker funzionante con:

- `LOAD_CONFIG_DEFAULTS`
- `INIT_SIGNIFICANT_PLACES`
- `LOG_SIGNIFICANT_PLACE_SAMPLE`

Il prototipo attuale:

- legge realmente il file `tasker_globals.csv` sul telefono con fallback ai default interni
- scrive subito il primo luogo del giorno
- crea un candidato nuovo luogo quando il dispositivo esce dal raggio del luogo corrente
- conferma il candidato dopo il tempo minimo richiesto
- usa nel CSV il timestamp di nascita del candidato quando un nuovo luogo viene confermato
- scrive nel CSV solo i luoghi confermati
- gestisce una prima forma di recovery operativo su config minima mancante e cambio giorno

## Prossimi passi prioritari

- fare test reali in movimento con questa versione
- rifinire ulteriormente il comportamento operativo su riavvii e stati sporchi
- pulire le globali obsolete ancora presenti nell'ambiente Tasker
- introdurre successivamente riconoscimento di luoghi noti e report giornalieri