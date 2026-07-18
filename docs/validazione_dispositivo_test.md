# Validazione Sul Dispositivo Di Test

## Scopo

Questa pagina riassume i risultati riproducibili ottenuti sul dispositivo fisico
principale del progetto. Non contiene coordinate, percorsi, seriali ADB o altri
identificativi personali.

Data della validazione: **18 luglio 2026**.

## Ambiente validato

| Voce | Valore |
| --- | --- |
| Dispositivo | Xiaomi Redmi 10C NFC |
| Model code | `220333QNY` |
| Codename rilevato | `rain` |
| Variante | EEA / Europa (`rain_eea`) |
| Android | 13, API 33 |
| MIUI | `V14.0.10.0.TGEEUXM` |
| Patch di sicurezza | 1 febbraio 2025 |
| Tasker | `6.6.20` |

Alla data della verifica, l'updater Xiaomi non proponeva firmware EEA piu'
recenti. Nessun firmware e' stato scaricato o installato durante i test.

## Configurazione di affidabilita' Tasker

Sul dispositivo sono risultate necessarie o utili queste impostazioni:

- avvio automatico MIUI abilitato per Tasker
- risparmio batteria MIUI impostato su `Nessuna restrizione`
- Tasker presente nella whitelist energetica Android
- posizione precisa e posizione in background concesse
- notifiche, wake lock, allarmi esatti e riconoscimento attivita' consentiti
- `Usa Allarmi Affidabili` impostato su `Sempre`
- notifica del monitor abilitata
- `Avvia Monitor all'Apertura dell'App` abilitato
- permesso MIUI `Mostra sulla schermata di blocco` impostato su
  `Consenti sempre`

Nel test conclusivo di riavvio, Tasker non era attivo prima del primo sblocco,
quando la configurazione protetta non era ancora disponibile. Senza aprire
l'app, processo e `MonitorService` sono partiti entro 30 secondi dal primo
sblocco e gli allarmi periodici sono stati ricreati. Il primo sblocco dopo
l'accensione e' quindi una precondizione operativa su questo telefono.

Dopo un `force-stop`, invece, Android non permette a un'app di ripartire da
sola. Se viene eseguito un arresto forzato, aprire Tasker. L'opzione
`Avvia Monitor all'Apertura dell'App` e' stata abilitata per rendere questa
procedura piu' affidabile; dopo la modifica non e' stato ripetuto un secondo
test di `force-stop`.

## Sensori di movimento

I sensori Android `significant_motion`, `motion_detect` e `stationary_detect`
sono presenti e utilizzabili da Tasker.

Risultati aggregati:

- `significant_motion`: nessun falso evento in due minuti di quiete; durante
  una camminata con schermo spento ha generato eventi in raffiche e il listener
  e' stato riarmato correttamente
- `motion_detect`: nessun evento in un minuto di quiete; durante il movimento
  ha prodotto eventi con intervallo mediano di circa 5 secondi, anche con
  schermo spento
- `stationary_detect`: durante la quiete ha prodotto eventi ripetuti circa ogni
  5 secondi; durante il movimento continuo non ha prodotto eventi nella
  finestra finale osservata; funziona anche con schermo spento

`stationary_detect` non va collegato direttamente a un fix GPS per ogni evento:
richiede debounce o cooldown. `significant_motion` e' il candidato migliore per
risvegliare una strategia ibrida, ma le raffiche devono essere accorpate.

## GPS assistito

I dati di assistenza GNSS non sono stati cancellati, quindi le misure descrivono
fix assistiti e non un cold start puro.

Su una serie controllata da fermo:

- 8 fix riusciti su 8
- TTFF mediano: circa 2,35 secondi
- TTFF p95: circa 2,78 secondi
- accuratezza dichiarata mediana: circa 31,5 metri
- accuratezza dichiarata p95: circa 71,6 metri
- dispersione radiale media osservata: circa 1,5 metri
- dispersione radiale massima osservata: circa 3,5 metri
- satelliti riportati: mediana 15

Dopo una pausa isolata di 180 secondi, la riacquisizione ha avuto un TTFF
interno di circa 3,63 secondi. L'accuratezza dichiarata dal provider e'
risultata conservativa e variabile, mentre la stabilita' geometrica da fermo e'
stata buona.

## Schermo spento e Doze

I profili sensore e il monitor Tasker hanno funzionato con schermo spento.
Su questa build MIUI, tuttavia, Doze profondo non e' stato forzabile con i
comandi ADB standard neppure con USB fisicamente scollegata. Il firmware e'
rimasto negli stati `INACTIVE/ACTIVE`.

Questo risultato non dimostra un malfunzionamento sotto Doze reale: indica che
il test forzato non e' riproducibile su questa build. I risultati relativi allo
schermo spento e all'esecuzione in background restano validi.

## Strategia consigliata

Il campionamento periodico ogni 2 minuti resta la baseline operativa validata.
Una futura strategia ibrida puo' usare `significant_motion` per aumentare il
campionamento dopo un movimento e ridurlo durante una quiete confermata.

Prima di sostituire la baseline servono ancora:

- una politica esplicita di debounce e cooldown
- fallback periodico quando gli eventi sensore non arrivano
- confronto energetico controllato di almeno 8 ore per strategia
- verifica su spostamenti e soste reali senza salvare dati privati nel repository

Il monitor energetico di 8 ore e' stato predisposto ma rinviato; non sono quindi
ancora disponibili conclusioni quantitative sul risparmio della strategia
ibrida.

