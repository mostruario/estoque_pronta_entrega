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

        # Se o caminho for algo como "P:\PRODUTO_PRONTA_ENTREGA\static\IMAGENS_PRODUTOS\SOFA SONETO_379922_379923.jpg"
        # Pegamos apenas o nome do arquivo:
        if imagem_path:
            nome_imagem = os.path.basename(imagem_path)
            imagem_url = url_for('static', filename=f'IMAGENS_PRODUTOS/{nome_imagem}')
        else:
            imagem_url = url_for('static', filename='sem_imagem.png')

        produtos.append({
            "PRODUTO": str(row.get("PRODUTO", "")),
            "MARCA": str(row.get("MARCA", "")),
            "IMAGEM_PRODUTO": imagem_url
        })

    return render_template("index.html", produtos=produtos)


if __name__ == "__main__":
    # Para rodar localmente
    app.run(debug=True, host="0.0.0.0", port=5000)

