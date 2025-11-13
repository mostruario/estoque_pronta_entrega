from flask import Flask, render_template, url_for, request
import pandas as pd
import os

app = Flask(__name__)

EXCEL_FILE = "ESTOQUE PRONTA ENTREGA CLAMI.xlsx"

@app.route('/')
def index():
    if not os.path.exists(EXCEL_FILE):
        return f"Erro: arquivo '{EXCEL_FILE}' não encontrado."

    df = pd.read_excel(EXCEL_FILE, header=1)
    df.columns = df.columns.str.strip()

    # 🔹 Renomeia apenas o que for usado diretamente
    df.rename(columns={
        "DESCRIÇÃO DO PRODUTO": "DESCRICAO_PRODUTO",
        "MARCA": "MARCA",
        "COMPRIMENTO": "COMPRIMENTO",
        "LARGURA": "LARGURA",
        "ALTURA": "ALTURA",
        "DIAMETRO": "DIAMETRO",
        "DE": "DE",
        "POR": "POR",
        "CODIGO DO PRODUTO": "CODIGO_PRODUTO",
        "ESTOQUE DISPONIVEL": "ESTOQUE",
        "LINK_IMAGEM": "IMAGEM_PRODUTO"
    }, inplace=True)

    # 🔹 Filtros
    filtro_marca = request.args.get("marca", "")
    pesquisa = request.args.get("pesquisa", "").lower().strip()

    marcas = sorted(df["MARCA"].dropna().unique())

    if filtro_marca:
        df = df[df["MARCA"].astype(str) == filtro_marca]
    if pesquisa:
        df = df[df["DESCRICAO_PRODUTO"].astype(str).str.lower().str.contains(pesquisa)]

    produtos = []
    codigos_vistos = set()  # 🔹 Evita duplicação de cards
    for _, row in df.iterrows():
        codigo_produto = str(row.get("CODIGO_PRODUTO", ""))
        if codigo_produto in codigos_vistos:
            continue  # pula se o código já foi adicionado
        codigos_vistos.add(codigo_produto)

        imagem_path = str(row.get("IMAGEM_PRODUTO", "")).strip()
        if imagem_path:
            nome_imagem = os.path.basename(imagem_path)
            nome_imagem = nome_imagem.replace("\\", "/").split("/")[-1]
            imagem_url = url_for('static', filename=f'IMAGENS_PRODUTOS/{nome_imagem}')
        else:
            imagem_url = url_for('static', filename='sem_imagem.png')

        # 🔹 Formata valores em reais (R$)
        def formatar_real(valor):
            try:
                valor_float = float(valor)
                return f"R$ {valor_float:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")
            except:
                return str(valor)

        produtos.append({
            "DESCRICAO_PRODUTO": str(row.get("DESCRICAO_PRODUTO", "")),
            "MARCA": str(row.get("MARCA", "")),
            "COMPRIMENTO": str(row.get("COMPRIMENTO", "")),
            "LARGURA": str(row.get("LARGURA", "")),
            "ALTURA": str(row.get("ALTURA", "")),
            "DIAMETRO": str(row.get("DIAMETRO", "")),
            "DE": formatar_real(row.get("DE", "")),
            "POR": formatar_real(row.get("POR", "")),
            "CODIGO_PRODUTO": codigo_produto,
            "ESTOQUE": str(row.get("ESTOQUE", "")),
            "IMAGEM_PRODUTO": imagem_url
        })

    return render_template(
        "index.html",
        produtos=produtos,
        marcas=marcas,
        filtro_marca=filtro_marca,
        pesquisa=pesquisa
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)




