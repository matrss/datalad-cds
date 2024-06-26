"""DataLad CDS extension"""

__docformat__ = "restructuredtext"

import logging

lgr = logging.getLogger("datalad.cds")

# Defines a datalad command suite.
# This variable must be bound as a setuptools entrypoint
# to be found by datalad
command_suite = (
    # description of the command suite, displayed in cmdline help
    "Custom Downloader for CDS data-store",
    [
        # specification of a command, any number of commands can be defined
        (
            # importable module that contains the command implementation
            "datalad_cds.download_cds",
            # name of the command class implementation in above module
            "DownloadCDS",
            # optional name of the command in the cmdline API
            "download-cds",
            # optional name of the command in the Python API
            "download_cds",
        ),
    ],
)

from . import _version  # noqa: E402

__version__ = _version.get_versions()["version"]
