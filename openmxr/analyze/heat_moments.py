from openmxr.song import Song


def get_heat_moments(song: Song):
    pass

def has_heatmap(song: Song) -> list[int]:
    return song.youtube_meta.get("heatmap", None) and True

def from_heatmap(song: Song):
    if not song.youtube_meta.get("heatmap"):
        raise Exception("heatmap not available")
    items = sorted(song.youtube_meta["heatmap"], reverse=True, key=lambda x:x["value"])[:3]
    return [int(i["start_time"] * song.sample_rate+i["end_time"] * song.sample_rate)//2 for i in items]
    
def from_spotify(song: Song) -> list[int]:
    pass