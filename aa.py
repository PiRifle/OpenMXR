# %%
import logging
logging.basicConfig(level=logging.DEBUG)
from openmxr.song import Song

song = Song.find(spotify_link="https://open.spotify.com/track/2ZhZ76JnLYcjFmcExTdxNF")

# %%
from openmxr.spotify.analyze import SpotifyAnalysis, get_loudest


a = SpotifyAnalysis(song)
# print(a.sections)
print(get_loudest(a.sections))

# %% [markdown]
# 

# %%
import librosa
import numpy as np
from pychorus.constants import N_FFT
from pychorus.similarity_matrix import TimeTimeSimilarityMatrix, TimeLagSimilarityMatrix

def create_chroma(y, sr, n_fft=N_FFT):
    """
    Generate the notes present in a song

    Returns: tuple of 12 x n chroma, song wav data, sample rate (usually 22050)
             and the song length in seconds
    """
    
    song_length_sec = y.shape[0] / float(sr)
    S = np.abs(librosa.stft(y, n_fft=n_fft))**2
    chroma = librosa.feature.chroma_stft(S=S, sr=sr)

    return chroma, y, sr, song_length_sec

chroma, _, sr, _ = create_chroma(song.audio_mono, song.sample_rate)
time_time_similarity = TimeTimeSimilarityMatrix(chroma, sr)
time_lag_similarity = TimeLagSimilarityMatrix(chroma, sr)
num_samples = chroma.shape[1]

# Visualize the results
# print(time_lag_similarity.display())
# time_time_similarity.display()

# %%
from pychorus.helpers import local_maxima_rows, detect_lines, SMOOTHING_SIZE_SEC
smoothing_size_samples = int(SMOOTHING_SIZE_SEC * sr)
time_lag_similarity.denoise(time_time_similarity.matrix,
                            smoothing_size_samples)



# %%
# Detect lines in the image
clip_length_samples = len(song.audio_mono)
candidate_rows = local_maxima_rows(time_lag_similarity.matrix)


# %%
lines = detect_lines(time_lag_similarity.matrix, candidate_rows,
                        clip_length_samples)

# %%
from json import JSONEncoder

class NumpyArrayEncoder(JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return JSONEncoder.default(self, obj)


# %%
import json
with open("file.json", "w") as f:
    json.dump(time_time_similarity.matrix, f, cls=NumpyArrayEncoder)


# %%
N_FFT

# %%
from matplotlib import pyplot as plt
plt.cla()

# %%
# %matplotlib ipympl
from matplotlib import pyplot as plt

def normalize_2d_array(arr):
    min_val = np.min(arr)
    max_val = np.max(arr)

    normalized_arr = (arr - min_val) / (max_val - min_val)

    return normalized_arr

# plt.imshow(normalize_2d_array(time_time_similarity.matrix), vmin=0, vmax=1)
# plt.colorbar()
# plt.title('Grayscale Image')
# plt.show()
# plt.savefig('imshow_plot_2K.png', dpi=200)



