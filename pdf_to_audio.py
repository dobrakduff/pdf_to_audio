from gtts import gTTS

def pdf_to_audio(text, output_file):
    tts = gTTS(text=text, lang='en')  # Change 'en' to your desired language code if different
    tts.save(output_file)
