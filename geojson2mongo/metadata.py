import os
from _collections_abc import MutableMapping
from typing import Any, Iterable, Iterator, Mapping, TypeVar, Union

from geometry import MultiPolygon
from utils import JSON_Subdir, dump_json, enum_json_files, load_json, load_source

MetadataJSONPath = os.path.join(JSON_Subdir, 'metadata.json')

_KT = TypeVar('_KT')
_KT_co = TypeVar('_KT_co', covariant=True)
_KT_contra = TypeVar('_KT_contra', contravariant=True)
_VT = TypeVar('_VT')
_VT_co = TypeVar('_VT_co', covariant=True)
_T = TypeVar('_T')
_T_co = TypeVar('_T_co', covariant=True)
_T_contra = TypeVar('_T_contra', contravariant=True)
KeychainType = Union[str, Iterable[Union[str, int]]]


def generate_metadata_file():
    dump_json(obj=enum_json_files(), fp=MetadataJSONPath)


def recursive_get(obj: Mapping, keychain: KeychainType) -> Any:
    if isinstance(keychain, str):
        return obj[keychain]
    else:
        __o = obj
        for _recurs_key in keychain:
            if not _recurs_key.endswith('*'):
                __r: Any = __o.get(_recurs_key, {})
                if isinstance(__r, dict):
                    if __r == {}:
                        break
                    else:
                        __o = __r
                else:
                    return __r
            else:
                search_pattern = _recurs_key.split('*')[0]
                for _k in __o.keys():
                    if _k.startswith(search_pattern):
                        return __o.get(_k)
                    elif _k == 'sovereign' and search_pattern.startswith('type'):
                        return 'state'.title()
        return __o


class MetadataHandler:
    def __init__(self):
        self.source = load_source()
        if not os.path.exists(MetadataJSONPath):
            generate_metadata_file()
        self.metadata: dict[str, tuple[int, int]] = load_json(MetadataJSONPath)

    def get_pointer_data(self, keychain: KeychainType = 'properties', **kwargs) -> dict | None:
        all_json_data = {}

        def key_handler(obj, src, **_):
            obj[key] = recursive_get(src, keychain=keychain)

        def handle_properties(obj, src, get_ids=False, get_names=False):
            if get_ids or get_names:
                ids = []
                src_props = src['properties']
                str_getter = 'id' if get_ids else 'name'
                for p in src_props.keys():
                    split_k = p.split('_')
                    if len(split_k) == 2:
                        if split_k[0] == str_getter and (split_k[1].isnumeric() or split_k[1] == 'engli'):
                            ids.append(src_props.get(p))
                obj[key] = ids
            else:
                obj[key] = recursive_get(src, keychain=keychain)

        id_str = kwargs.get('id_str', None)

        def instancecheck(_key_handler, _get_keys):
            if isinstance(keychain, list) and len(keychain) > 1 and keychain[0] == 'properties':
                _key_handler = handle_properties
                handle_props_kwargs = {
                    'ids': {
                        'get_ids': True,
                        'get_names': False
                    },
                    'names': {
                        'get_ids': False,
                        'get_names': True
                    }
                }
                _get_keys = handle_props_kwargs.get(keychain[1], {})
            elif isinstance(keychain, str) and keychain == 'properties':
                _key_handler = handle_properties
                _get_keys = {
                    'get_ids': True
                }
            return _key_handler, _get_keys

        if id_str is not None:
            key = id_str
            idx_0, idx_1 = self.metadata[id_str]
            return recursive_get(self.source[idx_0]['features'][idx_1], keychain)
        else:
            get_keys = {}
            key_handler, get_keys = instancecheck(key_handler, get_keys)
            for key in self.metadata.keys():
                k_idx_0, k_idx_1 = self.metadata[key]
                k_source = self.source[k_idx_0]['features'][k_idx_1]
                key_handler(obj=all_json_data, src=k_source, **get_keys)
            return all_json_data

    @staticmethod
    def generate_tree(mapping: Mapping[_KT, _VT]):
        def instancecheck(__node):
            if isinstance(__node, str):
                if __node.split('_')[-1].isnumeric():
                    return int(__node)
            return __node

        tree = {}
        keychain_lookup = {}
        it = iter(mapping)
        for _ in range(len(mapping)):
            keychain = []
            concat_chain_str = next(it)
            chain = mapping.get(concat_chain_str)
            if not chain:
                break
            node_0 = instancecheck(chain[0])
            keychain.append(node_0)
            if node_0 not in tree:
                tree[node_0] = {}
            cur_node = tree[node_0]
            for link in chain[1:]:
                node_x = instancecheck(link)
                keychain.append(node_x)
                if node_x not in cur_node:
                    cur_node[node_x] = {}
                cur_node = cur_node[node_x]
            keychain_lookup[concat_chain_str] = keychain
        return tree, keychain_lookup


