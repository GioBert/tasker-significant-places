# Registro Delle Modifiche Tasker

## Scopo

Questo registro conserva una traccia sintetica dei batch applicati alla
configurazione operativa. Non deve contenere coordinate, nomi di luoghi, hash
di backup privati o altri dati personali.

Per ogni batch annotare:

- identificativo e data;
- task o profili coinvolti;
- sintesi delle modifiche;
- documentazione Tasker consultata;
- checkpoint di rollback disponibile in locale;
- test eseguiti ed esito;
- decisione finale: mantenuto, osservazione o ripristinato.

## Batch Registrati

### B000 - Baseline Pre-Hardening - 18 Luglio 2026

Ambito:

- profilo periodico e tre task del progetto;
- assegnazione del nome `SIGNIFICANT_PLACES_PERIODIC_2MIN` al profilo e al
  contesto temporale;
- verifica della procedura di backup, pulizia e ripristino.

Checkpoint:

- backup privato datato verificato tramite XML e SHA-256;
- copia separata della configurazione esterna e dei CSV;
- dettagli e hash conservati esclusivamente nel contesto locale.

Test:

- pulizia e ripristino manuale riusciti;
- profilo, tre task e 126 azioni ripristinati;
- `MonitorService` e allarme periodico ricreati;
- due cicli automatici consecutivi conclusi con `ExitOK`;
- file esterni rimasti invariati.

Esito: **baseline mantenuta**.

Note:

- il test non ha cancellato le variabili;
- le criticita' applicative note non sono state ancora corrette e saranno
  distribuite in batch successivi.

### B001 - Allineamento Dei Fallback E Controllo Coordinate - 18 Luglio 2026

Ambito:

- task `LOAD_CONFIG_DEFAULTS`;
- task `INIT_SIGNIFICANT_PLACES`.

Modifiche:

- fallback interno `MIN_STOP_MINUTES` allineato da 1 a 5 minuti;
- fallback interno `GPS_MAX_ACCURACY_METERS` allineato da 200 a 50 metri;
- ripristinato il controllo congiunto che richiede sia `%gl_latitude` sia
  `%gl_longitude` impostate prima di considerare inizializzata la posizione.

Riferimenti Tasker:

- guida ufficiale `Variable Set`;
- guida ufficiale `Action Edit`, incluse le condizioni delle azioni.

Checkpoint:

- baseline pre-hardening B000 conservata localmente;
- backup nativo post-B001 creato sul telefono e copiato nell'area privata
  locale;
- integrita' verificata tramite SHA-256, conservato soltanto nel contesto
  locale.

Test:

- ricontrollo visuale delle tre modifiche dopo chiusura e riapertura di
  Tasker;
- `MonitorService` verificato attivo;
- backup post-B001 valido: un profilo, tre task, 126 azioni e 29 variabili;
- validatore locale: struttura e collegamenti validi;
- assenti gli errori e gli avvisi relativi alle tre correzioni B001;
- rimangono quattro avvisi noti, fuori dall'ambito di questo batch.

Esito: **mantenuto; osservazione durante il normale utilizzo**.

### B002 - Validazione Completa Del Fix GPS - 18 Luglio 2026

Ambito:

- task `INIT_SIGNIFICANT_PLACES`;
- task `LOG_SIGNIFICANT_PLACE_SAMPLE`;
- validatore XML e simulatore locali.

Modifiche:

- aggiunta all'inizializzazione la stessa validazione del fix usata nel ciclo
  principale;
- richiesti latitudine, longitudine, accuratezza e soglia numeriche e finite;
- latitudine ammessa nell'intervallo inclusivo da -90 a 90;
- longitudine ammessa nell'intervallo inclusivo da -180 a 180;
- accuratezza ammessa da zero alla soglia configurata;
- soglia di accuratezza richiesta finita e maggiore di zero;
- mantenuti i controlli B001 su latitudine e longitudine impostate, aggiungendo
  `%FIX_VALID ~ true` all'`If` di inizializzazione;
- aggiornati i test locali per coordinate fuori intervallo, accuratezza
  negativa e valori esattamente sui limiti.

