# Privacy E Anonimizzazione

## Regole di base

Nella repo non devono comparire dati personali o dati riconducibili a luoghi reali dell'utente.

## Regole operative

- nessun nome personale reale nei file versionati
- nessuna coordinata reale nei file di esempio
- nessun nome reale di luoghi nei file versionati
- modello commerciale, model code, versione Android e build possono essere
  documentati per rendere riproducibili i test, perche' non identificano il
  singolo esemplare
- nessun seriale ADB, IMEI, Android ID, numero telefonico, MAC, IP, SSID,
  account o altro identificativo univoco del dispositivo o dell'utente
- usare solo placeholder come `USER`, `Luogo_1`, `Luogo_2`
- usare coordinate fittizie, preferibilmente in mezzo al mare
- conservare `config/known_places.csv` solo in locale: il file e' escluso tramite `.gitignore`
- conservare CSV giornalieri e log reali fuori dalla directory del repository

## Esempi ammessi

```text
TIMESTAMP;LAT;LON;PLACE_ID;NAME
2026-03-14 00.00;0.000000;0.000000;1;Luogo_1
2026-03-14 10.12;0.000900;0.000900;2;Luogo_2
```

## Note di progetto

Queste regole si applicano sia alla documentazione sia ai file tecnici versionati nella repo.

Prima di ogni pubblicazione occorre controllare `git status` e verificare che non siano inclusi file di configurazione privata, CSV giornalieri o log operativi.

Se un dato personale viene inserito in un commit, eliminarlo nel commit successivo non e' sufficiente: occorre considerare compromesso il dato e bonificare anche la cronologia Git pubblicata.
