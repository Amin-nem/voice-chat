import api_keys
from elevenlabs import stream, generate
from openai import OpenAI
from whisperlive import transcribe_real_time


class AIAssistant:
    def __init__(self) -> None:
        self.openai_client = OpenAI(api_key=api_keys.openai())
        self.elevenlabs_api_key = api_keys.eleven()

        self.transcriber = None

        # initiates with the openai prompt
        self.full_transcript = [
            {'role': 'system', 'content': 'You are a friendly language partner who helps the ESL students become more fluent in English speaking. Be resourcefull, try to simplify you speech so that the student can understand you better.'},
        ]

# real-time transcription
    def start_transcription(self):
        transcript_text = transcribe_real_time(
            audio_length=10, model_name="base")
        if transcript_text:
            self.generate_ai_response(transcript_text)
        else:
            print("No audio detected. Please try speaking again.")


# generate ai response

    def generate_ai_response(self, transcript):
        self.full_transcript.append(
            {'role': 'user', 'content': transcript})
        print(f'\nYou:{transcript}', end='\r\n')
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
