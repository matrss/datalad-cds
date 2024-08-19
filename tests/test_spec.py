import hypothesis as h
import pytest

from datalad_cds.spec import Spec


@h.given(...)
def test_spec_url_equality(spec: Spec) -> None:
    assert Spec.from_url(spec.to_url()) == spec


@h.given(...)
def test_spec_invalid_url_causes_value_error(url: str) -> None:
    h.assume(not url.startswith("cds:v1-"))
    with pytest.raises(ValueError):
        Spec.from_url(url)
