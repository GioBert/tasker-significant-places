# tasker-significant-places

![Tasker Significant Places](docs/assets/hero.png)

`tasker-significant-places` e' un progetto Tasker per costruire un diario
giornaliero dei luoghi nei quali il telefono si e' fermato davvero, evitando di
registrare un tracciato continuo degli spostamenti.

L'idea nasce da un'esigenza pratica: non interessa registrare ogni singolo spostamento, ma capire con chiarezza **dove si e' stati** e **quando si e' arrivati in un luogo significativo**. In molte situazioni quotidiane un log di movimento continuo produce troppo rumore: semafori, traffico lento, soste brevi, pause tecniche. Questo progetto cerca invece di estrarre solo le soste che hanno davvero senso nel racconto della giornata.

Questo repository rappresenta l'evoluzione di prototipi precedenti, ma con un cambio importante di paradigma: non cerca piu' di descrivere il viaggio come sequenza di eventi di partenza, movimento e arrivo. Si concentra invece sui **luoghi significativi confermati**. Lo spostamento resta implicito tra due luoghi consecutivi.

## In parole semplici

L'automazione gira sul telefono, controlla periodicamente la posizione GPS e si comporta cosi':

1. identifica il luogo corrente noto
2. osserva se il telefono resta ancora in quell'area
3. se il telefono esce da quell'area, apre un candidato nuovo luogo
4. se il candidato resta stabile abbastanza a lungo, lo conferma
5. solo a quel punto scrive una riga nel CSV

Questo significa che il file finale non e' un tracciato di tutto il movimento, ma una lista pulita dei posti in cui il dispositivo si e' fermato in modo significativo.

## Schema a blocchi

```text
Campione GPS
    |
    v
Fix valido?
    | no -> ignora il campione
    | yes
    v
Dentro il luogo corrente?
    | yes -> resta nello stesso luogo, nessuna nuova riga
    | no
    v
Crea o aggiorna un candidato nuovo luogo
    |
    v
Il candidato resta stabile abbastanza a lungo?
    | no -> continua ad osservare
    | yes
    v
Conferma il nuovo luogo
    |
    v
Scrivi una riga nel CSV
```

## Cosa produce

Il risultato e' un CSV giornaliero con questo formato:

```text
TIMESTAMP;LAT;LON;PLACE_ID;NAME
2026-03-14 00.00;0.000000;0.000000;1;Luogo_1
```

Nel prototipo attuale il campo `TIMESTAMP` ha questo significato:

- per il primo record del giorno, rappresenta il momento in cui `INIT_SIGNIFICANT_PLACES` ottiene un fix valido
- per i luoghi successivi confermati, rappresenta il momento di nascita del candidato luogo, non il momento finale di conferma

Questo rende il log piu' vicino all'orario reale di arrivo, pur mantenendo la scrittura del record solo dopo che la sosta e' stata confermata.

## Avvio rapido

1. leggere [setup del telefono Android](docs/setup_telefono_android.md);
2. copiare sul telefono i file di configurazione partendo dagli esempi in
   `config/`;
3. importare `significant_places_tasker.xml` in Tasker;
4. verificare percorsi, permessi e valori con
   [configurazione esterna](docs/configurazione_esterna.md);
5. creare un backup manuale prima di ogni modifica seguendo
   [backup e ripristino](docs/backup_ripristino_tasker.md).

Il file `config/known_places.example.csv` contiene soltanto dati sintetici. I
file reali con coordinate e nomi dei luoghi devono restare locali e non devono
essere aggiunti a Git.

## Parte tecnica

### Parametri attuali del prototipo

- `LOG_DIR=/storage/emulated/0/_SignificantPlaces`
- `PLACE_RADIUS_METERS=100`
- `MIN_STOP_MINUTES=5`
- `PLACE_NAME_PREFIX=Luogo_`
- `GPS_MAX_ACCURACY_METERS=50`

### Principi di base

- il primo luogo della giornata viene scritto subito come record iniziale e, se corrisponde a un luogo noto, ne usa il nome
- un nuovo luogo viene confermato solo dopo una permanenza minima configurabile
- il CSV contiene solo luoghi confermati
- per i luoghi successivi al primo, il timestamp rappresenta la nascita del candidato confermato
- la documentazione e' in italiano
- XML, identificatori tecnici e codice restano in inglese

### Struttura della repo

- `significant_places_tasker.xml`: export pubblico anonimizzato di Tasker;
- `config/`: default pubblici ed esempio sintetico dei luoghi noti;
- `docs/`: specifiche, setup, privacy, validazione e procedure operative;
- `tools/`: simulatore, validatore e generatori dei backup di test;
- `tests/`: regressioni locali e percorso sintetico.

### Stato attuale

La repo contiene un'automazione Tasker funzionante e validata sul dispositivo
di test con:

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
- recupera dal CSV giornaliero luogo corrente e massimo `PLACE_ID` senza
  duplicare record;
- interrompe l'inizializzazione prima della scrittura se il CSV esistente e'
  vuoto, malformato o incoerente;
- espone stato e diagnostica persistenti tramite le variabili `%RECOVERY_*`

La recovery dal CSV giornaliero e la scrittura transazionale sono state
validate sul runtime Tasker. I test locali verificano inoltre struttura XML,
fallback di configurazione, replay CSV, commit dello stato e trasformazioni dei
backup di collaudo.

Per eseguire la suite:

```powershell
python -m unittest discover -s tests -v
```

## Affidabilita' dopo il riavvio

Sul dispositivo Xiaomi/MIUI usato per i test, le sole impostazioni di autostart
e batteria non hanno garantito in modo ripetibile la ricreazione automatica di
`MonitorService`. La presenza di Tasker nella schermata delle app recenti non
dimostra che il processo sia attivo.

E' stato quindi validato un watchdog MacroDroid Premium separato dalla logica
del progetto:

```text
Avvio Dispositivo -> Attendi 1 minuto -> Lancia Tasker
```

Il watchdog non modifica profili, task, variabili o CSV. Configurazione,
permessi e procedura di verifica sono documentati nel
[setup Android](docs/setup_telefono_android.md) e nella
[validazione del dispositivo](docs/validazione_dispositivo_test.md).

## Privacy

La repository pubblica non deve contenere coordinate reali, luoghi conosciuti,
percorsi, seriali ADB, identificativi Android o backup completi del telefono.
La strategia completa e la checklist prima del push sono descritte in
[privacy e anonimizzazione](docs/privacy_e_anonimizzazione.md).

### Prossimi passi prioritari

- continuare i test reali in movimento con questa versione
- osservare nel tempo l'affidabilita' del watchdog dopo riavvio e primo sblocco
- pulire le globali obsolete ancora presenti nell'ambiente Tasker
- valutare una strategia ibrida basata su movimento, con fallback periodico e
  confronto energetico controllato
- continuare a rifinire e testare il riconoscimento dei luoghi noti e introdurre report giornalieri
