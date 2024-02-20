# DataLad extension for the Copernicus Climate Data Store


## What?

A DataLad extension to integrate with the Copernicus Climate Data Store (CDS).
So far this just implements a `datalad download-cds` command that can be used to fetch data from the CDS
and record this action in a way so that `datalad get` (or just `git annex get`) can redo the download in the future.


## Why?

This extension enables automated provenance tracking for fetching data from the CDS.
In a dataset that retrieves data from the CDS using this extension it will become visible how this data was initially fetched
and how it can be retrieved again in the future.


## How?

You will first have to create an account with the CDS,
if you don't have one already.
You can do so here: <https://cds.climate.copernicus.eu/user/register?destination=%2F%23!%2Fhome>

Next,
you will need to create the "~/.cdsapirc" file as described here: <https://cds.climate.copernicus.eu/api-how-to#install-the-cds-api-key>.
This file is required since the datalad-cds extension internally uses the cdsapi package
and therefore uses its authentication mechanism.

Also,
you need to install datalad and the datalad-cds extension.
Both can be had through pip.

Now you are ready to use the extension.
When you look through the CDS you will notice that for any given dataset you can select a subset of the data using the "Download data" tab.
After you do that you can use the "Show API request" button at the bottom to get a short python script that would fetch the chosen subset using the cdsapi.
The following is an example of that:
```python
#!/usr/bin/env python
import cdsapi
c = cdsapi.Client()
c.retrieve(
    "reanalysis-era5-pressure-levels",
    {
        "variable": "temperature",
        "pressure_level": "1000",
        "product_type": "reanalysis",
        "year": "2008",
        "month": "01",
        "day": "01",
        "time": "12:00",
        "format": "grib"
    },
    "download.grib",
)
```

To fetch the same data to the same local file using datalad-cds we just need to adapt this a little:
```bash
$ datalad download-cds --path download.grib '
    {
        "dataset": "reanalysis-era5-pressure-levels",
        "sub-selection": {
            "variable": "temperature",
            "pressure_level": "1000",
            "product_type": "reanalysis",
            "year": "2008",
            "month": "01",
            "day": "01",
            "time": "12:00",
            "format": "grib"
        }
    }
'
```

The local path to save to ("download.grib") becomes the `--path` argument.
The dataset name ("reanalysis-era5-pressure-levels" in this case) becomes the value of the `dataset` key in a json object that describes the data to be downloaded.
The sub-selection of the dataset becomes the value of the `sub-selection` key.

After executing the above `datalad download-cds` command in a DataLad dataset a file called "download.grib" should be newly created.
This file will have its origin tracked in git-annex (you can see that by running `git annex whereis download.grib`).
If you now `datalad drop` the file
and then `datalad get` it you'll see that git-annex will automatically re-retrieve the file from the CDS
as if it was just another location to get data from.

To see more possible usage options take a look at the help page of the command (`datalad download-cds --help`)
or the documentation at <https://matrss.github.io/datalad-cds/>.
