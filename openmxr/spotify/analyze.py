from dataclasses import dataclass
from spotdl.utils.spotify import SpotifyClient
from openmxr.cache import Cache

from openmxr.song import Song

class SpotifyAnalysis:
    spotify_api = SpotifyClient()
    track: Song
    cache = Cache("spotify_analisys")
    
    def __init__(self, track: Song):
        self.track = track
        
    
    # @property
    # info(self):
    #     return 
    # spotify_api.audio_analysis()
    
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
