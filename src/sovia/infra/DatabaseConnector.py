from enum import Enum
from pathlib import Path

import numpy as np
from duckdb import InvalidInputException
from duckdb import connect
from pandas import DataFrame
from shapely import wkt
from shapely.geometry import shape

from sovia.utils.file_handling import get_path_to_data


def create_connection():
    con = connect(f"{get_path_to_data(__file__)}/database.duckdb")
    try:
        con.sql("LOAD spatial")
    except InvalidInputException:
        pass
    return con


def init():
    with create_connection() as con:
        con.sql(
            "CREATE TABLE IF NOT EXISTS bereiche (name varchar, number int1, color varchar, geom GEOMETRY, PRIMARY KEY (name, number))")
        con.sql("CREATE TABLE IF NOT EXISTS hausumringe (name varchar)")
        con.sql("CREATE TABLE IF NOT EXISTS klassifizierung (oi varchar, klassifizierung int)")
        con.sql("CREATE TABLE IF NOT EXISTS image_url (reihenfolge varchar, link varchar, PRIMARY KEY(reihenfolge))")

class Reihenfolge(Enum):
    ERSTER = "erster"
    ZWEITER = "zweiter"

def links_laden() -> DataFrame:
    with create_connection() as con:
        return con.sql("SELECT DISTINCT reihenfolge, link FROM image_url").fetchdf().set_index("reihenfolge")

def link_speichern(reihenfolge: Reihenfolge, link: str):
    sql = f"""
    INSERT OR REPLACE INTO image_url (reihenfolge, link) 
    VALUES ('{reihenfolge.value}', '{link}');
    """
    with create_connection() as con:
        con.sql(sql)



def hausumringe_speichern(filepath: Path):
    with create_connection() as con:
        con.sql(f"CREATE OR REPLACE TABLE hausumringe as SELECT * FROM ST_Read('{filepath}')")


def hausumringe_laden() -> DataFrame:
    sql = """
          SELECT *
          FROM hausumringe LIMIT 100 \
          """
    with create_connection() as con:
        return con.sql(sql).fetchdf()


def gebiet_speichern(name: str, polygons: dict):
    with create_connection() as con:
        con.sql(f"DELETE FROM bereiche WHERE name = '{name}'")
        color = np.random.randint(16, 256, size=3)
        color = [str(hex(i))[2:] for i in color]
        color = '#' + ''.join(color).upper()
        for i, polygon in enumerate(polygons):
            for coordinate in polygon['geometry']['coordinates'][0]:
                tmp = coordinate[0]
                coordinate[0] = coordinate[1]
                coordinate[1] = tmp
            # GeoJSON-Polygon in einem Feature verarbeiten
            geometry = shape(polygon["geometry"])  # Shapely-Objekt erzeugen
            wkt_geo = geometry.wkt  # WKT aus der Geometrie erzeugen

            # SQL-Statement zum Insert
            sql = f"""
            INSERT OR REPLACE INTO bereiche (name, number, color, geom) 
            VALUES ('{name}', {i}, '{color}', ST_Transform(ST_GeomFromText('{wkt_geo}'), 'EPSG:4326', 'EPSG:25832'));
            """
            con.sql(sql)


def gebiet_loeschen(name: str):
    with create_connection() as con:
        con.sql(f"DELETE FROM bereiche WHERE name = '{name}'")


def _to_geo(polygon_list):
    coords = []
    for wkt_geom in polygon_list:
        shapely_geom = wkt.loads(wkt_geom)
        coords.append([(x, y) for x, y in shapely_geom.exterior.coords])
    return coords


def gebiete_laden() -> list[tuple[str, str, list[list[tuple[float, float]]]]]:
    sql = """
          SELECT name, color, list(ST_asText(ST_Transform(b.geom, 'EPSG:25832', 'EPSG:4326'))) as geom
          FROM bereiche as b
          GROUP BY name, color
          """
    with create_connection() as con:
        df: DataFrame = con.sql(sql).fetchdf()

        df["geom"] = df["geom"].apply(lambda x: _to_geo(x))
        return list(zip(df["name"], df["color"], df["geom"]))


