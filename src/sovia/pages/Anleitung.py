import streamlit as st

st.title("SoVIA")
st.text("Solar Visual Inspection Assistant")
st.markdown("""

## Anleitung für die Verwendung des solar visual inspection assistant
Der Solar Visual Inspection Assistant soll Bauämter unterstützen Dachumbauten zu identifizieren, bei denen noch
Solarmodule auf dem Dach installiert werden müssten, da das im Rahmen einer Erneuerung der Dächer verpflichtend ist.
Um das zu ermöglichen werden Hausumringe benötigt, sowie das zu überprüfende Gebiet.
### Konfiguration
Hier werden Hausumringe hochgeladen und WMS-Server konfiguriert.
### Gebiete bearbeiten
Im nächsten Schritt müssen die auszuwertenden Gebiete angelegt werden, damit nicht bei jeder Überprüfung sofort alle
Hausumringe in ganz NRW überprüft werden, sondern jedes Amt sich seine Gebiete zusammenstellen kann.
### Gebiet untersuchen
Nachdem Gebiete angelegt wurden können diese untersucht werden. Die Ergebnisse werden in der Datenbank gespeichert.
### Ergebnisse verwalten
Die Ergebnisse der Untersuchung können hier betrachtet werden. Dabei wird immer die ID des Hausumrings angezeigt, die 
Bilder der WMS-Server, sowie die Klassifizierung und der Link zu GoogleMaps. Außerdem ist es möglich die Hausumringe 
auszublenden, wenn sie als nicht relevant eingestuft werden
""")
