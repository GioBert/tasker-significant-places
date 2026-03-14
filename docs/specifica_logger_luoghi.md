# Specifica Del Logger Dei Luoghi

## Obiettivo

Questa specifica descrive il comportamento del primo prototipo di automazione Tasker per `tasker-significant-places`.

Il sistema deve registrare nel CSV solo i luoghi significativi visitati, ignorando gli stati di movimento come eventi autonomi.

## Output atteso

Il file CSV deve avere questo formato:

```text
TIMESTAMP;LAT;LON;PLACE_ID;NAME
2026-03-14 00.00;0.000000;0.000000;1;Luogo_1
```

## Principio generale

Il logger non scrive eventi di partenza o arrivo. Scrive soltanto un nuovo record quando una nuova posizione si dimostra sufficientemente stabile da essere considerata un luogo significativo.

Tra un luogo e il successivo esiste implicitamente uno spostamento, ma questo non viene scritto nel CSV del logger di base.

## Parametri esterni

Il comportamento del logger deve essere guidato il piu' possibile dal file:

- `config/tasker_globals.csv`

Formato previsto:

```text
CHIAVE=valore
```

Parametri iniziali previsti:

- `LOG_DIR`
- `PLACE_RADIUS_METERS`
- `MIN_STOP_MINUTES`
- `SAMPLE_INTERVAL_MINUTES`
- `PLACE_NAME_PREFIX`
- `CSV_FILENAME_PATTERN`
- `WRITE_DAY_START_IMMEDIATELY`
- `GPS_MAX_ACCURACY_METERS`

## Concetti logici minimi

Il prototipo deve distinguere tra questi elementi logici:

- luogo confermato corrente
- candidato nuovo luogo
- tempo di inizio del candidato
- numero di campioni coerenti del candidato
- contatore progressivo dei luoghi

Non serve uno stato esplicito di tipo `MOVING`.

## Variabili interne minime suggerite

Nomi indicativi in inglese, coerenti con il resto del progetto:

- `%CURRENT_PLACE_LAT`
- `%CURRENT_PLACE_LON`
- `%CURRENT_PLACE_ID`
- `%CURRENT_PLACE_NAME`
- `%CANDIDATE_PLACE_LAT`
- `%CANDIDATE_PLACE_LON`
- `%CANDIDATE_SINCE`
- `%CANDIDATE_CONFIRM_COUNT`
- `%PLACE_COUNTER`
- `%LAST_SAMPLE_TIME`
- `%GPS_ACCURACY`
- `%FIX_VALID`
- `%DIST_FROM_CURRENT`
- `%DIST_FROM_CANDIDATE`

## Regola del primo luogo giornaliero

All'inizio della giornata, oppure al primo avvio utile del task giornaliero:

1. viene acquisita una posizione valida
2. viene creato immediatamente il primo record del giorno
3. il record viene scritto con:
   - `PLACE_ID = 1`
   - `NAME = Luogo_1`
4. le coordinate di quel record diventano il luogo confermato corrente

Questa regola e' attiva se `WRITE_DAY_START_IMMEDIATELY=true`.

## Regola per restare nello stesso luogo

Un campione valido e' considerato appartenente allo stesso luogo corrente se la distanza dal luogo confermato corrente e' minore o uguale a:

- `PLACE_RADIUS_METERS`

In questo caso:

- non si scrive nulla nel CSV
- l'eventuale candidato nuovo luogo viene azzerato

## Regola per creare un candidato nuovo luogo

Se un campione valido e' oltre `PLACE_RADIUS_METERS` rispetto al luogo corrente, non viene scritto subito nel CSV.

Invece:

1. se non esiste un candidato attivo, il campione diventa il primo candidato
2. se esiste gia' un candidato, si misura la distanza dal candidato
3. se il nuovo campione e' coerente con il candidato, si aggiorna il conteggio dei campioni coerenti
4. se non e' coerente, il candidato viene sostituito con il nuovo punto

## Coerenza del candidato

Nel primo prototipo si propone di usare la stessa soglia spaziale del luogo per verificare la coerenza del candidato:

- distanza dal candidato <= `PLACE_RADIUS_METERS`

Questa scelta semplifica il modello iniziale.

## Regola di conferma di un nuovo luogo

Un candidato diventa nuovo luogo confermato solo se entrambe le condizioni sono vere:

1. il tempo trascorso dal primo campione del candidato e' maggiore o uguale a `MIN_STOP_MINUTES`
2. i campioni recenti restano coerenti con il candidato

Quando il candidato viene confermato:

- `PLACE_COUNTER` viene incrementato
- viene creato un nuovo `PLACE_ID`
- viene creato un nuovo `NAME` con il prefisso configurato, ad esempio `Luogo_2`
- il nuovo record viene scritto nel CSV
- il luogo confermato corrente viene aggiornato
- il candidato viene azzerato

## Regola per ignorare soste brevi

Una posizione nuova che non riesce a mantenersi stabile abbastanza a lungo non deve produrre alcun record nel CSV.

Questo e' il meccanismo che deve filtrare:

- traffico lento
- semafori lunghi
- soste tecniche brevi
- fermate non significative

## Validita' del fix GPS

Un campione puo' essere usato solo se il fix e' considerato valido.

Nel primo prototipo la validita' deve almeno dipendere da:

- presenza di coordinate
- accuratezza GPS <= `GPS_MAX_ACCURACY_METERS`

Se il fix non e' valido:

- non si scrive nulla
- non si promuove alcun candidato
- non si aggiorna il luogo corrente

## Politica sul CSV

Il CSV del logger di base deve contenere solo luoghi confermati.

Non devono comparire:

- eventi `LEAVE`
- eventi `ARRIVE`
- eventi `MOVING`
- candidati non confermati

## Naming dei luoghi

Nel primo prototipo il nome del luogo e' automatico:

- `Luogo_1`
- `Luogo_2`
- `Luogo_3`

In una fase successiva si potra' introdurre:

- rinomina manuale
- luoghi noti
- luoghi ricorrenti

## Ricostruzione successiva dei viaggi

I viaggi non vengono loggati dall'automazione di base.

Saranno ricostruibili successivamente a partire da due record consecutivi nel CSV:

- origine = luogo precedente
- destinazione = luogo successivo
- durata = differenza tra i timestamp

## Caso minimo di esempio

Supponiamo:

- `PLACE_RADIUS_METERS = 100`
- `MIN_STOP_MINUTES = 10`

Sequenza:

1. il giorno parte in `Luogo_1`
2. il dispositivo si sposta
3. per alcuni minuti i campioni restano dispersi o brevi: nessuna scrittura
4. il dispositivo resta stabile in un nuovo punto per almeno 10 minuti
5. il sistema scrive `Luogo_2`

CSV atteso:

```text
TIMESTAMP;LAT;LON;PLACE_ID;NAME
2026-03-14 00.00;0.000000;0.000000;1;Luogo_1
2026-03-14 10.20;0.000900;0.000900;2;Luogo_2
```

## Vincoli del primo prototipo

Per mantenere il primo XML semplice, il prototipo non deve ancora includere:

- reverse geocoding
- luoghi noti
- report giornalieri
- classificazione esplicita dei viaggi
- log di debug troppo verbosi nel CSV finale

## Obiettivo del primo test reale

Il primo prototipo deve dimostrare soprattutto questo:

- riduzione netta dei falsi stop/start rispetto al paradigma precedente
- CSV molto piu' pulito
- registrazione delle vere soste significative
- possibilita' di ricostruire i viaggi in un secondo momento
