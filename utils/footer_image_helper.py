#!/usr/bin/env python3

# Copyright Muxup Contributors.
# Distributed under the terms of the MIT license, see LICENSE for details.
# SPDX-License-Identifier: MIT

import base64
import json
import os
import pathlib
import pprint
import random
import shutil
import subprocess
import flask
from flask import Flask
from flask import request

datasets = [
"ant",
"bat",
"bear",
"bee",
"bird",
"butterfly",
"camel",
"cat",
"cow",
"crab",
"crocodile",
"dog",
"dolphin",
"dragon",
"duck",
"elephant",
"fish",
"flamingo",
"frog",
"giraffe",
"hedgehog",
"horse",
"kangaroo",
"lion",
"lobster",
"monkey",
"mosquito",
"octopus",
"owl",
"panda",
"parrot",
"penguin",
"pig",
"rabbit",
"raccoon",
"rhinoceros",
"scorpion",
"sea turtle",
"shark",
"sheep",
"snail",
"spider",
"squirrel",
"swan",
"tiger",
"whale",
"zebra"
]

# Operate in root dir of the site.
os.chdir(pathlib.Path(__file__).parent.parent)
footer_data_path = pathlib.Path("footer_drawings.json")
footer_data = json.loads(footer_data_path.read_text(encoding="utf-8"))
dataset_count = dict.fromkeys(datasets, 0)
used_keys = set()
for entry in footer_data:
    dataset = entry[0]
    key = entry[1]
    used_keys.add(key)
    dataset_count[dataset] = dataset_count[dataset] + 1
pprint.pprint(dataset_count)

cache_path = pathlib.Path("cache")
if not cache_path.is_dir():
    cache_path.mkdir()


def ndjson_to_svg(parsed: str) -> str:
    ret = []
    ret.append('<svg width="256" height="256" xmlns="http://www.w3.org/2000/svg">')
    ret.append('<g stroke="black" fill="transparent" stroke-width="4">')
    for line in parsed['drawing']:
        x_vals, y_vals = line[0], line[1]
        path = []
        for idx, x in enumerate(x_vals):
            y = y_vals[idx]
            if idx == 0:
                path.append(f'<path d="M {x} {y}')
            else:
                path.append(f' L {x} {y}')
        path.append('"/>')
        ret.append("".join(path))
    ret.append('</g>')
    ret.append("</svg>\n")
    return "\n".join(ret)


for dataset in datasets:
    dataset_ndjson = dataset + ".ndjson"
    if not (cache_path / dataset_ndjson).is_file():
        print(f"File {dataset_ndjson} doesn't exist in cache dir - downloading")
        subprocess.run(["wget", "https://storage.googleapis.com/quickdraw_dataset/full/simplified/"+dataset_ndjson, "--directory-prefix=/tmp"], check=True)
        shutil.move(pathlib.Path("/tmp")/dataset_ndjson, cache_path/dataset_ndjson)

app = Flask(__name__)

@app.route("/")
def home():
    selected_dataset = min(dataset_count, key=dataset_count.get)
    with (cache_path/(selected_dataset+".ndjson")).open('r', encoding="utf-8") as f:
        lines = list(f)
    ret = []
    ret.append(f"""\
<!DOCTYPE html>
<html lang="en">
<head>
<title>Muxup footer image selector</title>
<style>
  button {{
  border: none;
  outline: none;
  background: none;
  cursor: pointer;
  padding: 0;
  text-decoration: none;
  font-family: inherit;
  font-size: inherit;
}}
</style>
</head>
<body>
<h1>Images from {selected_dataset} (current count: {dataset_count[selected_dataset]})</h1>
<form action="{flask.url_for("add")}" method="post">
<input name="dataset" type="hidden" value="{selected_dataset}"></input>
"""
               )
    num_selected_images = 0
    while num_selected_images < 30:
        random_idx = random.randrange(len(lines))
        parsed = json.loads(lines[random_idx])
        if parsed["key_id"] in used_keys:
            continue
        svg = ndjson_to_svg(parsed)
        svg_encoded = base64.b64encode(bytes(svg, "utf-8")).decode("ascii")
        if num_selected_images % 10 == 0:
            ret.append("<br>")
        ret.append(f'<button name="line" value="{random_idx}"><img src="data:image/svg+xml;base64,{svg_encoded}" width="50"></button>')
        num_selected_images += 1
    ret.append("""\
</form>
</body>
</html>
</head>\
"""
    )
    return "\n".join(ret)

@app.route("/add", methods=["POST"])
def add():
    dataset = request.form["dataset"]
    with (cache_path/(dataset+".ndjson")).open('r', encoding="utf-8") as f:
        lines = list(f)
    idx = int(request.form["line"])
    parsed = json.loads(lines[idx])
    if parsed["key_id"] in used_keys:
        raise ValueError("can't create svg as drawing was already used")
    svg = ndjson_to_svg(parsed)
    output_path = pathlib.Path("static")/"footer"/(str(len(footer_data)).zfill(4)+".svg")
    output_path.write_text(svg, encoding="utf-8")
    used_keys.add(parsed["key_id"])
    dataset_count[dataset] = dataset_count[dataset] + 1
    footer_data.append([dataset, parsed["key_id"]])
    footer_data_path.write_text(json.dumps(footer_data, indent=2))

    return flask.redirect("/")
    

app.run(debug=True)
