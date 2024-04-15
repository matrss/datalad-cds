from __future__ import annotations

import base64
import dataclasses
import json
import urllib.parse
from typing import Any, Dict

import datalad_cds.compat


@dataclasses.dataclass
class Spec:
    dataset: str
    sub_selection: dict

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> Spec:
        return cls(dataset=d["dataset"], sub_selection=d["sub-selection"])

    @classmethod
    def from_json(cls, s: str) -> Spec:
        return cls.from_dict(json.loads(s))

    @classmethod
    def from_url(cls, url: str) -> Spec:
        if not url.startswith("cds:v1-"):
            raise ValueError("unsupported URL value encountered")
        spec = cls.from_json(
            base64.urlsafe_b64decode(
                urllib.parse.unquote(
                    datalad_cds.compat.removeprefix(url, "cds:v1-")
                ).encode("utf-8")
            ).decode("utf-8")
        )
        return spec

    def to_dict(self) -> Dict[str, Any]:
        return {
            "dataset": self.dataset,
            "sub-selection": self.sub_selection,
        }

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), separators=(",", ":"), sort_keys=True)

    def to_url(self) -> str:
        json_spec = self.to_json()
        url = "cds:v1-" + urllib.parse.quote(
            base64.urlsafe_b64encode(json_spec.encode("utf-8"))
        )
        return url
