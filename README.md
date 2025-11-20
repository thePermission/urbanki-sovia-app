# SoVIA - App
In diesem Projekt wurde ein Demonstrator entwickelt, der eine bereits trainierte KI verwenden kann, um Dächer aus dem 
RVR-Gebiet zu klassifizieren. Die App unterscheidet zwischen Dächern, die neugemacht wurden, bei denen aber noch kein 
Solar installiert wurde und allen anderen Dächern. Zur Klassifizierung werden immer zwei Bilder von WMS-Servern verwendet.

## Installieren der Anwendung

### Nötige Vorbereitungen
Zu Verwendung dieses Projekts ist die Installation von UV nötig. UV kann über folgende URL heruntergeladen werden:
https://docs.astral.sh/uv/getting-started/installation/

### Installation der benötigten Pakete
```
uv sync
```

## Starten der Anwendung
```
uv run streamlit run .\src\sovia\main.py
```

## Konfiguration
über die Datei `config.py` können die Jahre und WMS-Adressen, sowie die Klassifikationsgrenze konfiguriert werden.