def gebiet_laden(name: str) -> tuple[str, str, list[list[tuple[float, float]]]]:
    sql = f"""
          SELECT name, color, list(ST_asText(ST_Transform(b.geom, 'EPSG:25832', 'EPSG:4326'))) as geom
          FROM bereiche as b
          WHERE name = '{name}'
          GROUP BY name, color
          """
    with create_connection() as con:
        df: DataFrame = con.sql(sql).fetchdf()
        df["geom"] = df["geom"].apply(lambda x: _to_geo(x))
        return df


def gebiete_auflisten() -> list[str]:
    with create_connection() as con:
        df = con.sql("SELECT DISTINCT name FROM bereiche ORDER BY name").fetchdf()
        return df["name"].to_list()


def get_hausumringe_in(name: str):
    AUFLOESUNG = 800 * 800
    with create_connection() as con:
        sql = f"""
        WITH ausgewaehlt as (
            SELECT * FROM bereiche
            WHERE name='{name}'
        ),
        links as (
            SELECT link_1, link_2 FROM (SELECT link as link_1 FROM image_url WHERE reihenfolge='erster') as erster
            LEFT JOIN (SELECT link as link_2 FROM image_url WHERE reihenfolge='zweiter') as zweiter ON 1=1
        )
        SELECT DISTINCT 
            h.oi,
            ST_asText(ST_Transform(h.geom, 'EPSG:25832', 'EPSG:4326')) as geom,
            ST_asText(ST_Transform(ST_Centroid(h.geom), 'EPSG:25832', 'EPSG:4326')) as center,
            ST_XMin(ST_Envelope(h.geom)) as x1,
            ST_YMIN(ST_Envelope(h.geom)) as y1,
            ST_XMAX(ST_Envelope(h.geom)) as x2,
            ST_YMAX(ST_Envelope(h.geom)) as y2,
            round(sqrt({AUFLOESUNG}/((x2-x1)/(y2-y1))), 0)::INTEGER as height,
            round({AUFLOESUNG}/sqrt({AUFLOESUNG}/((x2-x1)/(y2-y1))), 0)::INTEGER as width,
            l.link_1,
            l.link_2
        FROM ausgewaehlt as a, hausumringe as h 
        LEFT JOIN links as l ON 1=1
        WHERE ST_Contains(a.geom, h.geom)
        """
        return con.sql(sql).fetchdf()


def hausumringe_in(polygons) -> list[list[tuple[float, float]]]:
    name = "test"
    with create_connection() as con:
        con.sql(f"DELETE FROM bereiche WHERE name = '{name}'")
        for i, polygon in enumerate(polygons):
            for coordinate in polygon['geometry']['coordinates'][0]:
                tmp = coordinate[0]
                coordinate[0] = coordinate[1]
                coordinate[1] = tmp
            # GeoJSON-Polygon in einem Feature verarbeiten
            geometry = shape(polygon["geometry"])  # Shapely-Objekt erzeugen
            wkt_geo = geometry.wkt  # WKT aus der Geometrie erzeugen

            # SQL-Statement zum Insert
            sql = f"""
            INSERT OR REPLACE INTO bereiche (name, number, geom) 
            VALUES ('{name}', {i}, ST_Transform(ST_GeomFromText('{wkt_geo}'), 'EPSG:4326', 'EPSG:25832'));
            """
            con.sql(sql)
    sql = """
          SELECT h.oi, ST_asText(ST_Transform(h.geom, 'EPSG:25832', 'EPSG:4326')) as geom
          FROM bereiche as b,
               hausumringe as h
          WHERE ST_Contains(b.geom, h.geom)
          """
    with create_connection() as con:
        df = con.sql(sql).fetchdf()
        coords = []
        for wkt_geom in df["geom"]:
            shapely_geom = wkt.loads(wkt_geom)
            coords.append([(x, y) for x, y in shapely_geom.exterior.coords])
        return coords


def test(sql: str):
    with create_connection() as con:
        con.sql(sql).show()
