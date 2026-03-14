# Mappa Delle Variabili Tasker

## Scopo

Questo documento elenca le variabili effettivamente usate dal prototipo attuale di `tasker-significant-places`.

L'obiettivo e' chiarire quali variabili sono:

- di configurazione/default
- di stato persistente
- temporanee di campionamento
- di supporto alla scrittura del CSV

## Variabili di configurazione attuali

Il prototipo attuale imposta queste variabili nel task `LOAD_CONFIG_DEFAULTS`.

### `%LOG_DIR`

Percorso base in cui creare cartelle e file CSV.

### `%PLACE_RADIUS_METERS`

Distanza massima per considerare un campione appartenente allo stesso luogo confermato o allo stesso candidato.

### `%MIN_STOP_MINUTES`

Durata minima della sosta per confermare un nuovo luogo.

### `%PLACE_NAME_PREFIX`

Prefisso per il nome automatico dei luoghi. Esempio: `Luogo_`.

### `%GPS_MAX_ACCURACY_METERS`

Soglia massima di accuratezza accettabile per considerare valido un fix GPS.

## Nota sulla config esterna

Il file `config/tasker_globals.csv` e' allineato a questi valori, ma non viene ancora letto direttamente dal prototipo corrente.

## Variabili di stato persistente

### `%CURRENT_PLACE_LAT`
### `%CURRENT_PLACE_LON`
### `%CURRENT_PLACE_ID`
### `%CURRENT_PLACE_NAME`
### `%PLACE_COUNTER`
### `%CANDIDATE_PLACE_LAT`
### `%CANDIDATE_PLACE_LON`
### `%CANDIDATE_SINCE`
### `%CANDIDATE_CONFIRM_COUNT`
### `%LAST_SAMPLE_TIME`

Queste variabili rappresentano lo stato attivo del logger tra un campione e il successivo.

## Variabili temporanee di campionamento

### `%cur_lat`
### `%cur_lon`
### `%timestamp`
### `%now_seconds`
### `%GPS_ACCURACY`
### `%FIX_VALID`
### `%DIST_FROM_CURRENT`
### `%DIST_FROM_CANDIDATE`
### `%AT_CURRENT_PLACE`
### `%AT_CANDIDATE_PLACE`
### `%candidate_age_seconds`
### `%candidate_min_seconds`

Queste variabili vengono calcolate durante l'esecuzione del task principale.

## Variabili per la gestione del file CSV

### `%today`
### `%year`
### `%month`
### `%log_file`
### `%file_exists`

## Variabili inizializzate nel task giornaliero

Nel prototipo attuale `INIT_SIGNIFICANT_PLACES` inizializza almeno:

- `%PLACE_COUNTER = 1`
- `%CURRENT_PLACE_LAT`
- `%CURRENT_PLACE_LON`
- `%CURRENT_PLACE_ID = 1`
- `%CURRENT_PLACE_NAME = Luogo_1`
- `%CANDIDATE_PLACE_LAT = 0`
- `%CANDIDATE_PLACE_LON = 0`
- `%CANDIDATE_SINCE = 0`
- `%CANDIDATE_CONFIRM_COUNT = 0`
- `%LAST_SAMPLE_TIME = %TIMES`

## Variabili azzerate quando il candidato decade o viene promosso

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

Nel prototipo attuale il numero di variabili e' ancora orientato al debug e alla leggibilita' della logica. Eventuali pulizie ulteriori andranno fatte solo dopo ulteriori test reali.