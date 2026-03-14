# Visione Del Progetto

## Sintesi

`tasker-significant-places` e' un progetto centrato sulla registrazione dei luoghi significativi visitati nel corso della giornata.

Il progetto non cerca di classificare in modo esplicito gli stati di movimento. Al contrario, ignora il movimento come concetto autonomo e concentra la logica sull'individuazione delle soste stabili e sufficientemente lunghe da rappresentare un luogo significativo.

## Paradigma

Il paradigma previsto e':

- campionare periodicamente la posizione GPS
- riconoscere se il dispositivo e' ancora nel luogo stabile corrente
- ignorare i campioni che rappresentano semplice movimento o permanenze troppo brevi
- creare un nuovo luogo solo quando una nuova posizione si dimostra stabile per un tempo minimo

## Conseguenze sul modello dati

Il CSV non descrive piu' eventi di partenza e arrivo. Descrive invece una sequenza di luoghi visitati:

```text
TIMESTAMP;LAT;LON;PLACE_ID;NAME
2026-03-14 00.00;0.000000;0.000000;1;Luogo_1
2026-03-14 10.12;0.000900;0.000900;2;Luogo_2
```

Lo spostamento tra due righe e' implicito e potra' essere ricostruito successivamente da strumenti di elaborazione.

## Decisioni iniziali del prototipo attuale

- distanza massima per considerare "stesso luogo": `100 metri`
- tempo minimo di sosta per confermare un nuovo luogo: `1 minuto`
- il primo luogo della giornata viene scritto subito come record iniziale
- i nomi automatici dei luoghi seguono il formato `Luogo_1`, `Luogo_2`, ...
- il comportamento dell'automazione deve essere il piu' possibile parametrico tramite file di configurazione esterno

## Nota importante

Nel prototipo corrente il file `config/tasker_globals.csv` e' allineato ai valori usati, ma non viene ancora letto direttamente dall'automazione. I valori attivi vengono impostati da `LOAD_CONFIG_DEFAULTS` dentro l'XML.

## Roadmap iniziale

1. Consolidare il prototipo XML attuale.
2. Fare test reali in movimento.
3. Introdurre la lettura reale della configurazione esterna.
4. Introdurre successivamente riconoscimento di luoghi noti e report giornalieri.