from io import BytesIO, TextIOWrapper
import io
import json
import logging
from os import makedirs, path
import os
from random import sample
from typing import IO
import numpy as np
import soundfile as sf
from pyparsing import Any
from bz2 import BZ2Compressor, BZ2Decompressor
from madmom.io.audio import load_wave_file, write_wave_file, Signal
from tqdm.notebook import tqdm

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
    compressor = BZ2Compressor()
    decompressor = BZ2Decompressor()
    binary_format = True

    def load(self, file: IO[Any]):
        logging.debug(f"{self.name.upper()}: decompressing {file.name}")
        buffer = io.BytesIO()
        buffer.name = "audio.wav"
        file.seek(0, os.SEEK_END)
        size = file.tell()
        file.seek(0)
        progress_bar = tqdm(total=size, unit='B', unit_scale=True, desc='Decompressing')
        while True:
                chunk = file.read(16384)
                if not chunk:
                    progress_bar.close()
                    break
                progress_bar.update(len(chunk))
                buffer.write(self.decompressor.decompress(chunk))
        logging.debug(f"{self.name.upper()}: converting {file.name}")
        buffer.seek(0)
        y, sr = sf.read(buffer)
        return (sr, np.transpose(y))
    
    def dump(self, data, file):
        uncompressed = io.BytesIO()
        uncompressed.name = "audio.wav"
        logging.debug(f"{self.name.upper()}: converting {file.name}")
        write_wave_file(Signal(data=np.transpose(data[1]), sample_rate=48000), uncompressed, 48000)
        logging.debug(f"{self.name.upper()}: compressing {file.name}")
        size = len(uncompressed.getvalue())
        progress_bar = tqdm(total=size, unit='B', unit_scale=True, desc='Compressing')
        while True:
            chunk = uncompressed.read(16384)
            if not chunk:
                progress_bar.close()
                break
            progress_bar.update(len(chunk))
            file.write(self.compressor.compress(chunk))