import math
import threading
import time
from string import Template

import numpy as np
import pandas as pd
import shapely
import torch
from pandas import DataFrame
from shapely import wkt

from sovia.config import KLASSIFIZIERUNGSGRENZE
from sovia.infra.DatabaseConnector import get_hausumringe_in
from sovia.infra.ImageLoader import ImageLoader
from torch import nn

from sovia.infra.SiameseNeuralNetwork import load_model

GOOGLEMAPS = "https://www.google.com/maps/search/?api=1&query=$x,$y&hl=de"


img_loader = ImageLoader()

def finde_neue_daecher(name: str, model):
    hausumringe = get_hausumringe_in(name)
    if len(hausumringe) == 0:
        return []
    _prepare_dataset(hausumringe)
    hausumringe = _process_in_threads(hausumringe, model)
    return hausumringe[hausumringe["klasse"] > KLASSIFIZIERUNGSGRENZE]


def _prepare_dataset(df: DataFrame):
    start = time.time()
    _wms_links(df)
    _google_maps_links(df)
    print(f"Links erstellt: {time.time() - start}")
    df["frontend_coordinates"] = df["geom"].apply(lambda x: _frontend_geometrien(x))


def _wms_links(df: DataFrame):
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


def _google_maps_links(df: DataFrame):
    def _template(base: str, row):
        center: shapely.Point = wkt.loads(row["center"])
        params = {
            "x": center.x,
            "y": center.y,
        }
        return Template(base).substitute(params)

    df["maps"] = df.apply(lambda x: _template(GOOGLEMAPS, x), axis=1)


def _process_in_threads(df: DataFrame, model) -> DataFrame:
    anzahl_bilder_im_ram = 1000
    anzahl_der_threads = 8
    chunks = np.array_split(df, math.ceil(len(df) / anzahl_bilder_im_ram))
    verarbeitete_chunks = []
    for chunk in chunks:
        chunks_for_thread: DataFrame = np.array_split(chunk, anzahl_der_threads)
        threads = []
        for chunk_for_thread in chunks_for_thread:
            thread = threading.Thread(target=_lade_bilder, args=(chunk_for_thread,))
            threads.append(thread)
            thread.start()
        for thread in threads:
            thread.join()
        chunks_with_images = pd.concat(chunks_for_thread, ignore_index=True)
        _klassifiziere(chunks_with_images, model)
        verarbeitete_chunks.append(chunks_with_images[
                                       ["OI", "geom", "center", "x1", "y1", "x2", "y2", "height", "width", "link_1",
                                        "link_2", "maps", "frontend_coordinates", "klasse"]])
    return pd.concat(verarbeitete_chunks, ignore_index=True)


def _frontend_geometrien(row):
    shapely_geom = wkt.loads(row)
    return [(x, y) for x, y in shapely_geom.exterior.coords]


def _lade_bilder(df: DataFrame):
    df["imgs"] = df.apply(lambda x: img_loader.load(x["OI"], x["link_1"], x["link_2"], x["geom"]),
                          axis=1)


def _klassifiziere(df: DataFrame, model):
    start = time.time()
    df["klasse"] = df.apply(lambda x: _klassifiziere_row(model, x), axis=1)
    print(f"Klassifiziere: {time.time() - start}")


def _klassifiziere_row(model, row):
    try:
        with torch.no_grad():
            output1, output2 = model(row["imgs"][0].unsqueeze(0), row["imgs"][1].unsqueeze(0))
            distance = nn.functional.pairwise_distance(output1, output2)
            # Verwende .item() auf dem detached Tensor
            return distance.item()
    except Exception as e:
        print(e)
        return float(0)


if __name__ == "__main__":
    start = time.time()
    finde_neue_daecher("test", load_model())
    print(f"Gesamtdauer: {time.time() - start}")
