from flask import Flask, render_template, request, jsonify
from openai import OpenAI
import os
import markdown
import bleach


app = Flask(__name__)

def ler_api_key(nome_arquivo='api_key.txt'):
    try:
        with open(nome_arquivo, 'r') as arquivo:
            return arquivo.read().strip()
    except FileNotFoundError:
        print(f"Erro: O arquivo {nome_arquivo} não foi encontrado.")
        return None

api_key = ler_api_key()
if api_key is None:
    raise ValueError("Não foi possível obter a chave API.")

client = OpenAI(
    base_url="https://integrate.api.nvidia.com/v1",
    api_key=api_key
)

mensagens = [{"role": "system", "content": "You are a helpful assistant."}]

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/chat', methods=['POST'])
def chat():
    global mensagens
    pergunta = request.json['pergunta']
    mensagens.append({"role": "user", "content": pergunta})

    try:
        completion = client.chat.completions.create(
            model="nvidia/llama-3.1-nemotron-70b-instruct",
            messages=mensagens,
            temperature=0.9,
            top_p=0.7,
            max_tokens=1024
        )
        resposta = completion.choices[0].message.content

        html_resposta = markdown.markdown(resposta)

        html_resposta_seguro = bleach.clean(html_resposta, tags=['p','strong', 'em', 'u', 'h1', 'h2', 'h3', 'ul', 'ol', 'li', 'code', 'pre'])
        
        mensagens.append({"role": "assistant", "content": resposta})
        return jsonify({"resposta": html_resposta_seguro})
    except Exception as e:
        return jsonify({"erro": str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True)