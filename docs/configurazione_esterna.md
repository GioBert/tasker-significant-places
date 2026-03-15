# Configurazione Esterna Reale

## Obiettivo

Questo documento descrive i file di configurazione esterna del progetto `tasker-significant-places`.

L'obiettivo e' rendere l'automazione parametrica senza dover modificare l'XML per cambiare soglie, percorsi o convenzioni di naming.

## Stato attuale

Nel prototipo corrente il task `LOAD_CONFIG_DEFAULTS` legge realmente il file `config/tasker_globals.csv` sul telefono e applica fallback ai default interni se il file manca o contiene errori.

Accanto a questo file, il progetto puo' evolvere introducendo anche un secondo file dedicato ai luoghi noti.

## File di configurazione previsti

### 1. `tasker_globals.csv`

Serve per definire i parametri generali del logger, come:

- cartella di output
- raggio dei luoghi
- tempo minimo di conferma
- prefisso dei nomi automatici
- accuratezza GPS minima accettata

Percorso consigliato sul telefono:

```text
/storage/emulated/0/_SignificantPlaces/config/tasker_globals.csv
```

### 2. `known_places.csv`

Serve per definire un elenco personale di luoghi noti, associando a ciascuno:

- una chiave stabile
- un nome leggibile
- una coordinata centrale
- un raggio di riconoscimento

Percorso consigliato sul telefono:

```text
/storage/emulated/0/_SignificantPlaces/config/known_places.csv
```

Per motivi di privacy, il file reale personale non deve essere versionato nella repo.

Nella repo pubblica viene invece mantenuto solo un file di esempio:

```text
config/known_places.example.csv
```

## Formato di `tasker_globals.csv`

Il formato supportato e' una riga per parametro nel formato:

```text
CHIAVE=VALORE
```

Sono ammessi anche commenti, per rendere il file piu' leggibile e manutenibile.

Esempio coerente con il file reale attuale:

```text
# Configurazione principale del progetto tasker-significant-places
# Modifica questi valori per cambiare il comportamento dell'automazione.
# Formato previsto: CHIAVE=VALORE
# Le righe che iniziano con # sono commenti.

# Cartella radice in cui Tasker scrive i file CSV giornalieri.
LOG_DIR=/storage/emulated/0/_SignificantPlaces

# Distanza massima, in metri, per considerare due punti come lo stesso luogo.
PLACE_RADIUS_METERS=100

# Tempo minimo di sosta, in minuti, necessario per confermare un nuovo luogo.
MIN_STOP_MINUTES=5

# Prefisso usato per i nomi automatici dei luoghi, ad esempio Luogo_1, Luogo_2.
PLACE_NAME_PREFIX=Luogo_

# Accuratezza GPS massima accettata, in metri, per considerare valido un campione.
GPS_MAX_ACCURACY_METERS=50
```

## Formato di `known_places.csv`

Il formato concordato per i luoghi noti e' questo:

```text
PLACE_KEY;DISPLAY_NAME;LAT;LON;RADIUS_METERS
home;Casa;44.274650;11.689900;80
work_main;Lavoro XXX;44.273120;11.721220;120
```

Significato delle colonne:

- `PLACE_KEY`: chiave stabile del luogo
- `DISPLAY_NAME`: nome leggibile da usare nel CSV
- `LAT`: latitudine del centro del luogo
- `LON`: longitudine del centro del luogo
- `RADIUS_METERS`: raggio entro cui il luogo e' considerato riconosciuto

## Regole di matching per i luoghi noti

Le decisioni attuali del progetto sono queste:

- i luoghi noti vengono usati solo per il nome
- il matching avviene solo quando un luogo e' gia' stato confermato
- se un luogo confermato cade nel raggio di un luogo noto, il nome usato nel CSV deve essere `DISPLAY_NAME`
- in questo caso non si usa il placeholder `Luogo_n`
- se piu' luoghi noti sono compatibili, vince quello col centro piu' vicino
- se nessun luogo noto corrisponde, il sistema continua a usare i nomi automatici

## Regole di parsing per `tasker_globals.csv`

Il parser della config deve seguire queste regole:

- righe vuote: ignorate
- righe che iniziano con `#`: ignorate come commenti
- righe senza `=`: ignorate
- solo la prima `=` divide chiave e valore
- spazi iniziali e finali su chiave e valore: rimossi
- chiavi sconosciute: ignorate senza bloccare il task
- valori invalidi: ignorati, con fallback al default

## Parametri minimi attualmente supportati in `tasker_globals.csv`

- `LOG_DIR`
- `PLACE_RADIUS_METERS`
- `MIN_STOP_MINUTES`
- `PLACE_NAME_PREFIX`
- `GPS_MAX_ACCURACY_METERS`

## Strategia di fallback

Ordine consigliato:

1. caricare prima i default interni
2. tentare poi la lettura del file esterno
3. sovrascrivere solo i valori validi trovati nel file

In questo modo:

- se il file manca, il sistema continua a funzionare
- se una sola riga e' errata, il resto della config resta utilizzabile
- l'automazione non dipende in modo fragile da un singolo file

## Validazione minima consigliata

Per evitare configurazioni pericolose o prive di senso, la prima versione dovrebbe applicare almeno questi controlli:

- `LOG_DIR`: stringa non vuota
- `PLACE_RADIUS_METERS`: numero > 0
- `MIN_STOP_MINUTES`: numero >= 1
- `PLACE_NAME_PREFIX`: stringa non vuota
- `GPS_MAX_ACCURACY_METERS`: numero > 0

## Comportamento in caso di errore

Se la config non puo' essere letta o contiene errori:

- il task non deve fallire
- i default interni devono restare attivi
- il problema deve essere tracciabile nel runlog o tramite una variabile tecnica dedicata

## Variabili tecniche utili per l'implementazione

Una prima implementazione della config generale usa gia' variabili di supporto come:

- `%CONFIG_FILE_PATH`
- `%CONFIG_LOAD_STATUS`
- `%CONFIG_ERROR_COUNT`

## Obiettivo pratico

Quando questa parte sara' completata anche per i luoghi noti, l'utente dovra' poter:

- cambiare soglie e comportamento del logger modificando `tasker_globals.csv`
- definire i propri luoghi noti personali tramite `known_places.csv`
- mantenere pubblica la repo senza esporre i propri luoghi reali