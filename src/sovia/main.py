import streamlit as st

from sovia.infra.DatabaseConnector import init

st.set_page_config(layout="wide", page_title="SoVIA")
init()
frontpage = st.Page("pages/Anleitung.py", title="Anleitung")
konfiguration = st.Page("pages/konfiguration.py", title="Konfiguration")
gebiete_bearbeiten = st.Page("pages/gebiete_bearbeiten.py", title="Gebiete bearbeiten")
bereich_untersuchen = st.Page("pages/bereich_untersuchen.py", title="Gebiet untersuchen")
ergebnisse_verwalten = st.Page("pages/ergebnisse_verwalten.py", title="Ergebnisse verwalten")
pg = st.navigation([frontpage, konfiguration, gebiete_bearbeiten, bereich_untersuchen, ergebnisse_verwalten])
pg.run()
