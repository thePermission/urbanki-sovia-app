import os
import zipfile
from pathlib import Path

def find_shape_file(files: list[str]) -> Path | None:
    for file in files:
        if file.endswith(".shp"):
            return tmp_filepath / file
    return None


def zwischenspeichern(file) -> list[str]:
    with zipfile.ZipFile(file) as zip_file:
        zip_file.extractall(tmp_filepath)
        return zip_file.namelist()


def temp_dateien_loeschen(names: list[str]):
    for name in names:
        os.remove(tmp_filepath / name)


def get_path_to_data(file: str):
    current_file_path = Path(file)
    for parent in current_file_path.parents:
        if (parent / 'data').is_dir():
            return parent / 'data'

tmp_filepath = get_path_to_data(__file__) / "tmp"