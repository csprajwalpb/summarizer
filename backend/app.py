from flask import Flask,request,jsonify
from flask_cors import CORS
import os
import fitz
from dotenv import load_dotenv
from openai import OpenAI
from youtube_transcript_api import YouTubeTranscriptApi

load_dotenv()
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

app = Flask(__name__)
CORS(app, origin="http://localhost:3000")

def get_summary(prompt):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant that summarizes content."},
            {"role": "user", "content": prompt}
        ],
        max_tokens=150,
        temperature=0.7
    )
    return response.choices[0].message.content.strip()

@app.route('/summarize/text', methods=['POST'])
def summarize_text():
    data = request.get_json()
    text = data.get('text')
    if not text:
        return jsonify({"error": "No text provided"}), 400
    prompt = f"Summarize the following text:\n\n{text}"
    summary = get_summary(prompt)
    return jsonify({"summary": summary})


@app.route('/summarize/pdf', methods=['POST'])
def summarize_pdf():
    if 'file' not in request.files:
        return jsonify({"error": "No file uploaded"}), 400
    file = request.files['file']
    doc = fitz.open(stream=file.read(), filetype="pdf")
    text = ""
    for page in doc:
        text += page.get_text()
    prompt = f"Summarize the following PDF content:\n\n{text}"
    summary = get_summary(prompt)
    return jsonify({"summary": summary})

@app.route('/summarize/youtube', methods=['POST'])
def summarize_youtube():
    data = request.get_json()
    url = data.get('url')
    if not url:
        return jsonify({"error": "No video URL provided"}), 400
    video_id = url.split("v=")[-1]
    try:
        transcript = YouTubeTranscriptApi.get_transcript(video_id)
        text = " ".join([entry['text'] for entry in transcript])
        prompt = f"Summarize the following YouTube video transcript:\n\n{text}"
        summary = get_summary(prompt)
        return jsonify({"summary": summary})
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)