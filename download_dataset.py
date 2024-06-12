import json
import os

import requests

STANFORD_EARTHWORKS_SUBDOMAIN = 'https://earthworks.stanford.edu'


def main(dataset='rwanda-2015'):
    dataset_ids_fp = os.path.abspath('dataset_ids.json')
    with open(dataset_ids_fp, 'r', encoding='utf-8') as jf:
        dataset_ids_json: dict[str, dict[str, str]] = json.load(jf)
    if dataset_ids_json.get(dataset, None) is not None:
        if dataset == 'rwanda-2015':
            print(f"Downloading default GeoJSON dataset '{dataset}'")
        else:
            print(f"Downloading GeoJSON dataset '{dataset}'")
        for output_fn_prefix, geojson_id in dataset_ids_json[dataset].items():
            stanford_download_href = f'{STANFORD_EARTHWORKS_SUBDOMAIN}/download/file/stanford-{geojson_id}-geojson.json'
            geojson_part = stanford_download_href.split('/')[-1].split('-')[-1]
            local_fn = '-'.join([output_fn_prefix, dataset, geojson_part])
            local_fn_abspath = os.path.join(os.path.abspath(f'./geojson2mongo/json_data'), local_fn)
            with requests.get(stanford_download_href, stream=True) as r:
                print(f"Retrieving GeoJSON file from '{stanford_download_href}'...")
                r.raise_for_status()
                with open(local_fn_abspath, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
                    print(f"File saved as '{local_fn}'")
    else:
        raise ValueError(
            f"Dataset '{dataset}' not found in the dataset IDs JSON file")


if __name__ == '__main__':
    main()
