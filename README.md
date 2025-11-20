# SoVIA - App
In diesem Projekt wurde ein Demonstrator entwickelt, der eine bereits trainierte KI verwenden kann, um Dächer aus dem 
RVR-Gebiet zu klassifizieren. Die App unterscheidet zwischen Dächern, die neugemacht wurden, bei denen aber noch kein 
Solar installiert wurde und allen anderen Dächern. Zur Klassifizierung werden immer zwei Bilder von WMS-Servern verwendet.

## Installieren der Anwendung

### Nötige Vorbereitungen
Zur Verwendung des Projekts ist UV erforderlich. Die Installation für UV auf verschiedenen Betriebssystemen ist hier zu finden:

https://docs.astral.sh/uv/getting-started/installation/

Anschließend kann folgender Command ausgeführt werden:
```
uv sync
```
## Starten der Anwendung
```
uv run streamlit run .\src\sovia\main.py
```

## Konfiguration
über die Datei `config.py` können die Jahre und WMS-Adressen, sowie die Klassifikationsgrenze konfiguriert werden.

# Lizenz
[Apache 2.0 Lizenz](LICENSE)