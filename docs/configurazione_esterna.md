# Configurazione Esterna Reale

## Obiettivo

Questo documento definisce come deve funzionare la configurazione esterna del progetto `tasker-significant-places`.

L'obiettivo e' rendere l'automazione parametrica senza dover modificare l'XML per cambiare soglie, percorsi o convenzioni di naming.

## Stato attuale

Nel prototipo corrente il file `config/tasker_globals.csv` esiste, contiene commenti esplicativi in italiano ed e' allineato ai valori usati, ma non viene ancora letto direttamente da Tasker.

Il task `LOAD_CONFIG_DEFAULTS` imposta nell'XML gli stessi valori di default.

## Obiettivo della prossima implementazione

Il task di configurazione dovra':

- leggere il file esterno dal telefono
- interpretare il contenuto riga per riga
- valorizzare le globali Tasker corrispondenti
- usare fallback sicuri se il file manca o contiene errori
- permettere all'utente di modificare il comportamento dell'automazione senza cambiare il file XML

## Posizione del file sul telefono

Percorso consigliato:

```text
/storage/emulated/0/_SignificantPlaces/config/tasker_globals.csv
```

Questa scelta tiene la configurazione dentro la stessa cartella radice del progetto e semplifica backup, esportazione e sincronizzazione.

## Formato del file

Il formato da supportare e' una riga per parametro nel formato:

```text
CHIAVE=VALORE
```

Sono ammessi anche commenti, per rendere il file piu' leggibile e manutenibile.

Esempio completo coerente con il file reale:

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
MIN_STOP_MINUTES=1

# Prefisso usato per i nomi automatici dei luoghi, ad esempio Luogo_1, Luogo_2.
PLACE_NAME_PREFIX=Luogo_

# Accuratezza GPS massima accettata, in metri, per considerare valido un campione.
GPS_MAX_ACCURACY_METERS=200
```

## Regole di parsing

Il parser della config dovra' seguire queste regole:

- righe vuote: ignorate
- righe che iniziano con `#`: ignorate come commenti
- righe senza `=`: ignorate
- solo la prima `=` divide chiave e valore
- spazi iniziali e finali su chiave e valore: rimossi
- chiavi sconosciute: ignorate senza bloccare il task
- valori invalidi: ignorati, con fallback al default

## Parametri minimi da supportare

La prima implementazione reale deve leggere almeno queste chiavi:

- `LOG_DIR`
- `PLACE_RADIUS_METERS`
- `MIN_STOP_MINUTES`
- `PLACE_NAME_PREFIX`
- `GPS_MAX_ACCURACY_METERS`

## Strategia di fallback

Il caricamento della config deve essere robusto.

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

Una prima implementazione potrebbe usare variabili di supporto come:

- `%CONFIG_FILE_PATH`
- `%CONFIG_LOAD_STATUS`
- `%CONFIG_ERROR_COUNT`

Queste variabili non fanno parte del modello dati del prodotto, ma possono aiutare debug e recovery.

## Obiettivo pratico

Quando questa parte sara' completata, l'utente dovra' poter cambiare soglie e percorso di output modificando soltanto `tasker_globals.csv`, senza reimportare un nuovo XML.
