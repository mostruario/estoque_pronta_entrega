from flask import Flask, render_template, url_for, request
import pandas as pd
import os

app = Flask(__name__)

EXCEL_FILE = "ESTOQUE PRONTA ENTREGA CLAMI.xlsx"

@app.route('/')
def index():
    if not os.path.exists(EXCEL_FILE):
        return f"Erro: arquivo '{EXCEL_FILE}' não encontrado."

    # 🔹 Lê a planilha, segunda linha como cabeçalho
    df = pd.read_excel(EXCEL_FILE, header=1)
    df.columns = df.columns.str.strip()

    # 🔹 Renomeia colunas usadas
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
    filtro_produto = request.args.get("produto", "")
    pesquisa = request.args.get("pesquisa", "").lower().strip()

    marcas = sorted(df["MARCA"].dropna().unique())

    # 🔹 Filtra marca
    df_filtrado = df.copy()
    if filtro_marca:
        df_filtrado = df_filtrado[df_filtrado["MARCA"].astype(str) == filtro_marca]
    else:
        filtro_produto = ""

    # 🔹 Produtos disponíveis (dependem da marca)
    produtos_disponiveis = sorted(df_filtrado["DESCRICAO_PRODUTO"].dropna().unique())
    if filtro_produto:
        df_filtrado = df_filtrado[df_filtrado["DESCRICAO_PRODUTO"].astype(str) == filtro_produto]

    # 🔹 Filtro pesquisa (CORRIGIDO)
    if pesquisa:
        pesquisa_lower = pesquisa.lower()
        df_filtrado = df_filtrado[
            df_filtrado["DESCRICAO_PRODUTO"].astype(str).str.lower().str.contains(pesquisa_lower)
            | df_filtrado["CODIGO_PRODUTO"].astype(str).str.contains(pesquisa_lower)
        ]

    # 🔹 Monta lista de produtos sem duplicação de código
    produtos = []
    codigos_vistos = set()
    for _, row in df_filtrado.iterrows():
        codigo_produto = str(row.get("CODIGO_PRODUTO", ""))
        if codigo_produto in codigos_vistos:
            continue
        codigos_vistos.add(codigo_produto)

        imagem_path = str(row.get("IMAGEM_PRODUTO", "")).strip()
        if imagem_path:
            nome_imagem = os.path.basename(imagem_path).replace("\\", "/").split("/")[-1]
            imagem_url = url_for('static', filename=f'IMAGENS_PRODUTOS/{nome_imagem}')
        else:
            imagem_url = url_for('static', filename='sem_imagem.png')

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
        produtos_disponiveis=produtos_disponiveis,
        filtro_marca=filtro_marca,
        filtro_produto=filtro_produto,
        pesquisa=pesquisa
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)