Riferimenti Tasker:

- guida ufficiale `JavaScriptlet`;
- guida ufficiale `JavaScript Support`;
- guida ufficiale `Flow Control`;
- guida ufficiale `Task Edit`, inclusa l'aggiunta dopo l'azione selezionata.

Checkpoint:

- backup post-B001 conservato come rollback pre-B002;
- backup nativo post-B002 creato sul telefono e copiato nell'area privata
  locale;
- integrita' verificata tramite SHA-256, conservato soltanto nel contesto
  locale.

Test:

- ricontrollo integrale dei due JavaScriptlet tramite interfaccia e backup;
- un profilo, tre task, 127 azioni e 29 variabili nel backup post-B002;
- struttura XML e collegamenti validi;
- scomparsi gli avvisi `INIT_ACCURACY_UNCHECKED` e
  `GPS_RANGE_UNCHECKED`;
- 12 test locali superati;
- `MonitorService` attivo con `crashCount=0`;
- due cicli automatici post-Apply consecutivi conclusi con `ExitOK`;
- nessuna esecuzione manuale dei task e nessuna posizione di test generata.

Esito: **mantenuto; osservazione durante il normale utilizzo**.

### B003 - Conferma Multipla Del Luogo Candidato - 18 Luglio 2026

Ambito:

- task `LOG_SIGNIFICANT_PLACE_SAMPLE`;
- condizione di conferma del luogo candidato;
- validatore XML locale.

Modifiche:

- aggiunta alla condizione sul tempo minimo la richiesta
  `%CANDIDATE_CONFIRM_COUNT > 1`;
- un candidato non puo' quindi essere confermato dalla sola osservazione
  iniziale, anche in presenza di un intervallo temporale lungo;
- il contatore gia' incrementato dall'automazione diventa parte effettiva
  della decisione;
- aggiornato il validatore per controllare strutturalmente l'uso del contatore.

Riferimenti Tasker:

- guida ufficiale `Flow Control` per gli operatori matematici;
- guida ufficiale `Action Edit` per le condizioni multiple in AND.

Checkpoint:

- backup post-B002 conservato come rollback pre-B003;
- backup nativo post-B003 creato sul telefono e copiato nell'area privata
  locale;
- integrita' verificata tramite SHA-256, conservato soltanto nel contesto
  locale.

Test:

- verificato `%CANDIDATE_CONFIRM_COUNT > 1` nell'interfaccia e nel backup;
- intercettato e corretto prima dell'Apply un doppio simbolo `%` nel nome
  della variabile;
- struttura XML e collegamenti validi;
- scomparso l'avviso `CONFIRM_COUNT_UNUSED`;
- 13 test locali superati e scansione privacy dell'export pubblico senza
  corrispondenze;
- `MonitorService` attivo con `crashCount=0` e allarme periodico presente;
- due cicli automatici post-Apply consecutivi conclusi con `ExitOK`.

Esito: **mantenuto; osservazione durante il normale utilizzo**.

### B004 - Commit Dello Stato Dopo La Scrittura CSV - 18 Luglio 2026

Ambito:

- task `LOG_SIGNIFICANT_PLACE_SAMPLE`;
- sequenza di conferma e registrazione di un nuovo luogo;
- generazione e importazione controllata di un backup XML completo.

Modifiche:

- il nuovo contatore, ID, nome e coordinate vengono prima preparati nelle
  variabili locali `%next_place_*`;
- il matching con i luoghi conosciuti aggiorna il nome locale preparato;
- la riga CSV usa esclusivamente i valori locali preparati;
- le variabili globali vengono aggiornate soltanto nelle cinque azioni
  successive a `Scrivi File`;
- se `Scrivi File` fallisce, il comportamento predefinito di Tasker interrompe
  il task prima del commit globale e conserva candidato e stato precedente;
- aggiunto un generatore ripetibile del backup candidato B004.

Distribuzione controllata:

