import os
import logging
import requests
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

# 1. Carrega o arquivo .env
load_dotenv()

# 2. Configuração de Logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# 3. DEFINE a variável (A ordem aqui é o que causou o erro anterior)
FLOWISE_API_URL = os.getenv("FLOWISE_API_URL")

# 4. TESTE DE DEBUG (Agora o Python já sabe quem é a FLOWISE_API_URL)
print(f"\n--- TESTE DE CONEXÃO ---")
if FLOWISE_API_URL:
    print(f"URL CARREGADA COM SUCESSO: {FLOWISE_API_URL[:30]}...")
else:
    print("ERRO: A URL NÃO FOI ENCONTRADA NO ARQUIVO .ENV!")
print(f"------------------------\n")

def query_flowise(payload):
    try:
        if not FLOWISE_API_URL:
            return {"error": "Configuração da URL ausente."}
        
        response = requests.post(FLOWISE_API_URL, json=payload, timeout=30)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        logger.error(f"Erro na conexão com Flowise: {e}")
        return {"error": str(e)}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    data = request.json
    user_message = data.get("message")
    
    if not user_message:
        return jsonify({"answer": "Por favor, digite algo."}), 400

    result = query_flowise({"question": user_message})

    # Tratamento da resposta para garantir que o texto apareça no chat
    if isinstance(result, dict):
        answer = result.get("text") or result.get("json") or result.get("error") or "Sem resposta da IA."
    else:
        answer = "Erro no formato da resposta."

    return jsonify({"answer": answer})

if __name__ == '__main__':
    app.run(debug=True, port=5001)