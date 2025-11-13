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

    # Limpa e renomeia as colunas
    df.columns = df.columns.str.strip()
    df.rename(columns={
        "DESCRIÇÃO DO PRODUTO": "PRODUTO",
        "MARCA": "MARCA",
        "LINK_IMAGEM": "IMAGEM_PRODUTO"
    }, inplace=True)

    if "PRODUTO" not in df.columns:
        return "Erro: coluna 'PRODUTO' não encontrada no arquivo Excel."

        produtos = []

    for _, row in df.iterrows():
        imagem_path = str(row.get("IMAGEM_PRODUTO", "")).strip()

        if imagem_path:
            nome_imagem = os.path.basename(imagem_path)
            nome_imagem = nome_imagem.replace("\\", "/").split("/")[-1]
            imagem_url = url_for('static', filename=f'IMAGENS_PRODUTOS/{nome_imagem}')
        else:
            imagem_url = url_for('static', filename='sem_imagem.png')

        produtos.append({
            "PRODUTO": str(row.get("PRODUTO", "")).strip(),
            "MARCA": str(row.get("MARCA", "")).strip(),
            "COMPRIMENTO": str(row.get("COMPRIMENTO", "")).strip(),
            "LARGURA": str(row.get("LARGURA", "")).strip(),
            "ALTURA": str(row.get("ALTURA", "")).strip(),
            "DIAMETRO": str(row.get("DIÂMETRO", row.get("DIAMETRO", ""))).strip(),
            "DE": str(row.get("DE", "")).strip(),
            "POR": str(row.get("POR", "")).strip(),
            "CODIGO": str(row.get("CÓDIGO", row.get("CODIGO", ""))).strip(),
            "ESTOQUE": str(row.get("ESTOQUE DISPONÍVEL", row.get("ESTOQUE_DISPONIVEL", ""))).strip(),
            "IMAGEM_PRODUTO": imagem_url
        })

    return render_template("index.html", produtos=produtos)


if __name__ == "__main__":
    # Para rodar localmente e no Render
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)


