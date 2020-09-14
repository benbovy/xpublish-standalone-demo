#!/usr/bin/env python3

# Usage (for development):
#
# From the root directory, run
#
# $ uvicorn app.main:app --reload
#
from typing import List, Union

import xarray as xr
from fastapi import APIRouter, Depends
from xpublish.routers import base_router, common_router, zarr_router
from xpublish.dependencies import get_dataset


from .utils import DatasetTransform, extract_data_along_tracks, TrackCollection


extend_base_router = APIRouter()


@extend_base_router.get('/fieldnames')
def field_names(dataset: xr.Dataset = Depends(get_dataset)) -> List[str]:
    """Returns field names (data variables) in dataset."""

    fieldnames = dataset.data_vars.keys()

    return list(fieldnames)


esm_router = APIRouter()


@esm_router.post("/extract_tracks")
def extract_tracks(
        fieldnames: Union[str, List[str]],
        transform: DatasetTransform,
        tracks: TrackCollection,
        dataset: xr.Dataset = Depends(get_dataset),
) -> TrackCollection:
    """Extract data (one or multiple fields) along given ship tracks."""

    if transform.aggregation == "mean":
        dataset = dataset.mean(dim=transform.dim)

    return extract_data_along_tracks(dataset, fieldnames, tracks)


demo_dataset = xr.tutorial.open_dataset("air_temperature")

demo_dataset.rest(
    routers=[
        (base_router, {'tags': ['info']}),
        (extend_base_router, {'tags': ['info']}),
        (zarr_router, {'tags': ['zarr'], 'prefix': '/zarr'}),
        (esm_router, {'tags': ['esm'], 'prefix': '/esm'})
    ]
)

app = demo_dataset.rest.app