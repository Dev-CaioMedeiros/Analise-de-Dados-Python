from flask import Flask, render_template, request
import pandas as pd
import matplotlib.pyplot as plt
import os
import datetime
import folium
import json

app = Flask(__name__)

df = pd.read_excel("Microdados Sobre Violencia Domestica.xlsx")
df["MUNICÍPIO DO FATO"] = df["MUNICÍPIO DO FATO"].astype(str).str.strip().str.upper()

for col in ['SEXO', 'REGIAO GEOGRÁFICA', 'MUNICÍPIO DO FATO', 'NATUREZA', 'IDADE SENASP']:
    df[col] = df[col].astype(str).str.strip()

df['DATA DO FATO'] = pd.to_datetime(df['DATA DO FATO'], errors='coerce')

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

@app.route("/")
def dashboard():
    return render_template("index.html", categorias=colunas_disponiveis)

@app.route("/grafico/<categoria>")
def exibir_grafico(categoria):
    nome_coluna, tipo_grafico = colunas_disponiveis.get(categoria, ("MUNICÍPIO DO FATO", "bar"))
    nome_arquivo = f"grafico_{categoria}"
    dados = criar_grafico(nome_coluna, nome_arquivo, tipo_grafico)
    timestamp = datetime.datetime.now().timestamp()
    return render_template("grafico.html", dados=dados, categoria=categoria, nome_arquivo=nome_arquivo, timestamp=timestamp)

@app.route("/mapa")
def mapa():
    with open("geojs-26-mun.json", "r", encoding="utf-8") as f:
        geojson_data = json.load(f)

    dados_municipio = df["MUNICÍPIO DO FATO"].value_counts().reset_index()
    dados_municipio.columns = ["Municipio", "Casos"]
    dados_municipio["Municipio"] = dados_municipio["Municipio"].str.upper()

    mapa = folium.Map(location=[-8.0476, -34.8770], zoom_start=7)

    folium.Choropleth(
        geo_data=geojson_data,
        name="choropleth",
        data=dados_municipio,
        columns=["Municipio", "Casos"],
        key_on="feature.properties.name",
        fill_color="YlOrRd",
        fill_opacity=0.7,
        line_opacity=0.2,
        legend_name="Casos por Município"
    ).add_to(mapa)

    for feature in geojson_data["features"]:
        nome = feature["properties"]["name"].upper()
        casos = int(dados_municipio.set_index("Municipio").get("Casos", {}).get(nome, 0))
        popup = folium.Popup(f"{nome.title()}: {casos} caso(s)", parse_html=True)
        geo = folium.GeoJson(feature)
        geo.add_child(popup)
        geo.add_to(mapa)

    mapa.save("static/mapa_pernambuco.html")
    return render_template("mapa_pernambuco.html")

if __name__ == "__main__":
    app.run(debug=True, threaded=True)
