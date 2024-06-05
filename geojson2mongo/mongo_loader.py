import argparse
import os

from dotenv import load_dotenv
from pymongo import MongoClient

from metadata import TreeMap


def load_env_file(env_path):
    load_dotenv(env_path)


def load_to_mongo(data: dict):
    MONGO_URI = os.getenv('MONGO_URI')
    DATABASE_NAME = os.getenv('DATABASE_NAME')
    COLLECTION_NAME = os.getenv('COLLECTION_NAME')

    client = MongoClient(MONGO_URI)
    db = client[DATABASE_NAME]
    collection = db[COLLECTION_NAME]
    collection.insert_many([data[key] for key in data.keys()])
    client.close()


def main(env_path):
    load_env_file(env_path)
    treemap = TreeMap()
    treemap.transform(keychain=['properties', 'names'])
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
        if parent is not None:
            parent_node = str(':'.join(k.split(':')[:-1]))
            if parent_node not in node_rel_dict.keys():
                raise ValueError(f'Parent node not in keys: {parent_node}')
            if not node_rel_dict[parent_node].get('children', None):
                node_rel_dict[parent_node]['children'] = []
            node_rel_dict[parent_node]['children'].append(k)
        else:
            parent_node = None
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

    load_to_mongo(node_rel_dict)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Load GeoJSON data to MongoDB')
    parser.add_argument('--env', type=str, default='.env', help='Path to the .env file')
    args = parser.parse_args()
    main(args.env)