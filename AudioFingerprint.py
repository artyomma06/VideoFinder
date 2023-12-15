import os
import librosa
import numpy as np
import scipy as sp

magnitude_threshold = 0.9  # Amplitude threshold
chunk_length = 1 / 30  # Number of seconds
fft_size = 16

# Load audio file and return data along with the sampling rate
def load_audio_file(file_path):
    data, sampling_rate = librosa.load(file_path, sr=None)
    audio_data = (data, sampling_rate)
    return audio_data

# Segment audio into chunks based on specified chunk length
def segment_audio_chunks(audio_data):
    data = audio_data[0]
    sampling_rate = audio_data[1]
    samples_per_chunk = int(sampling_rate * chunk_length)
    num_chunks = len(data) // samples_per_chunk
    chunks = [data[i * samples_per_chunk:(i + 1) * samples_per_chunk] for i in range(num_chunks)]
    audio_chunks = (chunks, sampling_rate)
    return audio_chunks

# Extract fingerprint from an audio chunk using FFT and quantization
def get_fingerprint(audio_chunk):
    frequencies = sp.fft.fft(audio_chunk, fft_size)
    phase = np.angle(frequencies)
    phase_normalized = (phase + np.pi) / (2 * np.pi)
    phase_quantized = quantize_fingerprint(phase_normalized)
    return phase_quantized

# Quantize the phase values for fingerprint
def quantize_fingerprint(phase_normalized):
    phase_quantized = []
    phase_hexed = ""
    for i in range(0, len(phase_normalized)):
        temp = round(phase_normalized[i] * 15)
        phase_quantized.append(temp)
        temp_hexed = hex(temp)
        phase_hexed += temp_hexed[2:]
    return phase_hexed

# Process the entire audio file and return a list of fingerprints
def process_file(file_path):
    audio_file = load_audio_file(file_path)
    audio_chunks = segment_audio_chunks(audio_file)
    fingerprint = []
    for i in range(0, len(audio_chunks[0])):
        fingerprint.append(get_fingerprint(audio_chunks[0][i]))
    return fingerprint

# Process a specific chunk of the audio file and return its fingerprint
def process_first(file_path, chunk_num):
    audio_file = load_audio_file(file_path)
    audio_chunk = segment_audio_chunks(audio_file)[0][chunk_num]
    fingerprint = get_fingerprint(audio_chunk)
    return fingerprint
