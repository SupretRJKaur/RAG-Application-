from flask import Flask, request, jsonify, send_from_directory
from flask_cors import CORS
import google.generativeai as genai
import markdown
import chromadb
import os

app = Flask(__name__, static_folder='.')
CORS(app)

# ---------------- GEMINI SETUP ----------------
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def get_working_model():
    for m in genai.list_models():
        if "generateContent" in m.supported_generation_methods:
            print(f"✅ Using model: {m.name}")
            return genai.GenerativeModel(m.name)

    raise Exception("No compatible model found.")

text_model = get_working_model()

# ---------------- CHROMADB SETUP ----------------
chroma_client = chromadb.PersistentClient(path="./rag_db")

try:
    collection = chroma_client.get_collection("pdf_chunks")
    print("✅ ChromaDB loaded")
except:
    collection = None
    print("⚠️ Run ragsetup.py first")

def retrieve_context(query, top_k=3):
    if not collection:
        return "No database found."

    results = collection.query(
        query_texts=[query],
        n_results=top_k
    )

    if not results["documents"] or not results["documents"][0]:
        return "No matching context found."

    return "\n".join(results["documents"][0])

# ---------------- FRONTEND ROUTES ----------------
@app.route('/')
def home():
    return send_from_directory('.', 'index.html')

@app.route('/<path:path>')
def static_files(path):
    return send_from_directory('.', path)

# ---------------- CHAT ROUTE ----------------
@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_input = request.json.get('message', '')

        print(f"📨 User: {user_input}")

        context = retrieve_context(user_input)

        prompt = f"""
You are a helpful AI assistant.

Use this context if relevant:
{context}

Question:
{user_input}
"""

        response = text_model.generate_content(prompt)

        reply = response.text if response.text else "⚠️ No response from Gemini."

        return jsonify({
            "reply": markdown.markdown(reply)
        })

    except Exception as e:
        print("❌ Error:", e)
        return jsonify({
            "reply": f"⚠️ Error: {str(e)}"
        })

# ---------------- RUN APP ----------------
if __name__ == "__main__":
    print("🚀 Server starting...")
    app.run(host="127.0.0.1", port=8080, debug=True)
