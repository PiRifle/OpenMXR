from dataclasses import dataclass


@dataclass
class Metadata:
    title: str
    artist: str | None
    cover: str | None
    album: str | None
    year: str | None
    genre: str | None

