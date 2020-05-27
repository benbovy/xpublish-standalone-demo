#!/usr/bin/env python3

# Usage (for development):
#
# $ export FLASK_APP=api_demo.py
# $ python -m flask run --host=0.0.0.0 --port=9000

from flask import Flask, request
from fsspec.implementations.http import HTTPFileSystem
import requests
import xarray as xr

from utils import extract_field_along_tracks


app = Flask(__name__)

# url and port of xpublish server running for the demo dataset
demo_dataset_server_url = "http://127.0.0.1:5000"

# http map of demo dataset
fs = HTTPFileSystem()
demo_dataset_http_map = fs.get_mapper(demo_dataset_server_url)


@app.route('/datasets/demo')
def get_demo_dataset_html_repr():
    return requests.get(demo_dataset_server_url + "/").text


@app.route('/api/v1.0/datasets/demo/fieldnames')
def get_demo_dataset_field_names():
    """Returns variable names in demo dataset."""

    fieldnames = requests.get(demo_dataset_server_url + "/keys").json()

    return {"fieldnames": fieldnames}


@app.route('/api/v1.0/datasets/demo/info')
def get_demo_dataset_info():
    """Returns demo dataset info."""

    info = requests.get(demo_dataset_server_url + "/info").json()

    return {"info": info}


@app.route("/api/v1.0/datasets/demo/extract_tracks/", methods=["POST"])
def extract_demo_data_along_tracks():
    """Extract data along given ship tracks."""

    request_data = request.get_json()

    dataset = xr.open_zarr(demo_dataset_http_map, consolidated=True)

    transform = request_data["transform"]

    if transform is not None:
        if transform.get("aggregation") == "mean":
            dataset = dataset.mean(dim=transform.get("dim"))

    return extract_field_along_tracks(
        dataset, request_data["fieldname"], request_data["tracks"]
    )