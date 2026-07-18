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
