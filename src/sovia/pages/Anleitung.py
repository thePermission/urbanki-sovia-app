import streamlit as st

st.title("SoVIA")
st.text("Solar Visual Inspection Assistant")
st.markdown("""

## Anleitung für die Verwendung des Solar Visual Inspection Assistant
Der Solar Visual Inspection Assistant unterstützt Bauämter digital dabei, die Einhaltung der Solarpflicht bei 
Dachsanierungen zu überwachen. Die Anwendung identifiziert automatisiert Gebäude, die im Zuge einer Dachneueindeckung 
zur Installation von Photovoltaik-Anlagen verpflichtet sind, diese aber noch nicht umgesetzt haben.
Auf Basis von Hausumringen und dem definierten Prüfgebiet liefert das Tool Daten, um Umbaumaßnahmen gezielt zu 
verifizieren und die Energiewende auf kommunaler Ebene voranzutreiben.
### Konfiguration
Hier werden Hausumringe hochgeladen und WMS-Server konfiguriert.
### Gebiete bearbeiten
Um eine effiziente Auswertung zu gewährleisten, erfolgt die Analyse auf Basis individuell definierter Gebiete. Statt 
das gesamte Landesdatennetz (z. B. ganz NRW) zu durchsuchen, können Ämter ihre spezifischen Zuständigkeitsbereiche 
festlegen. Dies ermöglicht eine zielgerichtete Prüfung und verkürzt die Verarbeitungszeit erheblich.
### Gebiet untersuchen
Nach der Gebietsfestlegung erfolgt die detaillierte Auswertung. Alle generierten Daten werden unmittelbar in der 
Datenbank hinterlegt, sodass sie für spätere Abfragen, Berichte oder Folgemaßnahmen dauerhaft zur Verfügung stehen.
### Ergebnisse verwalten
Werten Sie Ihre Analysen effizient aus: Das Dashboard kombiniert die Hausumring-ID mit hochauflösenden WMS-Bilddaten 
und der entsprechenden Klassifizierung. Nutzen Sie den integrierten Google-Maps-Link für eine ergänzende Verifizierung.

Tipp: Markieren Sie irrelevante Treffer einfach mit „ausblenden“, um sie aus der Ansicht zu entfernen und den Fokus 
auf die wichtigen Fälle zu richten.
""")
