# Backup E Ripristino Di Tasker

## Scopo

Questa procedura protegge la configurazione Tasker prima di modifiche, test o
attivita' di recovery. Il backup deve essere verificato prima di usare
`Dati > Pulire` o di cancellare variabili.

Il backup Tasker e i file esterni del progetto sono due insiemi distinti:

- il backup XML conserva la configurazione Tasker e puo' includere variabili
  globali;
- `_SignificantPlaces` contiene configurazione esterna e CSV operativi e deve
  essere salvata separatamente.

## Metodo Supportato Per Le Modifiche

Le modifiche operative devono essere eseguite nell'editor di Tasker, seguendo
la guida ufficiale e l'Help della singola azione:

- [Task Edit](https://tasker.joaoapps.com/userguide/en/activity_taskedit.html)
- [Action Edit](https://tasker.joaoapps.com/userguide/en/activity_actionedit.html)
- [Data Backup](https://tasker.joaoapps.com/userguide/en/help/ah_data_backup.html)

Gli XML esportati vengono usati per backup, confronto, revisione e
versionamento. Non esiste uno schema XML pubblico che garantisca la sicurezza
della modifica manuale dei nodi interni; l'editing diretto dell'XML non e'
quindi il metodo ordinario per cambiare la configurazione attiva.

ADB e terminale possono essere usati per navigare nell'interfaccia, trasferire
i backup, calcolare hash, leggere log e verificare monitor e allarmi.

## Modifiche A Batch

Le correzioni vengono raggruppate in batch coerenti, evitando sia modifiche
isolate eccessivamente lente sia pacchetti troppo grandi da diagnosticare.

Per ogni batch sono sufficienti questi passaggi:

1. definire l'elenco breve delle modifiche e consultare la documentazione
   ufficiale delle azioni coinvolte;
2. creare un solo backup checkpoint prima del batch;
3. registrare il batch nel
   [Registro delle modifiche Tasker](registro_modifiche_tasker.md);
4. applicare le modifiche nell'interfaccia Tasker;
5. eseguire un controllo rapido di profilo, task, scrittura e Run Log;
6. osservare il funzionamento per un periodo proporzionato al rischio;
7. proseguire con il batch successivo oppure ripristinare il checkpoint.

Non serve ripetere l'intero test di disaster recovery per ogni batch. Il test
completo si ripete soltanto dopo modifiche strutturali, problemi di recovery o
prima di una release considerata stabile.

## Backup Preventivo

1. Aprire Tasker e applicare eventuali modifiche con la spunta nella barra
   superiore.
2. Selezionare `Dati > Backup`.
3. Salvare un file con data e scopo, ad esempio:

   ```text
   Tasker/configs/user/backup-AAAA-MM-GG-pre-modifica.xml
   ```

4. Copiare il file fuori dal telefono in un'area locale privata esclusa da
   Git.
5. Verificare almeno:
   - XML ben formato;
   - presenza del progetto, dei profili e dei task attesi;
   - collegamento tra profilo e task di ingresso;
   - numero atteso delle azioni;
   - hash SHA-256 uguale sul telefono e sulla copia locale.
6. Conservare le versioni precedenti in una sottocartella `archive` senza
   cancellarle.

Un backup con coordinate, luoghi, percorsi, variabili operative o altri dati
reali non deve essere aggiunto al repository.

## Nome Del Profilo E Nome Del Contesto

Tasker distingue il nome del profilo dal nome del suo contesto. Per rinominare
il profilo occorre tenere premuta la barra del titolo del profilo, non la riga
con l'icona dell'orologio. Dopo la modifica bisogna applicare con la spunta e
creare un nuovo backup.

Nel progetto il nome raccomandato e':

```text
SIGNIFICANT_PLACES_PERIODIC_2MIN
```

## Cosa Fa `Dati > Pulire`

`Dati > Pulire` rimuove la configurazione utente attiva, compresi profili,
task, scene e progetti. Non elimina automaticamente:

- preferenze di Tasker;
- variabili globali, che hanno un comando separato nella scheda `VARS`;
- backup XML nella memoria condivisa;
- `_SignificantPlaces` e i suoi CSV;
- `tasker_globals.csv` e `known_places.csv`.

Prima di confermare la pulizia deve gia' esistere una copia locale verificata
del backup.

## Ripristino Manuale

1. Selezionare `Dati > Ripristinare > Backup manuale`.
2. Scegliere il backup XML verificato sotto `Tasker/configs/user`.
3. Confermare il ripristino.
4. Applicare con la spunta, se presente.
5. Non avviare ripetutamente il task principale durante la verifica: Tasker
   puo' rifiutare copie concorrenti.

## Verifica Dopo Il Ripristino

Controllare nell'ordine:

1. nome e stato abilitato del profilo;
2. presenza dei tre task:
   - `LOAD_CONFIG_DEFAULTS`;
   - `INIT_SIGNIFICANT_PLACES`;
   - `LOG_SIGNIFICANT_PLACE_SAMPLE`;
3. collegamento del profilo a `LOG_SIGNIFICANT_PLACE_SAMPLE`;
4. frequenza del contesto periodico;
5. avvio di `MonitorService`;
6. presenza del successivo allarme periodico esatto;
7. almeno due cicli automatici consecutivi conclusi con `ExitOK`;
8. integrita' di `tasker_globals.csv`, `known_places.csv` e dei CSV storici.

La verifica deve evitare di riportare coordinate precise nei terminali,
rapporti o screenshot destinati alla pubblicazione.

## Variabili: Test Separato

La cancellazione delle variabili non fa parte del normale test di ripristino
della configurazione. Serve invece a simulare una perdita completa dello stato
operativo.

Prima di un test di questo tipo:

- creare un backup che includa le variabili;
- inventariare le variabili appartenenti al progetto;
- usare una directory CSV di prova oppure correggere prima la recovery dal CSV;
- evitare `Cancella tutto` se sullo stesso Tasker sono presenti altre
  automazioni;
- verificare che il contatore venga ricostruito dal CSV esistente e non riparta
  da zero.

Nella versione corrente la perdita delle variabili puo' produrre ID duplicati
se il CSV giornaliero esiste gia'. Il test completo delle variabili deve quindi
essere rinviato finche' questa recovery non e' stata resa robusta.

## Recovery Dopo Arresto Forzato O Riavvio

- Dopo un `force-stop`, aprire Tasker. Se monitor e allarmi non vengono
  ricreati, applicare la configurazione e uscire con Back.
- Dopo un riavvio completo, sbloccare il telefono almeno una volta per rendere
  disponibile la configurazione protetta.
- Verificare monitor e allarmi prima di considerare operativa l'automazione.

Sul dispositivo di test queste condizioni e impostazioni sono descritte in
[Validazione sul dispositivo di test](validazione_dispositivo_test.md).
