from dataclasses import dataclass
from openmxr.models.Metadata import Metadata
import numpy.typing as npt


@dataclass
class AnalyzedTrack:
    meta: Metadata
    sample_rate: int
    key: int
    waveform: npt.NDArray
    downbeats: list[int]
    best_downbeats: list[int]
    bpm: int  
