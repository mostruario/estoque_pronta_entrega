from flask import Flask, render_template
import pandas as pd
import os

app = Flask(__name__)

# Caminho base do projeto
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
EXCEL_PATH = os.path.join(BASE_DIR, "PRODUTOS", "ESTOQUE PRONTA ENTREGA CLAMI.xlsx")


def ajustar_caminho_imagem(caminho):
    """Converte caminho absoluto do Windows em caminho válido para o Flask"""
    if pd.isna(caminho):
        return None

    caminho = str(caminho).strip().replace("\\", "/")

    # Remove a parte inicial até STATIC/
    if "STATIC/" in caminho.upper():
        partes = caminho.upper().split("STATIC/")
        relativo = partes[1]  # tudo depois de STATIC/
        return f"IMAGENS_PRODUTOS/{os.path.basename(relativo)}"

    # Caso não tenha STATIC no caminho, assume que já é relativo
    return f"IMAGENS_PRODUTOS/{os.path.basename(caminho)}"


@app.route('/')
def index():
    """Página principal com os produtos"""
    # Lê o Excel pulando a primeira linha (porque os títulos estão na segunda)
    df = pd.read_excel(EXCEL_PATH, header=1)

    # Remove linhas sem descrição
    df = df.dropna(subset=['DESCRIÇÃO DO PRODUTO'])

    # Ajusta as imagens
    df['LINK_IMAGEM'] = df['LINK_IMAGEM'].apply(ajustar_caminho_imagem)

    # Converte para dicionário
    produtos = df.to_dict(orient='records')

    return render_template('index.html', produtos=produtos)


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))  # Porta dinâmica exigida pelo Render
    app.run(host='0.0.0.0', port=port)





