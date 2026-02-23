import math
import threading
from string import Template
import torch

from sovia.infra.DatabaseConnector import get_hausumringe_in, klassifizierung_speichern
from sovia.infra.ImageLoader import ImageLoader
import pandas as pd
import numpy as np
from sovia.infra.SiameseNeuralNetwork import SiameseNetwork
from torch import nn

img_loader = ImageLoader()


def scan_area(area_name: str, model, rescan: bool):
    hausumringe = get_hausumringe_in(area_name, rescan)
    if len(hausumringe) == 0:
        return []
    _wms_links(hausumringe)
    hausumringe = _process_in_threads(hausumringe, model)
    klassifizierung_speichern(hausumringe)

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

def _process_in_threads(df: pd.DataFrame, model) -> pd.DataFrame:
    anzahl_bilder_im_ram = 1000
    anzahl_der_threads = 8
    chunks = np.array_split(df, math.ceil(len(df) / anzahl_bilder_im_ram))
    verarbeitete_chunks = []
    for chunk in chunks:
        chunks_for_thread: pd.DataFrame = np.array_split(chunk, anzahl_der_threads)
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
                                       ["OI", "klasse"]])
    return pd.concat(verarbeitete_chunks, ignore_index=True)


def _klassifiziere(df: pd.DataFrame, model):
    df["klasse"] = df.apply(lambda x: _klassifiziere_row(model, x), axis=1)


def _klassifiziere_row(model: SiameseNetwork, row):
    try:
        with torch.no_grad():
            classification = model.forward_with_probability(row["imgs"][0].unsqueeze(0), row["imgs"][1].unsqueeze(0))
            return classification
    except Exception as e:
        print(e)
        return float(0)

def _lade_bilder(df: pd.DataFrame):
    df["imgs"] = df.apply(lambda x: img_loader.load(x["OI"], x["link_1"], x["link_2"], x["geom"]),
                          axis=1)