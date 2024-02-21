import pathlib
import subprocess

import cdsapi
from annexremote import Master, ProtocolError, RemoteError, SpecialRemote

import datalad_cds.spec

CDS_REMOTE_UUID = "923e2755-e747-42f4-890a-9c921068fb82"


class CDSRemote(SpecialRemote):
    transfer_store = None
    remove = None

    def initremote(self) -> None:
        pass

    def prepare(self) -> None:
        pass

    def _is_dry_run(self) -> bool:
        try:
            remote_name = self.annex.getgitremotename()
        except ProtocolError:
            return False
        git_dir = self.annex.getgitdir()
        result = subprocess.run(
            [
                "git",
                "--git-dir={}".format(git_dir),
                "config",
                "--get",
                "remote.{}.dry-run".format(remote_name),
            ],
            capture_output=True,
            text=True,
        )
        return result.returncode == 0 and result.stdout.strip() == "true"

    def _retrieve_cds(self, spec: datalad_cds.spec.Spec, filename: str) -> None:
        if self._is_dry_run():
            pathlib.Path(filename).write_text(spec.to_json())
            return
        c = cdsapi.Client()
        c.retrieve(spec.dataset, spec.sub_selection, filename)

    def transfer_retrieve(self, key: str, filename: str) -> None:
        urls = self.annex.geturls(key, "cds:")
        for url in urls:
            try:
                self._retrieve_cds(datalad_cds.spec.Spec.from_url(url), filename)
                break
            except:  # noqa: E722
                pass
        else:
            raise RemoteError("Failed to handle key {}".format(key))

    def whereis(self, key: str) -> str:
        url = self.annex.geturls(key, "cds:")[0]
        return datalad_cds.spec.Spec.from_url(url).to_json()

    def checkpresent(self, key: str) -> bool:
        # We just assume that we can always handle the key
        return True

    def claimurl(self, url: str) -> bool:
        return url.startswith("cds:")

    def checkurl(self, url: str) -> bool:
        return url.startswith("cds:")

    def getcost(self) -> int:
        # This is a very expensive remote
        return 1000

    def getavailability(self) -> str:
        # The Climate Data Store is publicly available on the internet
        return "global"


def main() -> None:
    master = Master()
    remote = CDSRemote(master)
    master.LinkRemote(remote)
    master.Listen()