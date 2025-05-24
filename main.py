# main.py  – Flask server & chat endpoints

import os
import time
import traceback

from dotenv import load_dotenv
from flask import Flask, request, jsonify, make_response
from flask_cors import CORS
from openai import OpenAI

import functions  # ← loads and returns assistant_id

# ── Load .env if present (makes local dev easy) ─────────────────────────
load_dotenv()

client = OpenAI(
    api_key=os.getenv("OPENAI_API_KEY"),
    default_headers={"OpenAI-Beta": "assistants=v2"},
)
assistant_id = functions.assistant_id  # persistent ID from functions.py

app = Flask(__name__)
CORS(app)

@app.after_request
def cors(response):
    response.headers["Access-Control-Allow-Origin"]  = "*"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    response.headers["Access-Control-Allow-Methods"] = "GET,POST,OPTIONS"
    return response

@app.route("/start", methods=["GET", "OPTIONS"])
def start():
    if request.method == "OPTIONS":
        return make_response(("", 204))
    thread = client.beta.threads.create()
    return jsonify({"thread_id": thread.id})

@app.route("/chat", methods=["POST", "OPTIONS"])
def chat():
    if request.method == "OPTIONS":
        return make_response(("", 204))
    try:
        data = request.get_json() or {}
        tid = data.get("thread_id")
        txt = (data.get("message") or "").strip()
        if not tid or not txt:
            return jsonify({"response": "⚠️ Missing thread_id or message."}), 400

        # 1) append user
        client.beta.threads.messages.create(thread_id=tid, role="user", content=txt)

        # 2) run assistant
        run = client.beta.threads.runs.create(thread_id=tid, assistant_id=assistant_id)

        # 3) wait for completion
        while True:
            status = client.beta.threads.runs.retrieve(thread_id=tid, run_id=run.id).status
            if status == "completed":
                break
            time.sleep(1)

        # 4) fetch assistant reply
        messages = client.beta.threads.messages.list(thread_id=tid, limit=1).data
        answer = messages[0].content[0].text.value
        return jsonify({"response": answer})

    except Exception as e:
        traceback.print_exc()
        return jsonify({"response": f"⚠️ {type(e).__name__}: {e}"}), 500

if __name__ == "__main__":
    port = int(os.getenv("PORT", 8080))
    app.run(host="0.0.0.0", port=port)
