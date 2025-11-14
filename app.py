# app_simple.py - Versión simplificada sin sentence-transformers
import os
from flask import Flask, render_template, request, jsonify
import pdfplumber
import re
from dotenv import load_dotenv

# Importar Google Generative AI
try:
    import google.generativeai as genai
    GOOGLE_AI_AVAILABLE = True
except ImportError:
    genai = None
    GOOGLE_AI_AVAILABLE = False

load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")

PDF_PATH = "mnt/data/Formulario_210_2025.pdf"

app = Flask(__name__)

# cargar y fragmentar PDF en memoria
def load_and_chunk_pdf(path, chunk_size=800):
    texts = []
    with pdfplumber.open(path) as pdf:
        for page in pdf.pages:
            text = page.extract_text() or ""
            # simple split por párrafos/líneas y luego por tamaño
            parts = []
            for p in text.split("\n\n"):
                p = p.strip()
                if not p: 
                    continue
                # fragmenta en trozos no muy largos
                i = 0
                while i < len(p):
                    parts.append(p[i:i+chunk_size])
                    i += chunk_size
            texts.extend(parts)
    return texts

print("Cargando PDF...")
chunks = load_and_chunk_pdf(PDF_PATH)
print(f"PDF cargado con {len(chunks)} fragmentos.")

# endpoint web
@app.route("/")
def index_page():
    return render_template("index.html")

def search_by_keywords(query, k=4):
    """Búsqueda simple por palabras clave"""
    query_words = query.lower().split()
    scored_chunks = []
    
    for chunk in chunks:
        chunk_lower = chunk.lower()
        score = 0
        
        # contar coincidencias de palabras del query
        for word in query_words:
            if word in chunk_lower:
                score += chunk_lower.count(word)
        
        if score > 0:
            scored_chunks.append((score, chunk))
    
    # ordenar por relevancia y tomar los mejores
    scored_chunks.sort(key=lambda x: x[0], reverse=True)
    return [chunk for score, chunk in scored_chunks[:k]]

def generate_answer_with_gemini(question, context_chunks):
    if not GOOGLE_AI_AVAILABLE or not GOOGLE_API_KEY:
        return "Fragmentos relevantes del Formulario 210:\n\n" + "\n\n---\n\n".join(context_chunks[:4])
    
    # concatenar contexto (acotar tamaño)
    context = "\n\n".join(context_chunks)
    prompt = f"Eres un asistente tributario experto. El usuario pregunta: {question}\n\nUsa SOLO la información del contexto para responder. CONTEXTO:\n{context}\n\nRespuesta clara y breve:"
    
    try:
        # configurar la API de Google
        genai.configure(api_key=GOOGLE_API_KEY)
        
        # crear el modelo (usar gemini-2.0-flash que es eficiente y rápido)
        model = genai.GenerativeModel('gemini-2.0-flash')
        
        # generar la respuesta
        response = model.generate_content(prompt)
        return response.text.strip()
        
    except Exception as e:
        print(f"Error con Gemini AI: {e}")
        # fallback si hay error con la API
        return "Fragmentos relevantes del Formulario 210:\n\n" + "\n\n---\n\n".join(context_chunks[:4]) + f"\n\n(Nota: Error con API de Google Gemini: {str(e)})"

@app.route("/ask", methods=["POST"])
def ask():
    data = request.json
    q = data.get("question","").strip()
    if not q:
        return jsonify({"error":"Pregunta vacía"}), 400
    
    sims = search_by_keywords(q, k=6)
    
    if GOOGLE_AI_AVAILABLE and GOOGLE_API_KEY:
        answer = generate_answer_with_gemini(q, sims)
    else:
        # fallback: devolver los fragmentos relevantes concatenados (sin modelo)
        answer = "Fragmentos relevantes del Formulario 210:\n\n" + "\n\n---\n\n".join(sims[:4])
        if not GOOGLE_AI_AVAILABLE:
            answer += "\n\n(Para respuestas generadas con IA, instala google-generativeai: pip install google-generativeai)"
        elif GOOGLE_API_KEY is None:
            answer += "\n\n(Si quieres respuestas generadas, añade una GOOGLE_API_KEY en .env)"
    
    return jsonify({"answer": answer})

if __name__ == "__main__":
    app.run(debug=True, port=5000)