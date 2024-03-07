import api_keys
import assemblyai as aai
from elevenlabs import stream, generate
from openai import OpenAI


class AIAssistant:
    def __init__(self) -> None:
        aai.settings.api_key = api_keys.assemblyai()
        self.openai_client = OpenAI(api_key=api_keys.openai())
        self.elevenlabs_api_key = api_keys.eleven()

        self.transcriber = None

        # initiates with the openai prompt
        self.full_transcript = [
            {'role': 'system', 'content': 'You are a friendly language partner who helps the ESL students become more fluent in English speaking. Be resourcefull, try to simplify you speech so that the student can understand you better.'},
        ]

# real-time transcription
    def start_transcription(self):
        self.transcriber = aai.RealtimeTranscriber(sample_rate=16000,
                                                   on_data=self.on_data,
                                                   on_error=self.on_error,
                                                   on_open=self.on_open,
                                                   on_close=self.on_close,
                                                   end_utterance_silence_threshold=1000)
        self.transcriber.connect()
        microphone_stream = aai.extras.MicrophoneStream(sample_rate=16000)
        self.transcriber.stream(microphone_stream)

    def stop_transcription(self):
        if self.transcriber:
            self.transcriber.close()
            self.transcriber = None

    def on_open(self, session_opened: aai.RealtimeSessionOpened):
        print("Session ID:", session_opened.session_id)
        return

    def on_data(self, transcript: aai.RealtimeTranscript):
        if not transcript.text:
            return

        if isinstance(transcript, aai.RealtimeFinalTranscript):
            self.generate_ai_response(transcript)
        else:
            print(transcript.text, end="\r")

    def on_error(self, error: aai.RealtimeError):
        print("An error occured:", error)
        return

    def on_close(self):
        print("Closing Session")
        return

# generate ai response
    def generate_ai_response(self, transcript):
        self.stop_transcription()
        self.full_transcript.append(
            {'role': 'user', 'content': transcript.text})
        print(f'\nYou:{transcript.text}', end='\r\n')
        response = self.openai_client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=self.full_transcript
        )
        ai_response = response.choices[0].message.content

        self.generate_audio(ai_response)
        self.start_transcription()
# generate audio

    def generate_audio(self, text):
        self.full_transcript.append({'role': 'assistant', 'content': text})
        print(f'\nAI:{text}')
        audio_stream = generate(
            api_key=self.elevenlabs_api_key,
            text=text,
            voice='Chris',
            stream=True)
        stream(audio_stream)


greeting = 'Hey! How\'s it going? I\'m gonna help you improve your English fluency. Are you ready?'
ai_assistant = AIAssistant()
ai_assistant.generate_audio(greeting)
ai_assistant.start_transcription()