- sorgente: backup nativo post-B003 conservato privatamente;
- candidato generato e validato localmente;
- nome breve sul telefono: `B004.xml`;
- importazione tramite `Dati > Ripristinare > Backup manuale`;
- checkpoint nativo successivo creato come `OK4.xml`;
- il candidato importato e' stato spostato nell'archivio, senza cancellarlo.

Riferimenti Tasker:

- guida ufficiale `Write File`;
- guida ufficiale `Action Edit`, parametro `Continue Task After Error`;
- guida ufficiale delle variabili locali `%err` e `%errmsg`;
- guida ufficiale `JavaScript Support` per la propagazione delle variabili
  locali modificate da un JavaScriptlet;
- guide ufficiali `Data Backup` e `Import Data`.

Checkpoint:

- backup post-B003 conservato come rollback pre-B004;
- backup nativo post-B004 `OK4.xml` sul telefono;
- copia privata locale verificata tramite SHA-256;
- candidato B004 e versioni intermedie conservati negli archivi locali e del
  telefono.

Test:

- 132 azioni complessive e 85 nel task principale;
- azione 63 `Scrivi File`, seguita dalle cinque assegnazioni globali 64-68;
- zero differenze nelle azioni tra candidato e backup nativo riesportato da
  Tasker;
- struttura XML e collegamenti validi;
- tre cicli automatici post-import conclusi con `ExitOK`;
- `MonitorService` attivo con `crashCount=0` e allarme periodico presente;
- nessun `ExitErr` o task malformato osservato.

Verifica sintetica successiva:

- una configurazione temporanea ha reindirizzato l'output sotto `TestData` e
  ridotto a un minuto la sola soglia del test;
- Mocaction ha alimentato Android sui provider `gps` e `fused`, ma l'azione
  `5.19` (`Ottieni Posizione v2`) e' andata in timeout dopo 20 secondi;
- il Run Log ha associato tutti i 21 `ExitErr` della finestra di test alla
  stessa azione di acquisizione;
- il ramo di conferma, `Scrivi File` e commit globale B004 non e' stato
  raggiunto;
- dopo il ripristino del checkpoint, i cicli reali sono tornati `ExitOK` e i
  file operativi preesistenti sono risultati invariati.

Questa prova non modifica l'esito strutturale del batch, ma lascia aperta la
validazione funzionale del ramo di nuova posizione. Mocaction non va usata per
considerare quel ramo collaudato su questo dispositivo.

Validazione funzionale successiva:

- aggiunto `tools/build_injected_location_test_backup.py`, che genera da un
  backup nativo un candidato temporaneo con output isolato e tre valori di
  posizione sintetici al posto di `Ottieni Posizione v2`;
- il generatore richiede esattamente 85 azioni B004 e produce 87 azioni,
  verificando che i cinque commit globali restino dopo `Scrivi File`;
- 15 test locali superati, incluso il controllo automatico del candidato
  iniettato;
- sul telefono e' stata scritta una sola riga sintetica e lo stato globale e'
  risultato coerente con la riga;
- candidato azzerato e nessuna duplicazione osservata;
- ripristino da `PREM.xml` completato con monitor e allarme attivi;
- zero file preesistenti modificati o mancanti nel confronto SHA-256;
- backup di prova archiviati sotto
  `archive/2026-07-18-location-tests` sul telefono.

Esito: **mantenuto; validazione runtime del ramo transazionale superata in
ambiente sintetico isolato**.

### B005 - Recovery Dal CSV Giornaliero - 18 Luglio 2026

Ambito:

- task `INIT_SIGNIFICANT_PLACES`;
- ricostruzione dello stato dopo import, perdita delle variabili o riavvio;
- protezione dei CSV esistenti e diagnostica persistente.

Modifiche:

- se il CSV del giorno esiste, viene letto e validato prima del fix GPS;
- l'ultimo record ripristina luogo corrente, ID e nome, mentre il massimo
  `PLACE_ID` diventa `%PLACE_COUNTER` per evitare collisioni;
- un CSV con sola intestazione viene inizializzato senza duplicare l'header;
- file vuoti, header errati, righe malformate, date incoerenti, coordinate non
  finite o fuori intervallo, ID non positivi e nomi vuoti causano uno stop con
  errore prima della scrittura;
