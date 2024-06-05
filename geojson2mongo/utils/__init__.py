__all__ = ['JSON_Subdir', 'dump_json', 'enum_json_files', 'flatten', 'load_json', 'load_source',
           'partition_scopes', 'reindent_all_json']

import json
import os
from typing import Any, AnyStr, Dict, List, Union

import dill as pickle

from geojson2mongo import root_path, source_path

JSON_Subdir = os.path.join(root_path, 'json')


def load_json(fp: AnyStr) -> Dict:
    with open(fp, 'r', encoding='utf-8') as input_f:
        return json.load(input_f)


def dump_json(obj: Dict, fp: AnyStr, *, indent: Union[None, str, int] = None):
    with open(fp, 'w', encoding='utf-8') as output_f:
        output_f.write(json.dumps(obj, indent=indent))


def reindent_all_json(*, indent: Union[None, int, str] = None):
    for file in os.listdir(JSON_Subdir):
        if not file.endswith('json'):
            continue
        file = os.path.join(JSON_Subdir, file)
        dump_json(load_json(file), file, indent=indent)


def flatten(nested_list: list[list[Any]]):
    for sublist in nested_list:
        for item in sublist:
            if not isinstance(item, int):
                yield item


def partition_scopes(filepaths: Union[List[AnyStr], None] = None, scopes=None):
    if filepaths is None:
        filepaths = os.listdir(JSON_Subdir)
    if scopes is None:
        scopes = ['base-boundary', 'admin-divisions']
    partitions = [[], []]
    for _fp in filepaths:
        eq_tuple = (_fp[2:].startswith(scopes[0]), _fp[2:].startswith(scopes[1]))
        for eq in enumerate(eq_tuple):
            if eq[1] is True:
                partitions[eq[0]].append(_fp)
    return partitions


def load_source(fp: AnyStr = os.path.join(source_path, 'src_json.pkl')):
    def build_cache():
        src = []
        scopes = list(flatten(partition_scopes()))
        for scope in scopes:
            json_data = load_json(os.path.join(JSON_Subdir, scope))
            src.append(json_data)
        with open(fp, 'wb') as wf:
            pickle.dump(src, wf)
        return src

    if not os.path.exists(fp):
        return build_cache()
    else:
        with open(fp, 'rb') as rf:
            return pickle.load(rf)


def enum_json_files():
    name2id_hashmap = {}

    def get_feature_properties(idx, obj: Dict[str, Any]):
        name_chain = []
        for key, value in list(obj.items()):
            key: str
            if (key.startswith('name') and key[-1].isnumeric()) or (key == 'sovereign'):
                if key == 'sovereign':
                    id_tag = '0'
                elif key.startswith('name') and value is not None:
                    id_tag = key[-1]
                else:
                    continue
                ord_id = obj.get(f'id_{id_tag}')
                name_chain.append(ord_id)
        id_str = ':'.join(map(lambda x: str(x), name_chain))
        name2id_hashmap[id_str] = idx

    json_src = load_source()
    for json_data in json_src:
        feature_keys: list = json_data.get('features')
        for feature in feature_keys:
            feature_idx = [json_src.index(json_data), feature_keys.index(feature)]
            if isinstance(feature, dict):
                feature: dict
                get_feature_properties(feature_idx, feature.get('properties'))
    return name2id_hashmap


if __name__ == '__main__':
    reindent_all_json()
