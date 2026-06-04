from flask import Flask, render_template, request, jsonify
import speech_recognition as sr
from textblob import TextBlob
from transformers import pipeline
import os
from pydub import AudioSegment

# Flask app
app = Flask(__name__)

# Recording folder
RECORD_FOLDER = "recordings"

if not os.path.exists(RECORD_FOLDER):
    os.makedirs(RECORD_FOLDER)

# Emotion Detection Model
emotion_pipeline = pipeline(
    "text-classification",
    model="j-hartmann/emotion-english-distilroberta-base",
    top_k=1
)

# Home page
@app.route("/")
def home():
    return render_template("index.html")

# Analyze route
@app.route("/analyze", methods=["POST"])
def analyze():

    if "audio" not in request.files:
        return jsonify({"error": "No audio found"})

    audio = request.files["audio"]

    webm_path = os.path.join(RECORD_FOLDER, "recording.webm")
    wav_path = os.path.join(RECORD_FOLDER, "recording.wav")

    # Save webm
    audio.save(webm_path)

    # Convert webm to wav
    sound = AudioSegment.from_file(webm_path)
    sound.export(wav_path, format="wav")

    recognizer = sr.Recognizer()

    try:
        with sr.AudioFile(wav_path) as source:
            audio_data = recognizer.record(source)

        # Speech to text
        text = recognizer.recognize_google(audio_data)

    except Exception as e:
        return jsonify({"error": str(e)})

    # Emotion Analysis
    emotion = emotion_pipeline(text)[0][0]["label"]

    # Sentiment
    sentiment = TextBlob(text).sentiment.polarity

    # Tone
    if sentiment > 0:
        tone = "Positive"
    elif sentiment < 0:
        tone = "Negative"
    else:
        tone = "Neutral"

    # Confidence & Stress
    confidence = "High"
    stress = "Low"

    if emotion.lower() in ["anger", "fear", "sadness"]:
        confidence = "Medium"
        stress = "High"

    # Feedback
    if tone == "Positive":
        feedback = "Excellent speaking tone and confidence."
    elif tone == "Negative":
        feedback = "Try to remain calm and speak positively."
    else:
        feedback = "Your speaking tone is balanced."

    return jsonify({
        "speech": text,
        "emotion": emotion,
        "tone": tone,
        "confidence": confidence,
        "stress": stress,
        "feedback": feedback
    })

# Run app
if __name__ == "__main__":
    app.run(debug=True)