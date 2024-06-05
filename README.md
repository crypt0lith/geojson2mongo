geojson2mongo
---
## Overview
`geojson2mongo` is a utility module for  [GeoJSON data](https://datatracker.ietf.org/doc/html/rfc7946) that focuses on constructing metadata mappings of GeoJSON objects, and loading those mappings into a MongoDB instance.

This is an **early version** of `geojson2mongo` (v0.1.0), so the scope remains limited to the original design context. Most of the control flow expects GeoJSON MultiPolygon geometries that specifically represent administrative and political divisions, since the original dataset used was the administrative divisions of Rwanda from the [Global Administrative Areas 2015 dataset.](https://earthworks.stanford.edu/?_=1462045970854&f%5Baccess%5D%5B%5D=public&f%5Baccess%5D%5B%5D=available&f%5Bdc_format_s%5D%5B%5D=Shapefile&f%5Bdc_subject_sm%5D%5B%5D=Administrative+and+political+divisions&f%5Bdct_provenance_s%5D%5B%5D=Stanford&f%5Bdct_spatial_sm%5D%5B%5D=Rwanda&f%5Blayer_geom_type_s%5D%5B%5D=Polygon&per_page=20&search_field=dummy_range&sort=score+desc%2C+dc_title_sort+asc) Future updates should focus on making the module more generalizable and extensible.

## Installation

Install using pip (recommended):
```bash
pip install geojson2mongo
```

## Setup `.env`

Create a file named `.env` with the following variables:
```dotenv
MONGO_URI = "mongodb://localhost:27017"  
DATABASE_NAME = "example_database"  
COLLECTION_NAME = "example_collection"
```

Specify its path using the `--env` argument when executing the script.
```bash
python -m geojson2mongo --env /path/to/your/.env
```