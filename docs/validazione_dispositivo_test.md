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

Il test conferma la recuperabilita' della configurazione, ma non simula la
perdita delle variabili. Quest'ultimo scenario resta separato perche' la
recovery corrente puo' duplicare gli ID quando il CSV giornaliero esiste gia'.

La procedura operativa completa e' in
[Backup e ripristino di Tasker](backup_ripristino_tasker.md).
