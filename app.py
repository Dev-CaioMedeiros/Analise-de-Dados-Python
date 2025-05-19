from flask import Flask, render_template, request
import io, base64, os, datetime, folium, json
import pandas as pd
import matplotlib.pyplot as plt

# Cria o aplicativo Flask
app = Flask(__name__)


# Lê os dados do Excel
# Esse arquivo tem os casos de violência doméstica
df = pd.read_excel("Microdados Sobre Violencia Domestica.xlsx")
df["MUNICÍPIO DO FATO"] = df["MUNICÍPIO DO FATO"].astype(str).str.strip().str.upper()


# Converte datas para o formato certo
df['DATA DO FATO'] = pd.to_datetime(df['DATA DO FATO'], errors='coerce')

# Dicionário com nomes que precisam ser corrigidos (nomes diferentes entre o Excel e o mapa)
substituicoes_municipios = {
    "BELEM DO SAO FRANCISCO": "BELEM DE SAO FRANCISCO",
    "SAO CAETANO": "SAO CAITANO",
    "LAGOA DE ITAENGA": "LAGOA DO ITAENGA",
    "ITAMARACA": "ILHA DE ITAMARACA"
}

# Define os tipos de gráficos que vão ser mostrados no dashboard
colunas_disponiveis = {
    "municipio": ("MUNICÍPIO DO FATO", "bar"),
    "regiao": ("REGIAO GEOGRÁFICA", "pie"),
    "natureza": ("NATUREZA", "barh"),
    "data": ("DATA DO FATO", "line"),
    "ano": ("ANO", "bar"),
    "sexo": ("SEXO", "bar"),
    "idade": ("IDADE SENASP", "bar"),
    "envolvidos": ("TOTAL DE ENVOLVIDOS", "line")
}

# Função que cria os gráficos com base nos dados
# Gera imagens salvas na pasta static
# Cada tipo usa um estilo de gráfico diferente

def criar_grafico(coluna, nome_arquivo, tipo):
    dados_contagem = df[coluna].value_counts().nlargest(11 if coluna == "ANO" else 10)

    if coluna == "DATA DO FATO":
        dados_contagem.index = pd.to_datetime(dados_contagem.index, errors='coerce')
        dados_contagem = dados_contagem.dropna()
        dados_contagem.index = dados_contagem.index.strftime('%d/%m/%Y')

    plt.figure(figsize=(10, 6))

    if tipo == "bar":
        dados_contagem.plot(kind='bar', color='teal')
    elif tipo == "pie":
        dados_contagem.plot(kind='pie', autopct='%1.1f%%', startangle=140, textprops={'fontsize': 10})
        plt.ylabel('')
        plt.xlabel('')
        
    elif tipo == "line":
        dados_contagem.sort_index().plot(kind='line', marker='o', color='green')
    elif tipo == "barh":
        dados_contagem.plot(kind='barh', color='teal')

    plt.xticks(rotation=45, ha='right', fontsize=10)
    plt.tight_layout()

    if not os.path.exists("static"):
        os.makedirs("static")

    plt.savefig(f"static/{nome_arquivo}.png")
    plt.close()

    return dados_contagem.reset_index().values.tolist()

# Página principal com os botões
@app.route("/")
def dashboard():
    return render_template("index.html", categorias=colunas_disponiveis)

# Mostra os gráficos de cada tipo escolhido pelo usuário
@app.route("/grafico/<categoria>")
def exibir_grafico(categoria):
    nome_coluna, tipo_grafico = colunas_disponiveis.get(categoria, ("MUNICÍPIO DO FATO", "bar"))
    nome_arquivo = f"grafico_{categoria}"
    dados = criar_grafico(nome_coluna, nome_arquivo, tipo_grafico)
    timestamp = datetime.datetime.now().timestamp()
    return render_template("grafico.html", dados=dados, categoria=categoria, nome_arquivo=nome_arquivo, timestamp=timestamp)

