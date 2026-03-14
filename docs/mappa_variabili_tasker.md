# Mappa Delle Variabili Tasker

## Scopo

Questo documento elenca le variabili previste per il primo prototipo XML di `tasker-significant-places`.

L'obiettivo e' chiarire quali variabili sono:

- di configurazione esterna
- di stato persistente
- temporanee di campionamento
- di supporto alla scrittura del CSV

## Variabili di configurazione esterna

Queste variabili devono essere lette dal file `config/tasker_globals.csv` e poi valorizzate come globali Tasker.

### `%LOG_DIR`

Percorso base in cui creare cartelle e file CSV.

### `%PLACE_RADIUS_METERS`

Distanza massima per considerare un campione appartenente allo stesso luogo confermato o allo stesso candidato.

### `%MIN_STOP_MINUTES`

Durata minima della sosta per confermare un nuovo luogo.

### `%SAMPLE_INTERVAL_MINUTES`

Intervallo teorico di campionamento. Utile soprattutto per verifica e debug.

### `%PLACE_NAME_PREFIX`

Prefisso per il nome automatico dei luoghi. Esempio: `Luogo_`.

### `%CSV_FILENAME_PATTERN`

Pattern logico del nome file. Nel primo prototipo puo' anche essere gestito indirettamente, ma va mantenuto come variabile di configurazione.

### `%WRITE_DAY_START_IMMEDIATELY`

Se `true`, il primo luogo giornaliero viene scritto subito.

### `%GPS_MAX_ACCURACY_METERS`

Soglia massima di accuratezza accettabile per considerare valido un fix GPS.

## Variabili di stato persistente

Queste variabili rappresentano lo stato attivo del logger tra un campione e il successivo.

### `%CURRENT_PLACE_LAT`

Latitudine del luogo confermato corrente.

### `%CURRENT_PLACE_LON`

Longitudine del luogo confermato corrente.

### `%CURRENT_PLACE_ID`

Identificativo numerico del luogo confermato corrente.

### `%CURRENT_PLACE_NAME`

Nome assegnato al luogo confermato corrente.

### `%PLACE_COUNTER`

Contatore progressivo dei luoghi confermati nel giorno corrente.

### `%CANDIDATE_PLACE_LAT`

Latitudine del candidato nuovo luogo.

### `%CANDIDATE_PLACE_LON`

Longitudine del candidato nuovo luogo.

### `%CANDIDATE_SINCE`

Timestamp di creazione del candidato nuovo luogo.

### `%CANDIDATE_CONFIRM_COUNT`

Numero di campioni coerenti accumulati dal candidato.

### `%LAST_SAMPLE_TIME`

Timestamp dell'ultimo campione elaborato con successo.

## Variabili temporanee di campionamento

Queste variabili possono essere aggiornate ad ogni esecuzione del task principale.

### `%cur_lat`

Latitudine del campione corrente.

### `%cur_lon`

Longitudine del campione corrente.

### `%timestamp`

Timestamp formattato per il CSV.

### `%GPS_ACCURACY`

Accuratezza del fix GPS corrente.

### `%FIX_VALID`

Indicatore booleano che segnala se il fix corrente e' utilizzabile.

### `%DIST_FROM_CURRENT`

Distanza tra il campione corrente e il luogo confermato corrente.

### `%DIST_FROM_CANDIDATE`

Distanza tra il campione corrente e il candidato nuovo luogo.

### `%sample_gap`

Differenza temporale rispetto al campione precedente. Utile per analisi e debug.

## Variabili per la gestione del file CSV

### `%today`

Data breve usata per comporre il nome file.

### `%year`

Anno corrente.

### `%month`

Mese corrente.

### `%day`

Giorno corrente, se serve separatamente.

### `%log_file`

Percorso finale del CSV giornaliero.

### `%file_exists`

Indicatore di esistenza del file, utile per scrivere l'header solo la prima volta.

## Variabili inizializzate all'avvio giornaliero

Nel primo task di inizializzazione giornaliera ci aspettiamo almeno:

- `%PLACE_COUNTER = 0` prima della scrittura del primo luogo
- `%CURRENT_PLACE_LAT = 0`
- `%CURRENT_PLACE_LON = 0`
- `%CURRENT_PLACE_ID = 0`
- `%CURRENT_PLACE_NAME` vuota
- `%CANDIDATE_PLACE_LAT = 0`
- `%CANDIDATE_PLACE_LON = 0`
- `%CANDIDATE_SINCE = 0`
- `%CANDIDATE_CONFIRM_COUNT = 0`
- `%LAST_SAMPLE_TIME = 0`

## Variabili azzerate quando il candidato decade

Quando un candidato viene invalidato o sostituito, vanno azzerate almeno:

- `%CANDIDATE_PLACE_LAT`
- `%CANDIDATE_PLACE_LON`
- `%CANDIDATE_SINCE`
- `%CANDIDATE_CONFIRM_COUNT`

## Variabili aggiornate quando un nuovo luogo viene confermato

Quando un candidato diventa luogo confermato:

- `%PLACE_COUNTER` incrementa
- `%CURRENT_PLACE_ID` assume il nuovo valore
- `%CURRENT_PLACE_NAME` viene costruita con `%PLACE_NAME_PREFIX`
- `%CURRENT_PLACE_LAT` e `%CURRENT_PLACE_LON` vengono aggiornate
- le variabili del candidato vengono azzerate

## Nota di implementazione

Nel primo XML conviene mantenere il numero di variabili il piu' basso possibile, ma senza comprimere troppo concetti diversi nella stessa variabile. La chiarezza della logica vale piu' di una minimizzazione prematura.
