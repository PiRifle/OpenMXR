from dataclasses import dataclass
from typing import Any
from spotdl.utils.spotify import SpotifyClient
from openmxr.cache import Cache

from openmxr.song import Song


@dataclass
class TrackAnalysisMeta:
    num_samples: int
    duration: float
    sample_md5: str
    offset_seconds: float
    window_seconds: float
    analysis_sample_rate: int
    analysis_channels: int
    end_of_fade_in: float
    start_of_fade_out: float
    loudness: float
    tempo: float
    tempo_confidence: float
    time_signature: int
    time_signature_confidence: float
    key: int
    key_confidence: float
    mode: float
    mode_confidence: float
    codestring: str
    code_version: float
    echoprintstring: str
    echoprint_version: float
    synchstring: str
    synch_version: float
    rhythmstring: str
    rhythm_version: float
    
      
@dataclass
class BaseSection:
    start: float
    duration: float
    confidence: float    
    
    def get_section_snippet(self, sr):
        return sr * self.start, sr * (self.start + self.duration)

@dataclass
class Bar(BaseSection):
    pass

@dataclass
class Beat(BaseSection):
    pass

@dataclass
class Section(BaseSection):
    loudness: float
    tempo: float
    tempo_confidence: float
    key: int
    key_confidence: float
    mode: int
    mode_confidence: float
    time_signature: float
    time_signature_confidence: float

@dataclass
class Segment(BaseSection):
    loudness_start: float
    loudness_max: float
    loudness_max_time: float
    loudness_end: float
    pitches: list[float]
    timbre: list[float]

@dataclass
class Tatum(BaseSection):
    pass


class SpotifyAnalysis:
    spotify_api = SpotifyClient()
    track: Song
    track_id: str
    cache = Cache("spotify_analysis")
    __audio_analysis: dict[str, Any]

    def __init__(self, track: Song):
        self.cache.check_cache_exists()
        self.track = track
        if not track.spotify_meta:
            raise Exception("No spotify meta found")
        self.track_id = track.spotify_meta["song_id"]

        if (data := self.cache.get(self.track_id)):
            self.__audio_analysis = data
        else:
            self.__audio_analysis = self.spotify_api.audio_analysis(self.track_id)
            self.cache.set(self.track_id, self.__audio_analysis)
    
    @property
    def info(self):
        return TrackAnalysisMeta(**self.__audio_analysis["track"])

    @property
    def bars(self):
        return [Bar(**item) for item in self.__audio_analysis["bars"]]
    
    @property
    def beats(self):
        return [Beat(**item) for item in self.__audio_analysis["beats"]]
    
    @property
    def sections(self):
        return [Section(**item) for item in self.__audio_analysis["sections"]]
    
    @property
    def segments(self):
        return [Segment(**item) for item in self.__audio_analysis["segments"]]
    
    @property
    def tatums(self):
        return [Tatum(**item) for item in self.__audio_analysis["tatums"]]

def get_loudest(items: list[Section]):
    return sorted(items, key=lambda x:x.loudness, reverse=True)[0]
