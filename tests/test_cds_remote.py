import subprocess

import datalad.api as da


def test_with_git_annex_testremote(single_file_dataset: da.Dataset) -> None:
    dataset = single_file_dataset
    dataset.get("download.grib")
    result = subprocess.run(
        [
            "git",
            "-C",
            dataset.path,
            "annex",
            "testremote",
            "cds",
            "--test-readonly",
            "download.grib",
        ],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0, f"{result.stdout=}\n{result.stderr=}"
