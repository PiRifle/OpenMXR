from dataclasses import dataclass
from io import BytesIO, TextIOWrapper
import librosa
import numpy as np
import numpy.typing as npt
import requests
from pyparsing import Any
import logging
import soundfile
from openmxr.cache import AudioCache, Cache
from openmxr.convert import convert_opus_to_wav
from openmxr.downloader.DownloadTask import DownloadTask
from openmxr import sp_client, dl_client, yt_client
from scipy.signal import resample


class Song():
    yt_link: str
    spotify_link: str
    _audio_cache: tuple[int, npt.NDArray] | None = None
    _spotify_cache: dict[str, Any] | None = None
    _yt_cache: dict[str, Any] | None = None
    
    __yt_cache_instance = Cache("yt")
    __spotify_cache_instance = Cache("spotify")
    __audio_cache_instance = AudioCache("audio")
    
    @property
    def audio(self):
        if (not self._audio_cache):
            raise Exception("audio not available")
        return self._audio_cache[1]
    
    @property
    def audio_mono(self):
        if (not self._audio_cache):
            raise Exception("audio not available")
        return self.to_mono(self._audio_cache[1])
    
    def to_mono(self, audio):
        return librosa.to_mono(audio)
    
    @property
    def sample_rate(self):
        if (not self._audio_cache) or self._audio_cache[0] == None:
            raise Exception("sample_rate not available")
        return self._audio_cache[0]
        
        
    @property
    def youtube_meta(self):
        if not self._yt_cache:
            raise Exception("youtube metadata not available")
        return self._yt_cache
        
    @property
    def spotify_meta(self):
        if not self._spotify_cache:
            raise Exception("spotify metadata not available")
        return self._spotify_cache
    
    def resampled(self, new_sample_rate, mono=False):
        if mono:
            audio = self.audio_mono
        else:
            audio = self.audio
        if len(audio.shape) > 1:
            return np.array([resample(channel, (len(channel)//self.sample_rate)*new_sample_rate) for channel in audio])
        return resample(audio, (len(self.audio_mono)//self.sample_rate)*new_sample_rate)
    
    
    def __init__(self, yt_url, spotify_url):
        self.yt_link = yt_url
        self.spotify_link = spotify_url
        
        if not self._yt_cache:
            if (cached := self.__yt_cache_instance.get(self.yt_link)):
                self._yt_cache = cached
            else:
                self._yt_cache = self._download_yt_meta()
                self.__yt_cache_instance.set(self.yt_link, self._yt_cache)
        if not self._spotify_cache:
            if (cached := self.__spotify_cache_instance.get(self.yt_link)):
                self._spotify_cache = cached
            else:
                self._spotify_cache = self._download_spotify_meta()
                self.__spotify_cache_instance.set(self.yt_link, self._spotify_cache)

        if not self._audio_cache:
            if (cached := self.__audio_cache_instance.get(self.yt_link)):
                self._audio_cache = cached
            else:
                self._audio_cache = self._download_audio()
                self.__audio_cache_instance.set(self.yt_link, self._audio_cache)

        logging.info(f"loaded {self._spotify_cache['name']}")

    @staticmethod
    def _check_link_valid(url: str):
        req = requests.head(url)
        return req.status_code < 400
            
    
    @classmethod
    def find(cls, spotify_link = None, youtube_link = None, query = None):
        if spotify_link and youtube_link:
            logging.info("Loading custom song config")
            return cls(spotify_link, youtube_link)
        if spotify_link:
            logging.info("Loading from spotify")
            return cls.from_spotify_link(spotify_link)
        if youtube_link:
            logging.info("Loading from youtube")
            return cls.from_yt_link(youtube_link)
        if query:
            logging.info(f"Searching {query}")
            return cls.from_search(query)
    
    @classmethod
    def from_spotify_link(cls, spotify_link: str):
        if (_cache_spotify := cls.__spotify_cache_instance.get(spotify_link)):
            cls._spotify_cache = _cache_spotify
            return cls(_cache_spotify["download_url"], _cache_spotify["url"])

        spotify_song = sp_client.search([spotify_link])[0]
        yt_url = yt_client.search(spotify_song)
        spotify_song.download_url = yt_url
        cls._spotify_cache = spotify_song.json
        cls.__spotify_cache_instance.set(spotify_song.url, spotify_song.json)
        return cls(yt_url, spotify_song.url)
    
    @classmethod
    def from_yt_link(cls, youtube_link: str):
        if (_cache_yt := cls.__yt_cache_instance.get(youtube_link)):    
            cls._yt_cache = _cache_yt
            return cls(_cache_yt["url"], _cache_yt["CUSTOM__spotify_url"])
        
        yt_song = dl_client.extract_info(youtube_link, download=False)
        cls._yt_cache = yt_song
        
        if yt_song:
            title = f"{yt_song.get('artist', '')} {yt_song.get('track', yt_song['fulltitle'])}"
            spotify_song = sp_client.search([title])[0]
            cls._spotify_cache = spotify_song.json
            spotify_song.download_url = youtube_link
            yt_song["CUSTOM__spotify_url"] = spotify_song.url
            cls.__spotify_cache_instance.set(spotify_song.url, spotify_song.json)
            cls.__yt_cache_instance.set(youtube_link, yt_song)
            return cls(youtube_link, spotify_song.url)
        raise Exception("this url is not valid")
    
    @classmethod
    def from_search(cls, query: str):
        return cls.from_spotify_link(query) # dirty way to search for song
    
    def _download_audio(self) -> tuple[int, npt.NDArray]:
        if not self._yt_cache:
            raise Exception("youtube cache not initialized")
                    
        audio_url = self._yt_cache["url"]
        if not self._check_link_valid(audio_url):
            self._yt_cache = self._download_yt_meta()
            self.__yt_cache_instance.set(self.yt_link, self._yt_cache)
            audio_url = self._yt_cache["url"]
        
        logging.info(f"Downloading {self._yt_cache['fulltitle']}")
        buffer = DownloadTask(audio_url).start()
        logging.info(f"Downloaded {self._yt_cache['fulltitle']}")
        
        logging.info(f"Converting {self._yt_cache['fulltitle']}")
        buffer = convert_opus_to_wav(buffer)
        logging.info(f"Converted {self._yt_cache['fulltitle']}")
        y, sr = soundfile.read(BytesIO(buffer))
        return (sr, np.transpose(y))
    
    def _download_spotify_meta(self) -> dict[str, Any]:
        spotify_song = sp_client.search([self.spotify_link])[0]
        return spotify_song.json
    
    def _download_yt_meta(self) -> dict[str, Any]:
        yt_song = dl_client.extract_info(self.yt_link, download=False)
        if yt_song:
            return yt_song
        raise Exception("this url is not valid")
    
    # def analyze(self) -> AnalyzedTrack:
    #     return AnalyzedTrack() 
    
# logging.basicConfig(level=logging.INFO)
