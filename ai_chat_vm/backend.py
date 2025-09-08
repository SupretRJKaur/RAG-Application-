from flask import Flask, request, jsonify, send_file
from flask_cors import CORS
import google.generativeai as genai
import markdown
import chromadb
from sentence_transformers import SentenceTransformer
import os

app = Flask(__name__)
CORS(app)


genai.configure() 


text_model = genai.GenerativeModel("models/gemini-1.5-flash")
image_model = genai.GenerativeModel("models/gemini-image-1.0")


chroma_client = chromadb.PersistentClient(path="./rag_db")
collection = chroma_client.get_collection("pdf_chunks")

embedding_model = SentenceTransformer("all-MiniLM-L6-v2")

def retrieve_context(query, top_k=3):
    query_emb = embedding_model.encode(query).tolist()
    results = collection.query(query_embeddings=[query_emb], n_results=top_k)
    if not results["documents"] or not results["documents"][0]:
        return "No matching context found."
    return "\n".join(results["documents"][0])


@app.route('/')
def serve_index():
    return send_file('index.html')

@app.route('/style.css')
def serve_css():
    return send_file('style.css')

@app.route('/scripts.js')
def serve_js():
    return send_file('scripts.js')

@app.route('/bg.jpg')
def serve_bg():
    return send_file('bg.jpg')

@app.route('/chat', methods=['POST'])
def chat():
    try:
        user_input = request.json.get('message', '')
        print(f"📨 User asked: {user_input}")

        if any(word in user_input.lower() for word in ["image", "picture", "draw", "show me"]):
            img_response = image_model.generate_content(prompt=user_input)
            img_url = getattr(img_response, "image_url", None)
            return jsonify({"image": img_url, "reply": "Here's the image you requested!"})

      
        context = retrieve_context(user_input)
        prompt = f"""
        You are a helpful AI assistant. Use the following context (if relevant) to answer clearly:

        Context:
        {context}

        Question: {user_input}
        """
        response = text_model.generate_content(prompt)
        reply_markdown = getattr(response, "text", "⚠️ Gemini returned no reply.")
        reply_html = markdown.markdown(reply_markdown)

        print(f"✅ Gemini replied (HTML): {reply_html}")
        return jsonify({"reply": reply_html})

    except Exception as e:
        print(f"❌ Error: {e}")
        return jsonify({"reply": f"⚠️ Gemini failed: {e}"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