## Limiti e privacy

- nessun cold start GNSS puro eseguito
- Doze profondo forzato non raggiunto su questa build MIUI
- test energetico prolungato non ancora eseguito
- risultati GPS pubblicati soltanto come tempi, errori e dispersioni aggregate
- dati grezzi e coordinate reali esclusi dal repository

## Run Log E Test Con Posizione Fittizia

Il Run Log nativo di Tasker e' risultato gia' attivo. Il 18 luglio 2026 ne e'
stata esportata una copia privata per associare gli errori agli ID delle azioni,
senza pubblicare valori delle variabili o coordinate.

Un test controllato con Mocaction ha usato una configurazione temporanea con:

- output reindirizzato sotto una directory `TestData` sul telefono;
- `MIN_STOP_MINUTES=1`;
- checkpoint nativo immediatamente precedente al test;
- manifest SHA-256 dei file operativi prima e dopo il test.

Android ha ricevuto la posizione fittizia sui provider `gps` e `fused`, con
accuratezza simulata compatibile con il limite del progetto. Tasker, tuttavia,
non ha ottenuto un fix utilizzabile tramite l'azione `5.19`, identificata
nell'XML come `Ottieni Posizione v2` (`code 366`) con timeout di 20 secondi.
Il Run Log ha registrato 21 `ExitErr` consecutivi durante la sola finestra del
test, tutti associati all'azione `5.19`.

Dopo l'arresto della posizione fittizia e il ripristino del checkpoint:

- Mocaction e' stata rimossa come app per la posizione fittizia;
- monitor e allarme periodico sono rimasti attivi;
- i cicli reali sono tornati a concludersi con `ExitOK`;
- nessuno dei 126 file preesistenti e' risultato modificato o mancante;
- l'unico file aggiunto era il CSV isolato di test con la sola intestazione.

Il timeout dimostra che Mocaction non e' un metodo valido, su questo telefono,
per collaudare il ramo successivo a `Ottieni Posizione v2`. Non dimostra un
errore del commit transazionale B004, perche' il task non ha raggiunto quel
ramo. Nei log Android sono comparsi anche riavvii del renderer WebView durante
la sequenza di timeout; il Run Log identifica pero' `Ottieni Posizione v2` come
azione primaria in errore, mentre le esecuzioni reali successive terminano
correttamente.

Per un futuro test sintetico del ramo B004 occorre usare un metodo che produca
variabili di posizione accettate da Tasker oppure una configurazione temporanea
che inietti dati sintetici dopo l'azione di acquisizione. La configurazione
reale non deve essere modificata per adattarla a Mocaction.

### Iniezione Dopo L'Acquisizione

Il ramo B004 e' stato successivamente collaudato con una seconda configurazione
temporanea. La sola `Ottieni Posizione v2` del task principale e' stata
sostituita da tre `Imposta Variabile` contenenti latitudine, longitudine e
accuratezza deliberatamente sintetiche. Tutta la logica successiva e' rimasta
identica alla configurazione B004.

Risultato:

- una sola riga sintetica aggiunta al CSV isolato;
- contatore globale incrementato di una unita';
- ID della riga uguale al contatore confermato;
- stato globale della posizione uguale ai valori scritti nella riga;
- timestamp e nome presenti;
- conteggio e tempi del candidato azzerati dopo il commit;
- nessuna riga duplicata nei cicli successivi;
- zero file operativi preesistenti modificati o mancanti dopo il ripristino.

Questo test valida sul runtime Tasker la sequenza B004 `staging locale > Scrivi
File > commit globale`. Non valida l'acquisizione GPS, che resta coperta dai
test reali separati.

## Backup E Ripristino Della Configurazione

Il 18 luglio 2026 e' stato eseguito un test completo e controllato della
procedura di disaster recovery della configurazione Tasker:

- backup manuale XML copiato fuori dal telefono e validato prima della
  pulizia;
- hash SHA-256 verificato uguale tra telefono e copia locale;
- configurazione utente rimossa con `Dati > Pulire`;
- variabili globali ed archivio `_SignificantPlaces` rimasti intatti;
- ripristino eseguito dal backup manuale;
- profilo nominato, abilitato e collegato al task principale;
- tre task e 126 azioni ripristinati;
- `MonitorService` e allarme periodico esatto ricreati;
- due cicli automatici consecutivi conclusi con `ExitOK`;
- configurazione esterna verificata invariata tramite hash.

### Recovery B005 Da CSV Esistente

Il 18 luglio 2026 e' stata validata anche la recovery dello stato dal CSV
giornaliero. Dopo `LOAD_CONFIG_DEFAULTS`, l'avvio manuale di INIT ha:

- letto un CSV valido con tre record senza modificarlo;
- impostato `%RECOVERY_STATUS` a `recovered`;
- ricostruito `%PLACE_COUNTER` al massimo ID esistente;
- lasciato invariati hash, dimensione e numero di righe;
- terminato il ramo di recovery prima del fix GPS;
- mantenuto `MonitorService`, nove allarmi Tasker e cicli periodici `ExitOK`.

I tentativi intermedi hanno verificato anche il comportamento fail-closed:
gli stop diagnostici non hanno modificato il CSV. Un primo candidato non
ancora fail-closed aveva aggiunto una riga; la copia preventiva e' stata
ripristinata byte per byte e la versione e' stata archiviata come fallita.

La procedura operativa completa e' in
[Backup e ripristino di Tasker](backup_ripristino_tasker.md).
