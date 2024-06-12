"""DataLad extension for the Climate Data Store"""

__docformat__ = "restructuredtext"
import logging
from typing import Iterable, Literal, Optional, Union

from datalad.distribution.dataset import (
    EnsureDataset,
    datasetmethod,
    require_dataset,
)
from datalad.interface.base import Interface, build_doc, eval_results
from datalad.interface.common_opts import nosave_opt, save_message_opt
from datalad.interface.results import get_status_dict
from datalad.support.annexrepo import AnnexRepo
from datalad.support.constraints import EnsureNone, EnsureStr
from datalad.support.param import Parameter

import datalad_cds.cds_remote
import datalad_cds.spec

logger = logging.getLogger("datalad.cds.download_cds")


# decoration auto-generates standard help
@build_doc
# all commands must be derived from Interface
class DownloadCDS(Interface):
    """Downloads specified datasets from the CDS data store"""

    _params_ = dict(
        spec=Parameter(
            doc="""A json string or python dictionary containing the key
            "dataset" with the datasets name (i.e. what is shown as the first
            parameter to cdsapi.Client.retrieve if you do a "Show API request"
            on some dataset in the CDS) and the key "sub-selection" with the
            sub-selection of the dataset that should be fetched (i.e. what is
            shown as the second parameter to cdsapi.Client.retrieve).""",
        ),
        dataset=Parameter(
            args=("-d", "--dataset"),
            metavar="PATH",
            doc="""specify the dataset to add files to. If no dataset is given,
            an attempt is made to identify the dataset based on the current
            working directory. Use [CMD: --nosave CMD][PY: save=False PY] to
            prevent adding files to the dataset.""",
            constraints=EnsureDataset() | EnsureNone(),
        ),
        path=Parameter(
            args=("-O", "--path"),
            doc="""target path to download to.""",
            constraints=EnsureStr(),
        ),
        batch=Parameter(
            args=("--batch",),
            action="store_true",
            doc="""By default a single call to `git annex addurl` will be made
            for each request to download. The batch option can be supplied to
            instead re-use a `git annex addurl --batch` process for multiple
            consecutive calls to download-cds. This is only useful when used
            with the python API.""",
        ),
        lazy=Parameter(
            args=("--lazy",),
            action="store_true",
            doc="""By default the file will be immediately downloaded. If the
            lazy flag is supplied then the CDS request is only recorded as a
            source for the file, but no download is initiated. Keep in mind that
            there is no way to validate the correctness of the request if the
            lazy flag is used.""",
        ),
        save=nosave_opt,
        message=save_message_opt,
    )

    @staticmethod
    @datasetmethod(name="download_cds")
    @eval_results
    def __call__(
        spec: Union[str, dict],
        path: str,
        *,
        dataset: Optional[str] = None,
        message: Optional[str] = None,
        batch: bool = False,
        lazy: bool = False,
        save: bool = True,
    ) -> Iterable[dict]:
        if isinstance(spec, dict):
            parsed_spec = datalad_cds.spec.Spec.from_dict(spec)
        elif isinstance(spec, str):
            parsed_spec = datalad_cds.spec.Spec.from_json(spec)
        else:
            raise TypeError("spec could not be parsed")
        ds = require_dataset(dataset, check_installed=True)
        ensure_special_remote_exists_and_is_enabled(ds.repo, "cds")
        pathobj = ds.pathobj / path
        url = parsed_spec.to_url()
        options = []
        if lazy:
            options.append("--fast")
            options.append("--verifiable")
        ds.repo.add_url_to_file(pathobj, url, batch=batch, options=options)
        if save:
            msg = (
                message
                if message is not None
                else "[DATALAD] Download from Climate Data Store"
            )
            yield ds.save(pathobj, message=msg)
        yield get_status_dict(action="cds", ds=ds, status="ok")


def ensure_special_remote_exists_and_is_enabled(
    repo: AnnexRepo, remote: Literal["cds"]
) -> None:
    """Initialize and enable the cds special remote, if it isn't already.

    Very similar to datalad.customremotes.base.ensure_datalad_remote.
    """

    uuids = {"cds": datalad_cds.cds_remote.CDS_REMOTE_UUID}
    uuid = uuids[remote]

    name = repo.get_special_remotes().get(uuid, {}).get("name")
    if not name:
        repo.init_remote(
            remote,
            [
                "encryption=none",
                "type=external",
                "autoenable=true",
                "externaltype={}".format(remote),
                "uuid={}".format(uuid),
            ],
        )
    elif repo.is_special_annex_remote(name, check_if_known=False):
        logger.debug("special remote %s is enabled", name)
    else:
        logger.debug("special remote %s found, enabling", name)
        repo.enable_remote(name)
