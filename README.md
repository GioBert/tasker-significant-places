# tasker-significant-places

Automazione Tasker orientata all'individuazione dei luoghi significativi visitati dal dispositivo, con configurazione esterna e log minimale basato sulle soste.

## Obiettivo

Questo progetto nasce come alternativa al paradigma basato su `LEAVE / ARRIVE / MOVING`.

L'obiettivo principale e' identificare i luoghi visitati e registrare solo le soste significative. Gli spostamenti tra due luoghi non vengono loggati come eventi espliciti: sono impliciti nella successione cronologica dei luoghi registrati.

## Formato CSV previsto

```text
TIMESTAMP;LAT;LON;PLACE_ID;NAME
2026-03-14 00.00;0.000000;0.000000;1;Luogo_1
```

## Principi di base

- il primo luogo della giornata viene scritto subito come record iniziale
- un nuovo luogo viene confermato solo dopo una permanenza minima configurabile
- il progetto usa un file di configurazione esterno
- la documentazione e' in italiano
- XML, identificatori tecnici e codice restano in inglese

## Struttura iniziale

- `config/tasker_globals.csv`
- `docs/visione_progetto.md`
- `docs/privacy_e_anonimizzazione.md`
- `docs/setup_telefono_android.md`
- `docs/convenzioni_linguistiche.md`
- `docs/precisione_dei_dati.md`
- `docs/strumenti_consigliati.md`

## Stato attuale

La repo contiene la base documentale e di configurazione del nuovo progetto. L'automazione Tasker vera e propria verra' sviluppata in una fase successiva, dopo la definizione tecnica del nuovo paradigma.
