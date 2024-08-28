import pathlib

import datalad.api as da
import pytest
from _pytest.fixtures import SubRequest
from datalad.conftest import setup_package  # noqa: F401


@pytest.fixture
def empty_dataset(tmp_path: pathlib.Path) -> da.Dataset:
    dataset = da.create(tmp_path)
    dataset.configuration("set", [("remote.cds.dry-run", "true")], scope="local")
    yield dataset
    dataset.drop(what="all", reckless="kill", recursive=True)


@pytest.fixture(params=["non-lazy", "lazy"])
def single_file_dataset(request: SubRequest, empty_dataset: da.Dataset) -> da.Dataset:
    request_dict = {
        "dataset": "reanalysis-era5-pressure-levels",
        "sub-selection": {
            "variable": "temperature",
            "pressure_level": "1000",
            "product_type": "reanalysis",
            "date": "2017-12-01/2017-12-31",
            "time": "12:00",
            "format": "grib",
        },
    }
    dataset = empty_dataset
    dataset.download_cds(
        request_dict,
        lazy=request.param == "lazy",
        path="download.grib",
    )
    return dataset