# Página que permite filtrar os dados com base em opções escolhidas
@app.route("/data", methods=["GET", "POST"])
def filtrar_data():
    meses = [
        (0, 'Todos'), (1, 'Janeiro'), (2, 'Fevereiro'), (3, 'Março'), (4, 'Abril'),
        (5, 'Maio'), (6, 'Junho'), (7, 'Julho'), (8, 'Agosto'), (9, 'Setembro'),
        (10, 'Outubro'), (11, 'Novembro'), (12, 'Dezembro')
    ]
    anos_disponiveis = sorted(df['DATA DO FATO'].dropna().dt.year.unique().tolist())
    anos_unicos = [(0, 'Todos')] + [(ano, str(ano)) for ano in anos_disponiveis] 
    sexos = ['Todos'] + sorted(df['SEXO'].dropna().unique().tolist())
    regioes = ['Todas'] + sorted(df['REGIAO GEOGRÁFICA'].dropna().unique().tolist())
    municipios = ['Todos'] + sorted(df['MUNICÍPIO DO FATO'].dropna().unique().tolist())
    naturezas = ['Todas'] + sorted(df['NATUREZA'].dropna().unique().tolist())
    idades = ['Todas'] + sorted(df['IDADE SENASP'].dropna().unique().tolist())

    resultado = None
    total_casos = 0

    if request.method == "POST":
        tipo_filtro = request.form.get("tipo_filtro")
        filtros = []

        # Filtro por mês/ano ou intervalo de datas
        if tipo_filtro == "padrao":
            mes_selecionado = request.form.get("mes")
            ano_selecionado = request.form.get("ano")
            if mes_selecionado != '0':
                filtros.append(df['DATA DO FATO'].dt.month == int(mes_selecionado))
            if ano_selecionado != '0':
                filtros.append(df['DATA DO FATO'].dt.year == int(ano_selecionado))
        elif tipo_filtro == "intervalo":
            data_inicio = request.form.get("data_inicio")
            data_fim = request.form.get("data_fim")
            if data_inicio:
                filtros.append(df['DATA DO FATO'] >= pd.to_datetime(data_inicio))
            if data_fim:
                filtros.append(df['DATA DO FATO'] <= pd.to_datetime(data_fim))

        # Filtros de outras colunas
        sexo_selecionado = request.form.get("sexo")
        regiao_selecionada = request.form.get("regiao")
        municipio_selecionado = request.form.get("municipio")
        natureza_selecionada = request.form.get("natureza")
        idade_selecionada = request.form.get("idade")

        if sexo_selecionado != 'Todos':
            filtros.append(df['SEXO'] == sexo_selecionado)
        if regiao_selecionada != 'Todas':
            filtros.append(df['REGIAO GEOGRÁFICA'] == regiao_selecionada)
        if municipio_selecionado != 'Todos':
            filtros.append(df['MUNICÍPIO DO FATO'] == municipio_selecionado)
        if natureza_selecionada != 'Todas':
            filtros.append(df['NATUREZA'] == natureza_selecionada)
        if idade_selecionada != 'Todas':
            filtros.append(df['IDADE SENASP'] == idade_selecionada)

        if filtros:
            filtro_final = filtros[0]
            for filtro in filtros[1:]:
                filtro_final = filtro_final & filtro
            filtro = df[filtro_final]
            total_casos = len(filtro)
            resultado = f"{total_casos} caso(s) encontrado(s) com os filtros selecionados"
        else:
            total_casos = len(df)
            resultado = f"Total de {total_casos} casos registrados."

    return render_template(
        "data.html",
        meses=meses,
        anos=anos_unicos,
        sexos=sexos,
        regioes=regioes,
        municipios=municipios,
        naturezas=naturezas,
        idades=idades,
        resultado=resultado,
        total_casos=total_casos
    )

# Rota que gera o mapa com dados por município
@app.route("/mapa")
def mapa():
    import unidecode

    with open("geojs-26-mun.json", "r", encoding="utf-8") as f:
        geojson_data = json.load(f)

    # Ajustes no nome dos municípios
    df["MUNICÍPIO SEM ACENTO"] = df["MUNICÍPIO DO FATO"].apply(lambda x: unidecode.unidecode(x))
    df["MUNICÍPIO CORRIGIDO"] = df["MUNICÍPIO SEM ACENTO"].replace(substituicoes_municipios)
    df["REGIAO SEM ACENTO"] = df["REGIAO GEOGRÁFICA"].apply(lambda x: unidecode.unidecode(str(x).upper()))

    # Conta os casos por município
    dados_municipio = df.groupby("MUNICÍPIO CORRIGIDO").agg({
        "TOTAL DE ENVOLVIDOS": "count",
        "REGIAO SEM ACENTO": "first"
    }).reset_index()

    dados_municipio.columns = ["municipio", "casos", "regiao"]

    # Corrige os nomes dos municípios no GeoJSON
    for feature in geojson_data["features"]:
        nome_original = feature["properties"]["name"]
        nome_formatado = unidecode.unidecode(nome_original.upper())
        feature["properties"]["municipio_fmt"] = nome_formatado

    # Cria o mapa
    mapa = folium.Map(location=[-8.0476, -34.8770], zoom_start=7)

    # Cria o mapa colorido com os dados
    folium.Choropleth(
        geo_data=geojson_data,
        name="choropleth",
        data=dados_municipio,
        columns=["municipio", "casos"],
        key_on="feature.properties.municipio_fmt",
        fill_color="YlOrRd",
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name="Casos por Município",
    ).add_to(mapa)

    # Popups com nome, casos e região
    casos_dict = dict(zip(dados_municipio["municipio"], dados_municipio["casos"]))
    regioes_dict = dict(zip(dados_municipio["municipio"], dados_municipio["regiao"]))

    for feature in geojson_data["features"]:
        nome_mun = feature["properties"]["municipio_fmt"]
        feature["properties"]["casos"] = casos_dict.get(nome_mun, 0)
        feature["properties"]["regiao"] = regioes_dict.get(nome_mun, "Desconhecida")

    folium.GeoJson(
        geojson_data,
        name="Municípios",
        tooltip=folium.GeoJsonTooltip(
            fields=["name", "casos", "regiao"],
            aliases=["Município:", "Casos:", "Região:"],
            localize=True,
            sticky=False
        )
    ).add_to(mapa)

    # Salva o mapa como HTML
    mapa.save("static/mapa_pernambuco.html")
    return render_template("mapa_pernambuco.html")