- un secondo `Test File` impedisce di creare o appendere se lo stato del file
  e il ramo scelto sono incoerenti;
- aggiunte `%RECOVERY_STATUS`, `%RECOVERY_ERROR_COUNT` e
  `%RECOVERY_LAST_ERROR`;
- aggiunto `tools/build_b005_csv_recovery_backup.py` e reso rigoroso il replay
  CSV del simulatore locale.

Riferimenti Tasker:

- guida ufficiale `Test File`: un test fallito cancella la variabile risultato;
- guida ufficiale `Variables`: una variabile non inizializzata resta letterale;
- guide ufficiali `Read File`, `JavaScriptlet`, `If`, `Stop` e `Write File`.

Checkpoint:

- `PRE5.xml`: rollback immediato pre-B005;
- `OK5.xml`: backup nativo della configurazione runtime validata;
- `OK4.xml`: checkpoint B004 precedente;
- tentativi intermedi conservati, non cancellati, nelle cartelle archivio;
- copie complete e log con dati reali conservati soltanto nella TestData
  privata locale.

Test e anomalie intercettate:

- il primo candidato usava un controllo booleano non supportato per
  `Test File` e aggiungeva una riga; il CSV originale e' stato ripristinato
  byte per byte dalla copia preventiva e il candidato e' stato ritirato;
- i candidati successivi hanno terminato fail-closed senza modificare il CSV,
  permettendo di isolare semantica del risultato, controllo di flusso e ordine
  di inizializzazione;
- il test manuale corretto richiede prima `LOAD_CONFIG_DEFAULTS`, come avviene
  nel flusso reale, e poi `INIT_SIGNIFICANT_PLACES`;
- recovery finale: `%RECOVERY_STATUS=recovered`, `%PLACE_COUNTER=3`, CSV
  invariato byte per byte, `MonitorService` attivo e nove allarmi Tasker;
- task periodico successivo concluso con `ExitOK`;
- 20 test locali superati e validatore XML senza errori o warning.

Nota: il checkpoint runtime `OK5.xml` contiene una diagnostica cosmetica che,
in assenza di errore, puo' mostrare il riferimento locale letterale. Il
generatore e l'export pubblico successivi usano il valore esplicito `none`.
La recovery e i dati non sono influenzati.

Esito: **mantenuto; recovery runtime da CSV esistente superata**.

### Watchdog Di Riavvio MacroDroid - 18 Luglio 2026

Ambito:

- mitigazione esterna per la mancata ricreazione automatica di
  `MonitorService` dopo alcuni riavvii reali del telefono;
- nessuna modifica ai profili, task o dati Significant Places.

Configurazione:

- MacroDroid `5.65.9`, macro `WATCHDOG_TASKER_BOOT`;
- evento `Avvio Dispositivo`;
- attesa di un minuto senza allarme esatto;
- avvio normale di Tasker, senza forzare una nuova istanza e senza esclusione
  dalle app recenti;
- nessun vincolo.

Prerequisiti:

- avvio automatico MIUI e batteria `Nessuna restrizione` per MacroDroid;
- sospensione dell'app inutilizzata disabilitata;
- apertura di finestre dal background, finestre pop-up e visualizzazione sulla
  schermata di blocco consentite;
- MacroDroid abilitato, macro attiva e licenza Premium attiva sul dispositivo
  di test.

Test:

- prova manuale conclusa con apertura automatica di Tasker, processo presente
  e `MonitorService` attivo;
- riavvio reale concluso senza apertura manuale delle app;
- dopo il primo sblocco MacroDroid e Tasker risultavano in esecuzione e
  `MonitorService` era attivo;
- nessun dato o file Significant Places modificato dal watchdog.

Esito: **mantenuto; workaround di boot validato sul dispositivo di test**.

## Modello Per I Batch Successivi

```text
### BNNN - Titolo - Data

Ambito:
- ...

Modifiche:
- ...

Riferimenti Tasker:
- ...

Checkpoint:
- backup privato disponibile: si/no

Test:
- ...

Esito: mantenuto / in osservazione / ripristinato
```
