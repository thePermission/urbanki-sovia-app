import folium as fl
import streamlit as st
from folium import FeatureGroup
from streamlit_folium import st_folium

from sovia.application.ergebnisse_verwalten_service import get_ergebnisse
from sovia.infra.DatabaseConnector import gebiete_laden, gebiete_auflisten, ausblenden_speichern, \
    ausblenden_zurücksetzen

if st.session_state.get('polys') is None:
    st.session_state['polys'] = []
if st.session_state.get('center') is None:
    st.session_state.center = [51.59397531704631, 7.136821746826173]
if st.session_state.get('zoom') is None:
    st.session_state.zoom = 14

st.title("Ergebnisse verwalten")
st.markdown("""
Die Ergebnisse aus den durchgeführten Untersuchungen können hier verwaltet werden. Zuerst muss dafür ein Gebiet ausgewählt
werden, anschließend werden sie geladen über den Button "laden". Die Klassifizierungsgrenze gibt an, ab welcher Klassifizierung
die Ergebnisse angezeigt werden sollen. Eine Klassifizierung von 0 bedeutet, dass es sich sehr wahscheinlich nicht um ein neues
Dach handelt, während eine Klassifizierung von 1 bedeutet, dass es sich um ein neues Dach handelt. Die Ergebnisse erscheinen
unterhalt der Map und können dort ausgeblendet werden, sollte sich die KI geirrt haben. Dazu wird der Haken rechts in der Tabelle
gesetzt in der Spalte "ausblenden" und anschließend der "speicher" Button gedrückt. Möchte man (beispielsweise wenn neue WMS-Server
konfiguriert wurden) diese ausgebelendeten Hausumringe wieder einblenden muss man den Button "zurücksetzen" drücken.
""")

def _filtern():
    if st.session_state.get("findings") is not None:
        loaded_findings = st.session_state.findings
        st.session_state.findings_filtered = loaded_findings[
            loaded_findings["klassifizierung"] > st.session_state.klassifizierungsgrenze].sort_values(by=["klassifizierung"])


left_column, right_column = st.columns([0.8, 0.2])
with right_column:
    st.selectbox("Gebiete", gebiete_auflisten(), key="gebiet_to_discover")
    st.slider("Klassifizierungsgrenze", min_value=0.0, max_value=1.0, step=0.01, value=0.5,
              key="klassifizierungsgrenze", on_change=_filtern)

    def _click_laden():
        with st.spinner(text="laden...", show_time=True):
            try:
                st.session_state["findings"] = get_ergebnisse(st.session_state.gebiet_to_discover)
                _filtern()
                st.success("Laden abgeschlossen!")
            except Exception as e:
                st.error(f"Laden fehlgeschlagen! {e}")

    st.button("laden", on_click=_click_laden)
    st.text("Ausblenden für dieses Gebiet zurücksetzen:")
    def _reset_ausblenden():
        ausblenden_zurücksetzen(st.session_state.gebiet_to_discover)
        st.session_state["findings"] = get_ergebnisse(st.session_state.gebiet_to_discover)
        _filtern()
    st.button("zurücksetzen", on_click=_reset_ausblenden)

m = fl.Map(location=st.session_state.center, zoom_start=st.session_state.zoom)
with left_column:
    fg = FeatureGroup()
    for gebiet in gebiete_laden():
        for polygon in gebiet[2]:
            opacity = 0.5 if gebiet[0] == st.session_state.gebiet_to_discover else 0.1
            poly = fl.Polygon(
                locations=polygon,
                color=gebiet[1],
                fill=True,
                fill_color=gebiet[1],
                fill_opacity=opacity,
                tooltip=gebiet[0],
            )
            fg.add_child(poly)
    findings = st.session_state.get("findings_filtered")
    if findings is not None and len(findings) > 0:
        for finding in list(findings["frontend_coordinates"]):
            poly = fl.Polygon(
                locations=finding,
                color="red",
                fill=True,
                fill_color="red",
                fill_opacity=1,
            )
            fg.add_child(poly)
    map_state = st_folium(m, use_container_width=True,
                          key="folium_map", feature_group_to_add=fg)

if findings is not None:
    if len(findings) == 0:
        st.text("Es wurden keine Dächer in diesem Gebiet gefunden.")
    else:
        def _speichern():
            with st.spinner("speichern"):
                changed = st.session_state.get("findings_filtered").iloc[list(st.session_state.edited["edited_rows"].keys())]
                changed["ausblenden"] = True
                ausblenden_speichern(changed[["OI", "ausblenden"]])
                st.session_state["findings"] = get_ergebnisse(st.session_state.gebiet_to_discover)
                _filtern()
                st.success("Speichern abgeschlossen!")

        st.button("speichern", on_click=_speichern)
        findings = st.session_state.get("findings_filtered")
        st.data_editor(
            findings[["OI", "link_1", "link_2", "klassifizierung", "maps", "ausblenden"]],
            column_config={
                "OI": st.column_config.TextColumn("ID"),
                "link_1": st.column_config.ImageColumn("Erster"),
                "link_2": st.column_config.ImageColumn("Zweiter"),
                "maps": st.column_config.LinkColumn("Google Maps", display_text="Link zu Maps"),
                "ausblenden": st.column_config.CheckboxColumn("Ausblenden"),
            },
            hide_index=True,
            height=800,
            row_height=200,
            key="edited",
        )