#Cria a rota para comparar dois municípios ou regiões
@app.route("/comparar", methods=["GET", "POST"])
def comparar():
    resultado = None
    erro = None
    # Obtém o tipo do formulário ou mantém o padrão
    tipo = request.form.get("tipo", request.args.get("tipo", "municipio"))

    try:
        # Determina as opções e a coluna com base no tipo
        if tipo == "regiao":
            opcoes = sorted(df["REGIAO GEOGRÁFICA"].dropna().unique().tolist())
            coluna = "REGIAO GEOGRÁFICA"
        else:
            opcoes = sorted(df["MUNICÍPIO DO FATO"].dropna().unique().tolist())
            coluna = "MUNICÍPIO DO FATO"

        if request.method == "POST" and "local1" in request.form and "local2" in request.form:
            local1 = request.form.get("local1")
            local2 = request.form.get("local2")

            # Valida se os locais foram selecionados
            if not local1 or not local2:
                erro = "Selecione ambos os locais."
            elif local1 not in opcoes or local2 not in opcoes:
                erro = "Um ou ambos os locais selecionados são inválidos."
            else:
                # Calcula os totais
                total_1 = df[df[coluna] == local1].shape[0]
                total_2 = df[df[coluna] == local2].shape[0]

                # Obtém a distribuição por sexo
                resumo_1 = df[df[coluna] == local1]["SEXO"].value_counts().to_dict()
                resumo_2 = df[df[coluna] == local2]["SEXO"].value_counts().to_dict()

                # Gera a comparação
                if total_1 > total_2:
                    comparacao = f"{local1} teve {total_1 - total_2} caso(s) a mais que {local2}."
                elif total_2 > total_1:
                    comparacao = f"{local2} teve {total_2 - total_1} caso(s) a mais que {local1}."
                else:
                    comparacao = f"{local1} e {local2} tiveram a mesma quantidade de casos."

                resultado = {
                    "tipo": tipo,
                    "local1": local1,
                    "total1": total_1,
                    "resumo1": resumo_1,
                    "local2": local2,
                    "total2": total_2,
                    "resumo2": resumo_2,
                    "comparacao": comparacao
                }

        return render_template(
            "comparar.html",
            tipo=tipo,
            opcoes=opcoes,
            resultado=resultado if resultado else {},
            erro=erro
        )

    except KeyError as e:
        erro = f"Erro: Coluna {e} não encontrada no DataFrame."
    except Exception as e:
        erro = f"Erro inesperado: {str(e)}"

    return render_template(
        "comparar.html",
        tipo=tipo,
        opcoes=opcoes if 'opcoes' in locals() else [],
        resultado=resultado if resultado else {},
        erro=erro
    )



@app.route("/opcoes")
def obter_opcoes():
    tipo = request.args.get("tipo", "municipio")
    try:
        if tipo == "regiao":
            opcoes = sorted(df["REGIAO GEOGRÁFICA"].dropna().unique().tolist())
        else:
            opcoes = sorted(df["MUNICÍPIO DO FATO"].dropna().unique().tolist())
        return {"opcoes": opcoes}
    except Exception as e:
        return {"opcoes": [], "erro": str(e)}

@app.route("/comparador")
def comparador():
    return render_template("comparador.html")

@app.route("/graficos")
def graficos():
    return render_template("graficos.html")

@app.route("/gerar_graficos", methods=["POST"])
def gerar_graficos_route():
    data = request.get_json()
    variaveis = data.get('variaveis', [])

    if not variaveis:
        return "<p>Nenhuma variável selecionada.</p>"

    html = "<h2>Gráficos Gerados</h2>"
    timestamp = datetime.datetime.now().timestamp()

    for var in variaveis:
        if var not in colunas_disponiveis:
            html += f"<p>Variável inválida: {var}</p>"
            continue

        nome_coluna, tipo_grafico = colunas_disponiveis[var]
        nome_arquivo = f"grafico_{var}"

        if var == "ano" and "ANO" not in df.columns:
            df["ANO"] = df["DATA DO FATO"].dt.year

        criar_grafico(nome_coluna, nome_arquivo, tipo_grafico)

        html += f"""
            <div style="margin-bottom: 30px;">
                <h3>{nome_coluna}</h3>
                <img src="/static/{nome_arquivo}.png?{timestamp}" style="max-width: 100%; height: auto;">
            </div>
        """

    return html

if __name__ == "__main__":
    app.run(debug=True, threaded=True)