class TreeMap(MutableMapping):
    def __new__(cls, *args, **kwargs):
        instance = super(TreeMap, cls).__new__(cls)
        handler = MetadataHandler()
        tree, keychain_lookup = handler.generate_tree(handler.get_pointer_data())
        instance.handler = handler
        instance.tree = tree
        instance.lookup_table = keychain_lookup
        return instance

    def __init__(self):
        self.root = self._Link()
        self.root.next = self.root.prev = self.root
        self.__map = {}
        for key, value in self.lookup_table.items():
            self.__map[key] = self._Link(key=key)
            self.root.prev.next = self.__map[key]
            self.__map[key].prev = self.root.prev
            self.root.prev = self.__map[key]
            self.__map[key].next = self.root
        self.root.prev.next = self.root
        self.__update()


    class _Link:
        __slots__ = 'prev', 'next', 'key', 'geom', 'type', '__weakref__'

        def __init__(self, key=None):
            self.key = key
            self.geom = None
            self.type = None
            self.next = None
            self.prev = None


    def __getitem__(self, __k: _KT) -> _VT_co:
        keychain = self.lookup_table.get(__k)
        if keychain is None:
            raise KeyError(__k)
        return recursive_get(self.tree, keychain)

    def __setitem__(self, __k: _KT, __v: _VT) -> None:
        raise NotImplementedError(
            "TreeMap items are immutable. Use 'TreeMap.transform()' to update the mapping")

    def transform(self, keychain=None):
        if keychain is None:
            self.update(self.handler.get_pointer_data(keychain=['properties', 'ids']))
        elif isinstance(keychain, list) and keychain[0] == 'properties' and keychain[-1] in ['ids', 'names']:
            self.update(self.handler.get_pointer_data(keychain=keychain))
        else:
            __m = {}
            iterator = reversed(self.lookup_table.keys())
            for _ in range(len(self.lookup_table)):
                it: str = next(iterator)
                sub_it = it.split(':')
                sub_keys = [sub_it[0]]
                for subkey_part in sub_it[1:]:
                    cur_idx = sub_it.index(subkey_part)
                    rejoined_str: str = sub_keys[cur_idx - 1] + f':{sub_it[cur_idx]}'
                    sub_keys.append(rejoined_str)
                subdict = {}
                sub_values = []
                for s in sub_keys:
                    res: dict | None = None
                    if s not in subdict:
                        if s in self.lookup_table:
                            res = self.handler.get_pointer_data(id_str=s, keychain=keychain)
                            subdict[s] = res
                    else:
                        res = subdict[s]
                    if res is not None:
                        sub_values.append(res)
                __m[it] = sub_values
            self.update(__m)

    def update(self, __m: Mapping[_KT, _VT], **kwargs: _VT) -> None:
        tree, keychain_lookup = self.handler.generate_tree(__m)
        self.lookup_table.update(keychain_lookup)
        self.tree.clear()
        self.tree.update(tree)

    def geom(self, __k: _KT) -> MultiPolygon:
        return self.__map[__k].geom

    def div_type(self, __k: _KT) -> str:
        return self.__map[__k].type

    def __delitem__(self, __k: _KT) -> None:
        raise NotImplementedError(
            'Deletion is not supported for TreeMap objects.')

    def __len__(self) -> int:
        return len(self.lookup_table)

    def __iter__(self) -> Iterator[_KT]:
        current = self.root.next
        while current is not self.root:
            yield current.key
            current = current.next

    def __update(self):
        def _get_ptr(keychain):
            return self.handler.get_pointer_data(id_str=__k, keychain=keychain)

        def _multipolygon():
            coords = _get_ptr(['geometry', 'coordinates'])
            bbox = _get_ptr(['properties', 'bbox'])
            if not isinstance(bbox, list):
                try:
                    bbox = _get_ptr(['bbox'])
                    return MultiPolygon(coords, bbox)
                except ValueError as e:
                    raise e from None
            return MultiPolygon(coords, bbox)

        def _type():
            return _get_ptr(['properties', 'type_*'])

        for __k in self.lookup_table.keys():
            self.__map[__k].key = __k
            self.__map[__k].geom = _multipolygon()
            self.__map[__k].type = _type()
