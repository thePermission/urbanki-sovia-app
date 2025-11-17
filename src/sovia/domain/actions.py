from string import Template

import shapely
import torch
from pandas import DataFrame
from shapely import wkt
from torch import nn

from sovia.infra.DatabaseConnector import get_hausumringe_in
from sovia.infra.ImageLoader import ImageLoader
from sovia.infra.SiameseNeuralNetwork import load_model

WMS1 = "https://geodaten.metropoleruhr.de/dop/top_2020?language=ger&width=$width&height=$height&bbox=$x1,$y1,$x2,$y2&crs=EPSG:25832&format=image/png&request=GetMap&service=WMS&styles=&transparent=true&version=1.3.0&layers=top_2020"
WMS2 = "https://geodaten.metropoleruhr.de/dop/top_2024?language=ger&width=$width&height=$height&bbox=$x1,$y1,$x2,$y2&crs=EPSG:25832&format=image/png&request=GetMap&service=WMS&styles=&transparent=true&version=1.3.0&layers=top_2024"
GOOGLEMAPS = "https://www.google.com/maps/search/?api=1&query=$x,$y&hl=de"

KLASSIFIZIERUNGSGRENZE = 0.5

img_loader = ImageLoader()


def finde_neue_daecher(name: str):
    hausumringe = get_hausumringe_in(name)
    _prepare_dataset(hausumringe)
    _klassifiziere(hausumringe)
    # return hausumringe[hausumringe["klasse"] > KLASSIFIZIERUNGSGRENZE]
    return hausumringe


def _prepare_dataset(df: DataFrame):
    _wms_links(df)
    _google_maps_links(df)
    df["frontend_coordinates"] = df["geom"].apply(lambda x: _frontend_geometrien(x))


def _wms_links(df: DataFrame):
    def _template(base: str, row):
        params = {
            "width": row["width"],
            "height": row["height"],
            "x1": row["x1"],
            "x2": row["x2"],
            "y1": row["y1"],
            "y2": row["y2"],
        }
        return Template(base).substitute(params)

    df["link_1"] = df.apply(lambda x: _template(WMS1, x), axis=1)
    df["link_2"] = df.apply(lambda x: _template(WMS2, x), axis=1)


def _google_maps_links(df: DataFrame):
    def _template(base: str, row):
        center: shapely.Point = wkt.loads(row["center"])
        params = {
            "x": center.x,
            "y": center.y,
        }
        return Template(base).substitute(params)

    df["maps"] = df.apply(lambda x: _template(GOOGLEMAPS, x), axis=1)


def _frontend_geometrien(row):
    shapely_geom = wkt.loads(row)
    return [(x, y) for x, y in shapely_geom.exterior.coords]


def _klassifiziere(df: DataFrame):
    model = load_model()
    df["klasse"] = df.apply(lambda x: _klassifiziere_row(model, x), axis=1)


def _klassifiziere_row(model, row):
    try:
        img1, img2 = img_loader.load(row["link_1"], row["link_2"], row["geom"])
        with torch.no_grad():
            output1, output2 = model(img1.unsqueeze(0), img2.unsqueeze(0))
            distance = nn.functional.pairwise_distance(output1, output2)
            # Verwende .item() auf dem detached Tensor
            return distance.item()
    except Exception as e:
        print(e)
        return float(99999)
