from io import TextIOWrapper
import json
import logging
from os import makedirs, path
import pickle
from pyparsing import Any

from openmxr.utils.hash import mkmd5


class Cache:
    name: str
    binary_format = False
    
    def __init__(self, name: str):
        self.name = name
        self.check_cache_exists()
    
    @staticmethod
    def load(file: TextIOWrapper):
        return json.load(file)

    @staticmethod
    def dump(data, file: TextIOWrapper):
        return json.dump(data, file, ensure_ascii=False)


    def check_cache_exists(self):
        if not path.isdir(path.join("./.cache/", self.name)):
            logging.debug(f"Creating cache {path.join('./.cache/', self.name)}")
            makedirs(path.join("./.cache/", self.name))

    def get_cache_filename(self, cache_key: str) -> str:
        return path.join("./.cache/", self.name, f"{mkmd5(cache_key)}.cache")

    def get(self, key) -> Any | None:
        cache_filename = self.get_cache_filename(key)
        if not path.exists(cache_filename):
            return None
        logging.debug(f"{self.name.upper()}: loading {cache_filename}")
        with open(cache_filename, f'r{"b" if self.binary_format else ""}') as file:
            try:
                return self.load(file) #type: ignore
            except:
                return None

    def set(self, key, data):
        self.check_cache_exists()
        cache_filename = self.get_cache_filename(key)
        logging.debug(f"{self.name.upper()}: saving {cache_filename}")
        with open(cache_filename, f'w{"b" if self.binary_format else ""}') as file:
            self.dump(data, file) #type: ignore
            
    
class AudioCache(Cache):
    binary_format = True
    @staticmethod
    def load(file):
        return tuple(pickle.load(file)) #type: ignore
    
    @staticmethod
    def dump(data, file):
        pickle.dump(data, file) #type: ignore
