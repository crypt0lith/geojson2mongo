__all__ = ['main_cli']

import argparse
import os

from dotenv import load_dotenv
from pymongo import MongoClient

from .metadata import TreeMap


def check_jsondir_is_empty(json_data_subdir: list[str]):
    it = iter(json_data_subdir)
    while True:
        try:
            if next(it).endswith('geojson.json'):
                return
        except StopIteration:
            break
    from download_dataset import STANFORD_EARTHWORKS_SUBDOMAIN, main as download_default_dataset
    print('JSON data subdirectory is empty.')
    try:
        user_inp: str = ''
        while user_inp.lower() not in ['y', 'n']:
            try:
                user_inp = input(
                    f"Download the default GeoJSON dataset 'rwanda-2015' from '"
                    f"{STANFORD_EARTHWORKS_SUBDOMAIN}'? "
                    f"[y, N]: ")
            except KeyboardInterrupt as e:
                print()
                raise e from None
        if user_inp == 'y':
            download_default_dataset()
        elif user_inp == 'n':
            exit()
    except Exception as e:
        raise e


def relate_nodes(treemap: 'TreeMap') -> dict:
    node_rel_dict = {}
    k_unique = set()
    for k in treemap.lookup_table.keys():
        if k in k_unique:
            raise ValueError(f'Non-unique key found: {k}')
        else:
            k_unique.add(k)
        k_levels = treemap.lookup_table.get(k)
        if len(k_levels) > 1:
            parent = f'{k_levels[-2]}'
        else:
            parent = None
        parent_node = handle_parent_node(k, node_rel_dict, parent)
        name = treemap.lookup_table.get(k)[-1]
        div_type = treemap.div_type(k)
        geoshape = treemap.geom(k)
        shape_data = {
            'centroid': geoshape.centroid,
            'bbox': geoshape.bbox,
            'coordinates': geoshape.coordinates
        }
        node_rel_dict[k] = dict(
            node=k, name=name, type=div_type, parent=parent_node, children=[], geom=shape_data)
    return node_rel_dict


def handle_parent_node(k: str, node_rel_dict: dict, parent):
    if parent is not None:
        parent_node = str(':'.join(k.split(':')[:-1]))
        if parent_node not in node_rel_dict.keys():
            raise ValueError(f'Parent node not in keys: {parent_node}')
        if not node_rel_dict[parent_node].get('children', None):
            node_rel_dict[parent_node]['children'] = []
        node_rel_dict[parent_node]['children'].append(k)
    else:
        parent_node = None
    return parent_node


def load_to_mongo(data: dict):
    MONGO_URI = os.getenv('MONGO_URI')
    DATABASE_NAME = os.getenv('DATABASE_NAME')
    COLLECTION_NAME = os.getenv('COLLECTION_NAME')
    print('Uploading GeoJSON metadata to MongoDB...')
    client = MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]
    collection = db[COLLECTION_NAME]
    collection.insert_many([data[key] for key in data.keys()])
    client.close()


def main(env_path):
    json_data_subdir = os.listdir(os.path.join(os.path.dirname(__file__), './json_data'))
    check_jsondir_is_empty(json_data_subdir)
    print('Processing GeoJSON metadata...')
    treemap = TreeMap()
    treemap.transform(keychain=['properties', 'names'])
    load_dotenv(env_path)
    load_to_mongo(relate_nodes(treemap))


def main_cli():
    parser = argparse.ArgumentParser(description='Load GeoJSON data to MongoDB')
    parser.add_argument('--env', type=str, default='.env', help='Path to the .env file')
    args = parser.parse_args()
    main(args.env)
