import whisper
import pyaudio
import wave
import warnings


def transcribe_real_time(audio_length=5, model_name="base"):
    """
    Captures audio from the microphone for a specified duration and returns the transcription.

    Parameters:
    - audio_length: Length of the audio capture in seconds. Default is 5 seconds.
    - model_name: Whisper model size to use for transcription. Default is 'base'.

    Returns:
    - Transcription text as a string.
    """
    warnings.filterwarnings(
        "ignore", message="FP16 is not supported on CPU; using FP32 instead")

    # Load the Whisper model
    model = whisper.load_model(model_name, device='cpu')

    # PyAudio configuration
    FORMAT = pyaudio.paInt16
    CHANNELS = 1
    RATE = 44100
    CHUNK = 1024
    WAVE_OUTPUT_FILENAME = "temp_audio_file.wav"

    audio = pyaudio.PyAudio()

    # Start streaming from microphone
    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True,
                        frames_per_buffer=CHUNK)
    print("Recording...")

    frames = []

    for i in range(0, int(RATE / CHUNK * audio_length)):
        data = stream.read(CHUNK)
        frames.append(data)

    print("Finished recording.")

    # Stop and close the stream
    stream.stop_stream()
    stream.close()
    audio.terminate()

    # Save the recorded data as a WAV file
    wf = wave.open(WAVE_OUTPUT_FILENAME, 'wb')
    wf.setnchannels(CHANNELS)
    wf.setsampwidth(audio.get_sample_size(FORMAT))
    wf.setframerate(RATE)
    wf.writeframes(b''.join(frames))
    wf.close()

    # Transcribe the audio file
    result = model.transcribe(WAVE_OUTPUT_FILENAME)

    # Optionally, clean up the temporary audio file here
    # os.remove(WAVE_OUTPUT_FILENAME)

    return result["text"]


# Example of using the function
if __name__ == "__main__":
    transcription = transcribe_real_time(audio_length=10, model_name="base")
    print("Transcription: ", transcription)
