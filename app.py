import os
import logging
import requests
from flask import Flask, render_template, request, jsonify
from dotenv import load_dotenv

# 1. Carrega as variáveis do arquivo .env
load_dotenv()

# 2. Configuração de Logs (Essencial para monitorar erros no Terminal)
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = Flask(__name__)

# 3. Definição da URL da API
FLOWISE_API_URL = os.getenv("FLOWISE_API_URL")

# Teste de inicialização para garantir que o .env foi lido
print("\n" + "="*30)
if FLOWISE_API_URL:
    print(f"✅ CONEXÃO CONFIGURADA: {FLOWISE_API_URL[:40]}...")
else:
    print("❌ ERRO: FLOWISE_API_URL não encontrada no arquivo .env")
print("="*30 + "\n")

def query_flowise(payload):
    """Envia a pergunta para a API do Flowise e trata a resposta."""
    try:
        if not FLOWISE_API_URL:
            return {"error": "URL da API não configurada corretamente."}
        
        response = requests.post(FLOWISE_API_URL, json=payload, timeout=120)
        
        # Log da resposta bruta para facilitar o debug no terminal
        logger.info(f"Status da Resposta: {response.status_code}")
        
        if response.status_code != 200:
            return {"error": f"Erro na API ({response.status_code}): {response.text}"}

        return response.json()
    except requests.exceptions.RequestException as e:
        logger.error(f"Erro de rede ao conectar com Flowise: {e}")
        return {"error": "Não foi possível conectar ao servidor de IA."}
    except Exception as e:
        logger.error(f"Erro inesperado: {e}")
        return {"error": "Ocorreu um erro interno no processamento."}

@app.route('/')
def index():
    """Renderiza a página inicial do Chat."""
    return render_template('index.html')

@app.route('/ask', methods=['POST'])
def ask():
    """Rota que recebe a mensagem do JavaScript e retorna a resposta da IA."""
    try:
        data = request.json
        user_message = data.get("message")
        
        if not user_message:
            return jsonify({"answer": "Por favor, digite sua dúvida."}), 400

        # Envia a pergunta para o Flowise
        result = query_flowise({"question": user_message})

        # Tratamento flexível da resposta (Flowise pode retornar 'text', 'json' ou 'answer')
        if isinstance(result, dict):
            if "error" in result:
                return jsonify({"answer": f"Desculpe, tive um problema: {result['error']}"}), 500
            
            answer = result.get("text") or result.get("answer") or result.get("json") or "Não consegui formular uma resposta."
        else:
            answer = str(result)

        return jsonify({"answer": answer})

    except Exception as e:
        logger.error(f"Erro na rota /ask: {e}")
        return jsonify({"answer": "Erro interno no servidor ao processar sua pergunta."}), 500

if __name__ == '__main__':
    # Rodando em modo debug para facilitar o desenvolvimento
    app.run(debug=True, port=5001)

    