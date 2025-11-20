import folium as fl
import streamlit as st
from folium import FeatureGroup
from streamlit_folium import st_folium

from sovia.domain.actions import finde_neue_daecher
from sovia.infra.DatabaseConnector import gebiete_laden, gebiete_auflisten
from sovia.infra.SiameseNeuralNetwork import load_model

if st.session_state.get('polys') is None:
    st.session_state['polys'] = []
if st.session_state.get('center') is None:
    st.session_state.center = [51.59397531704631, 7.136821746826173]
if st.session_state.get('zoom') is None:
    st.session_state.zoom = 14


@st.cache_resource
def load_model_from_disk():
    return load_model()


st.title("Gebiet untersuchen")

left_column, right_column = st.columns([0.8, 0.2])
with right_column:
    st.selectbox("Gebiete", gebiete_auflisten(), key="gebiet_to_discover")


    def _click_untersuchen():
        with st.spinner(text="untersuche...", show_time=True):
            findings = finde_neue_daecher(st.session_state.gebiet_to_discover, load_model_from_disk())
            st.session_state["findings"] = findings


    st.button("untersuchen", on_click=_click_untersuchen)

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
    findings = st.session_state.get("findings")
    if findings is not None:
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

findings = st.session_state.get("findings")
if findings is not None:
    st.data_editor(
        findings[["OI", "link_1", "link_2", "maps"]],
        column_config={
            "OI": st.column_config.TextColumn("ID"),
            "link_1": st.column_config.ImageColumn("Vorher"),
            "link_2": st.column_config.ImageColumn("Nachher"),
            "maps": st.column_config.LinkColumn("Google Maps"),
        },
        hide_index=True,
        height=800,
        row_height=200,
    )
