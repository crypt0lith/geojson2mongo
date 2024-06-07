geojson2mongo
---

## Overview

`geojson2mongo` is a utility module for  [GeoJSON data](https://datatracker.ietf.org/doc/html/rfc7946) that focuses on constructing metadata mappings of GeoJSON objects, and loading those mappings into a MongoDB instance.

## Installation

```bash
git clone https://github.com/crypt0lith/geojson2mongo.git
cd geojson2mongo
```

Install dependencies:
```bash
pip install -r requirements.txt
```

Then run the extract script to unzip the example dataset:
```bash
python extract_dataset.py
```

## Setup `.env`

Create a file named `.env` with the following variables:
```dotenv
MONGO_URI = "mongodb://localhost:27017"  
DATABASE_NAME = "test_db"  
COLLECTION_NAME = "test_coll"
```

Specify its path using the `--env` argument when executing the script.
```bash
python -m geojson2mongo.loader --env /path/to/your/.env
```
