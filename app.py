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

    # 🔹 Renomeia colunas usadas (preserva nomes originais caso existam)
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
        "LINK_IMAGEM": "IMAGEM_PRODUTO"   # caso exista este nome
    }, inplace=True)

    # 🔹 Filtros (recebe marca_hidden caso template envie lista de marcas)
    filtro_marca_raw = request.args.get("marca_hidden", request.args.get("marca", ""))
    # transforma em lista se vier como "A,B,C"
    filtro_marca = [m.strip() for m in filtro_marca_raw.split(",") if m.strip()] if filtro_marca_raw else []
    # considera "Todas" como não-filtrar
    if "Todas" in [m.upper() for m in filtro_marca]:
        filtro_marca = []

    filtro_produto = request.args.get("produto", "")
    filtro_imagem = request.args.get("imagem", "").strip().lower()   # 'com' | 'sem' | ''
    pesquisa = request.args.get("pesquisa", "").strip()

    marcas = sorted(df["MARCA"].dropna().unique())

    # 🔹 Filtra marca (suporta múltiplas marcas)
    df_filtrado = df.copy()
    if filtro_marca:
        df_filtrado = df_filtrado[df_filtrado["MARCA"].astype(str).isin(filtro_marca)]
    else:
        # quando não filtra por marca, zera filtro produto para evitar dependência
        filtro_produto = ""

    # 🔹 Produtos disponíveis (dependem da marca filtrada)
    produtos_disponiveis = sorted(df_filtrado["DESCRICAO_PRODUTO"].dropna().unique())
    if filtro_produto:
        df_filtrado = df_filtrado[df_filtrado["DESCRICAO_PRODUTO"].astype(str) == filtro_produto]

    # 🔹 Determina coluna que indica "SEM IMAGEM"/"COM IMAGEM" na planilha
    # possíveis nomes: 'IMAGEM' (coluna V), 'IMAGEM_PRODUTO', 'LINK_IMAGEM'
    imagem_col = None
    for candidate in ["IMAGEM", "IMAGEM_PRODUTO", "LINK_IMAGEM"]:
        if candidate in df_filtrado.columns:
            imagem_col = candidate
            break

    # 🔹 FILTRO DE IMAGEM (usa o texto da planilha: "SEM IMAGEM" / "COM IMAGEM" ou vazio)
    if filtro_imagem and imagem_col:
        if filtro_imagem == "com":
            # mantém linhas que NÃO estão marcadas como "SEM IMAGEM" e que não são vazias
            df_filtrado = df_filtrado[
                (~df_filtrado[imagem_col].astype(str).str.upper().str.contains(r"SEM\s*IMAGEM", na=False))
                & (df_filtrado[imagem_col].astype(str).str.strip() != "")
                & df_filtrado[imagem_col].notna()
            ]
        elif filtro_imagem == "sem":
            # mantém linhas marcadas como "SEM IMAGEM" ou vazias / NaN
            df_filtrado = df_filtrado[
                df_filtrado[imagem_col].astype(str).str.upper().str.contains(r"SEM\s*IMAGEM", na=False)
                | df_filtrado[imagem_col].astype(str).str.strip().eq("")
                | df_filtrado[imagem_col].isna()
            ]

    # 🔹 Filtro pesquisa (DESCRIÇÃO OU CÓDIGO) - case insensitive
    if pesquisa:
        pesquisa_lower = pesquisa.lower()
        df_filtrado = df_filtrado[
            df_filtrado["DESCRICAO_PRODUTO"].astype(str).str.lower().str.contains(pesquisa_lower, na=False)
            | df_filtrado["CODIGO_PRODUTO"].astype(str).str.contains(pesquisa_lower, na=False)
        ]

    # 🔹 Monta lista de produtos sem duplicação de código
    produtos = []
    codigos_vistos = set()
    for _, row in df_filtrado.iterrows():
        codigo_produto = str(row.get("CODIGO_PRODUTO", ""))
        if codigo_produto in codigos_vistos:
            continue
        codigos_vistos.add(codigo_produto)

        # pega o caminho/valor da imagem (coluna original se existir)
        imagem_path_raw = ""
        for candidate in ["LINK_IMAGEM", "IMAGEM_PRODUTO", "IMAGEM"]:
            if candidate in row and row.get(candidate, "") is not None:
                imagem_path_raw = str(row.get(candidate, "")).strip()
                if imagem_path_raw:
                    break

        # se planilha marcar "SEM IMAGEM" ou string vazia -> usar imagem padrão
        if imagem_path_raw and not imagem_path_raw.upper().startswith("SEM IMAGEM"):
            # extrai nome do arquivo e monta URL estática
            nome_imagem = os.path.basename(imagem_path_raw).replace("\\", "/").split("/")[-1]
            imagem_url = url_for('static', filename=f'IMAGENS_PRODUTOS/{nome_imagem}')
        else:
            # arquivo default na pasta static (como você indicou)
            imagem_url = url_for('static', filename='IMAGENS_PRODUTOS/SEM IMAGEM.jpg')

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
        filtro_marca=filtro_marca,       # lista (pode estar vazia)
        filtro_produto=filtro_produto,
        filtro_imagem=filtro_imagem,     # 'com' | 'sem' | ''
        pesquisa=pesquisa
    )


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(debug=True, host="0.0.0.0", port=port)


