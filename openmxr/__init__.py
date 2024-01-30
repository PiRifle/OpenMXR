from spotdl import Spotdl
from spotdl.utils.config import DEFAULT_CONFIG
from spotdl.download.downloader import Downloader
from yt_dlp import YoutubeDL

sp_client = Spotdl(
    client_id=DEFAULT_CONFIG["client_id"],
    client_secret=DEFAULT_CONFIG["client_secret"],
    user_auth=DEFAULT_CONFIG["user_auth"],
    cache_path=DEFAULT_CONFIG["cache_path"],
    no_cache=True,
    headless=True,
)

yt_client = Downloader(settings={"simple_tui": True})
dl_client = YoutubeDL({'format': 'bestaudio/best'})