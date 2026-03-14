# Comportamento Operativo

## Obiettivo

Questo documento definisce il comportamento operativo dell'automazione nel suo uso quotidiano sul telefono.

L'obiettivo e' rendere `tasker-significant-places` prevedibile, autonoma e capace di recuperare da situazioni comuni senza interventi manuali.

## Principio generale

Il profilo periodico deve restare sempre attivo.

Ad ogni esecuzione del task principale, il sistema deve essere in grado di capire se:

- sta continuando a lavorare sul giorno corrente
- deve inizializzare un nuovo giorno
- deve recuperare uno stato incompleto o mancante

## Avvio giornaliero

Il sistema deve produrre un CSV per ogni giorno.

Comportamento desiderato:

1. al primo ciclo utile del giorno viene eseguito `INIT_SIGNIFICANT_PLACES`
2. viene creato il file CSV giornaliero
3. viene scritto il primo luogo della giornata
4. le variabili `%CURRENT_PLACE_*` diventano la base del monitoraggio successivo

## Riconoscimento del cambio giorno

L'automazione non dovrebbe dipendere da un solo evento schedulato a mezzanotte.

Comportamento consigliato:

- ad ogni esecuzione del task principale si calcola la data corrente
- se il file giornaliero atteso non coincide con il giorno corrente, oppure se la data salvata nello stato non coincide, il sistema deve reinizializzare il giorno

In pratica il cambio giorno deve essere riconosciuto in modo opportunistico e robusto.

## Riavvio del telefono o riavvio di Tasker

Dopo un riavvio, il sistema non deve richiedere correzioni manuali nella maggior parte dei casi.

Comportamento desiderato:

- se il profilo riparte e le variabili critiche non sono valorizzate, il sistema deve rieseguire `LOAD_CONFIG_DEFAULTS`
- se manca uno stato valido del luogo corrente, il sistema deve rieseguire `INIT_SIGNIFICANT_PLACES`
- se la data e' cambiata, il sistema deve aprire un nuovo CSV del nuovo giorno

## Variabili critiche da considerare per il recovery

Per capire se il sistema e' in uno stato valido, il task principale dovrebbe poter verificare almeno queste variabili:

- `%LOG_DIR`
- `%PLACE_RADIUS_METERS`
- `%MIN_STOP_MINUTES`
- `%CURRENT_PLACE_LAT`
- `%CURRENT_PLACE_LON`
- `%CURRENT_PLACE_ID`
- `%CURRENT_PLACE_NAME`
- `%PLACE_COUNTER`

Se una di queste e' assente o palesemente invalida, il comportamento sicuro e' reinizializzare.

## Gestione del GPS scarso

Se il fix GPS non e' valido:

- non si deve scrivere nulla nel CSV
- non si deve promuovere alcun candidato
- il luogo corrente non deve cambiare
- il task deve semplicemente attendere il ciclo successivo

Questo evita che una finestra temporanea di GPS scarso sporchi il diario dei luoghi.

## Gestione di file e cartelle

Il sistema deve essere in grado di ricreare automaticamente gli elementi mancanti.

Comportamento desiderato:

- se la cartella radice non esiste, viene creata
- se la sottocartella `config` non esiste, non deve bloccare il logging di base
- se il file CSV del giorno non esiste, viene creato con header corretto

## Gestione della config esterna

Una volta implementata la lettura reale della config, il comportamento operativo consigliato e' questo:

1. caricare i default interni
2. tentare la lettura della config esterna
3. proseguire anche in caso di assenza o errori della config

In questo modo la configurazione esterna migliora la flessibilita', ma non diventa un punto singolo di fallimento.

## Mock location

La mock location e' ammessa solo come strumento di test.

Nel comportamento operativo normale:

- il sistema deve lavorare con il GPS reale
- i test con mock location non devono essere considerati validazione finale del progetto

## Flusso operativo desiderato

Flusso semplificato del task periodico:

1. verificare che la config minima sia disponibile
2. se manca, caricare o ricaricare i default
3. verificare che il giorno corrente sia inizializzato
4. se non lo e', eseguire `INIT_SIGNIFICANT_PLACES`
5. se lo e', eseguire la logica di `LOG_SIGNIFICANT_PLACE_SAMPLE`

## Obiettivo pratico

Quando questa parte sara' completata, l'automazione dovra' poter restare attiva sul telefono e continuare a produrre CSV giornalieri coerenti anche dopo:

- riavvii
- cambi giorno
- errori temporanei del GPS
- perdita temporanea di alcune variabili globali
