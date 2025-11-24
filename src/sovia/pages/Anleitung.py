import streamlit as st

st.title("SoVIA")
st.text("Solar Visual Inspection Assistant")
st.markdown("""
## Anleitung für die Verwendung des solar visual inspection assistant
Der Solar Visual Inspection Assistant soll Bauämter unterstützen Dachumbauten zu identifizieren, bei denen noch
Solarmodule auf dem Dach installiert werden müssten, da das im Rahmen einer Erneuerung der Dächer verpflichtend ist.
Um das zu ermöglichen werden Hausumringe benötigt, sowie das zu überprüfende Gebiet.
### Hausumringe hochladen
Zuerst müssen die Hausumringe hochgeladen werden. Bisher wurden die Hausumringe von der Seite 
https://www.opengeodata.nrw.de/produkte/geobasis/lk/akt/hu_shp/ bezogen.
Dort kann eine Zip-Datei heruntergeladen werden, die in SoVIA hochgeladen werden kann, auf der Seite
[Hausumringe hochladen](/hausumringe_upload)
### Gebiete bearbeiten
Im nächsten Schritt müssen die auszuwertenden Gebiete angelegt werden, damit nicht bei jeder Überprüfung sofort alle
Hausumringe in ganz NRW überprüft werden, sondern jedes Amt sich seine Gebiete zusammenstellen kann.
### Gebiet untersuchen
Jetzt kann eins der zuvor angelegten Gebiete ausgewählt werden und alle Dächer überprüft werden, die sich im Inneren des
Gebiets befinden. Nach der Überprüfung werden die, von der KI als auffällig gekennzeichneten Dächer angezeigt. Zu jedem
markierten Dach wird die ID des Hausumringes angezeigt, sowie das vorher und nachher Bild der verschiedenen Jahre und 
ein Link zu Googlemaps, um die Adresse des Hausumrings zu ermitteln
""")
