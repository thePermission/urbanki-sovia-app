from string import Template

from sovia.infra.DatabaseConnector import get_ergbenisse_von
from shapely import wkt
import pandas as pd
import shapely

from sovia.infra.ImageLoader import ImageLoader

GOOGLEMAPS = "https://www.google.com/maps/search/?api=1&query=$x,$y&hl=de"
img_loader = ImageLoader()

def get_ergebnisse(name: str):
    df = get_ergbenisse_von(name)
    _prepare_dataset(df)
    return df

def _frontend_geometrien(row):
    shapely_geom = wkt.loads(row)
    return [(x, y) for x, y in shapely_geom.exterior.coords]


def _prepare_dataset(df: pd.DataFrame):
    _wms_links(df)
    _google_maps_links(df)
    df["frontend_coordinates"] = df["geom"].apply(lambda x: _frontend_geometrien(x))


def _wms_links(df: pd.DataFrame):
    def _template(name: str, row):
        params = {
            "width": row["width"],
            "height": row["height"],
            "x1": row["x1"],
            "x2": row["x2"],
            "y1": row["y1"],
            "y2": row["y2"],
        }
        return Template(row[name]).substitute(params)

    df["link_1"] = df.apply(lambda x: _template("link_1", x), axis=1)
    df["link_2"] = df.apply(lambda x: _template("link_2", x), axis=1)


def _google_maps_links(df: pd.DataFrame):
    def _template(base: str, row):
        center: shapely.Point = wkt.loads(row["center"])
        params = {
            "x": center.x,
            "y": center.y,
        }
        return Template(base).substitute(params)

    df["maps"] = df.apply(lambda x: _template(GOOGLEMAPS, x), axis=1)
