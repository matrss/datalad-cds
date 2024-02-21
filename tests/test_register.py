import datalad.api as da


def test_register() -> None:
    assert hasattr(da, "download_cds")
