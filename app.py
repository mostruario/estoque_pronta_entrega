from flask import Flask, render_template, url_for
import pandas as pd
import os

app = Flask(__name__)

# Nome do arquivo Excel
EXCEL_FILE = "ESTOQUE PRONTA ENTREGA CLAMI.xlsx"

@app.route('/')
def index():
    if not os.path.exists(EXCEL_FILE):
        return f"Erro: arquivo '{EXCEL_FILE}' não encontrado."

    # Lê a planilha (linha 2 é o cabeçalho)
    df = pd.read_excel(EXCEL_FILE, header=1)

    # Limpa e renomeia colunas
    df.columns = df.columns.str.strip()
    df.rename(columns={
        "DESCRIÇÃO DO PRODUTO": "PRODUTO",
        "MARCA": "MARCA",
        "COMPRIMENTO": "COMPRIMENTO",
        "LARGURA": "LARGURA",
        "ALTURA": "ALTURA",
        "DIÂMETRO": "DIAMETRO",
        "DE": "DE",
        "POR": "POR",
        "CÓDIGO DO PRODUTO": "CODIGO",
        "ESTOQUE DISPONIVEL": "ESTOQUE",
        "LINK_IMAGEM": "IMAGEM_PRODUTO"
    }, inplace=True)

    produtos = []

    for _, row in df.iterrows():
        imagem_path = str(row.get("IMAGEM_PRODUTO", "")).strip()

        # ✅ Mantém o mesmo método de antes para funcionar no Render
        if imagem_path:
            nome_imagem = os.path.basename(imagem_path).replace("\\", "/")
            imagem_url = url_for('static', filename=f'IMAGENS_PRODUTOS/{nome_imagem}')
        else:
            imagem_url = url_for('static', filename='sem_imagem.png')

        produtos.append({
            "MARCA": str(row.get("MARCA", "")),
            "PRODUTO": str(row.get("PRODUTO", "")),
            "COMPRIMENTO": str(row.get("COMPRIMENTO", "")),
            "LARGURA": str(row.get("LARGURA", "")),
            "ALTURA": str(row.get("ALTURA", "")),
            "DIAMETRO": str(row.get("DIAMETRO", "")),
            "DE": str(row.get("DE", "")),
            "POR": str(row.get("POR", "")),
            "CODIGO": str(row.get("CODIGO", "")),
            "ESTOQUE": str(row.get("ESTOQUE", "")),
            "IMAGEM_PRODUTO": imagem_url
        })

    return render_template("index.html", produtos=produtos)


if __name__ == "__main__":
    # Para rodar localmente
    app.run(debug=True, host="0.0.0.0", port=5000)


