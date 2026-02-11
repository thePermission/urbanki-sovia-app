from optparse import Option

import streamlit as st

from sovia.infra.DatabaseConnector import hausumringe_speichern, hausumringe_laden, links_laden, Reihenfolge, \
    link_speichern
from sovia.utils.file_handling import zwischenspeichern, find_shape_file, temp_dateien_loeschen


def upload_file():
    file = st.session_state.hausumringe_upload
    if file is not None:
        with st.spinner("Hausumringe werden importiert..."):
            erstellte_dateien = zwischenspeichern(file)
            shape_file_path = find_shape_file(erstellte_dateien)
            hausumringe_speichern(shape_file_path)
            temp_dateien_loeschen(erstellte_dateien)
        st.success("Import erfolgreich")

def link_konfiguration():
    st.markdown("""
    Links müssen mit den Platzhaltern definiert werden:\n
    \\$width, \\$height, \\$x1, \\$y1, \\$x2, \\$y2\n
    Beispiel: https://geodaten.metropoleruhr.de/dop/top_2024?language=ger&width=$width&height=$height&bbox=$x1,$y1,$x2,$y2&crs=EPSG:25832&format=image/png&request=GetMap&service=WMS&styles=&transparent=true&version=1.3.0&layers=top_2024
    """)
    left, right = st.columns(2)
    with left:
        reihenfolge = st.selectbox("Reihenfolge", [Reihenfolge.ERSTER, Reihenfolge.ZWEITER], format_func=lambda x: x.value)
    with right:
        neuer_link = st.text_input("Neuer Link")
    if st.button("speichern"):
        link_speichern(reihenfolge, neuer_link)
    links = links_laden()
    st.text("Aktuelle Links:")
    st.table(links)


def main():
    st.title("Konfiguration")
    st.markdown("""
    ## Hausumringe
    Zuerst müssen die Hausumringe hochgeladen werden. Bisher wurden die Hausumringe von der Seite 
    https://www.opengeodata.nrw.de/produkte/geobasis/ bezogen.
    Dort kann eine Zip-Datei heruntergeladen werden, die hier hochgeladen werden kann.
    """)
    st.file_uploader("Hausumringe hochladen", key="hausumringe_upload", on_change=upload_file, type=["zip"])
    st.markdown("""
    ## WMS-Server
    Dannach müssen die beiden WMS-Server eingerichtet werden, von denen die Bilddaten bezogen werden sollen.
    """)
    link_konfiguration()


main()
