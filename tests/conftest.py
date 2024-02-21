import pathlib

import datalad.api as da
import pytest
from datalad.conftest import setup_package  # noqa: F401


@pytest.fixture
def empty_dataset(tmp_path: pathlib.Path) -> da.Dataset:
    dataset = da.create(tmp_path)
    yield dataset
    dataset.drop(what="all", reckless="kill", recursive=True)
