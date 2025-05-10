from flask import Flask, render_template, request
import pandas as pd
import matplotlib.pyplot as plt
import os
import datetime

app = Flask(__name__)
df = pd.read_excel("Microdados de Violencia Domestica.xlsx")

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
        plt.xlabel(coluna.title(), fontsize=12)
        plt.ylabel("Quantidade de Casos", fontsize=12)

    elif tipo == "pie":
        dados_contagem.plot(
            kind='pie',
            autopct='%1.1f%%',
            startangle=140,
            textprops={'fontsize': 10, 'color': 'black'}
        )
        plt.xlabel("")
        plt.ylabel("")

    elif tipo == "line":
        dados_contagem.sort_index().plot(kind='line', marker='o', color='green')
        plt.xlabel(coluna.title(), fontsize=12)
        plt.ylabel("Quantidade de Casos", fontsize=12)

    elif tipo == "barh":
        dados_contagem.plot(kind='barh', color='teal')
        plt.xlabel("Quantidade de Casos", fontsize=12)
        plt.ylabel(coluna.title(), fontsize=12)

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

@app.route("/data", methods=["GET", "POST"])
def filtrar_data():

    meses = [
        (1, 'Janeiro'), (2, 'Fevereiro'), (3, 'Março'), (4, 'Abril'),
        (5, 'Maio'), (6, 'Junho'), (7, 'Julho'), (8, 'Agosto'),
        (9, 'Setembro'), (10, 'Outubro'), (11, 'Novembro'), (12, 'Dezembro')
    ]

    df['DATA DO FATO'] = pd.to_datetime(df['DATA DO FATO'], errors='coerce')
    anos_unicos = sorted(df['DATA DO FATO'].dropna().dt.year.unique())

    resultado = None
    total_casos = 0

    if request.method == "POST":
        mes = request.form.get("mes")
        ano = request.form.get("ano")

        if mes and ano:
            mes = int(mes)
            ano = int(ano)

            filtro = df[
                (df['DATA DO FATO'].dt.month == mes) &
                (df['DATA DO FATO'].dt.year == ano)
            ]
            total_casos = len(filtro)

            nome_mes = dict(meses)[mes]
            resultado = f"{nome_mes} de {ano} — {total_casos} caso(s) registrado(s)"

    return render_template("data.html", meses=meses, anos=anos_unicos, resultado=resultado, total_casos=total_casos)

@app.route("/grafico/<categoria>")
def exibir_grafico(categoria):
    nome_coluna, tipo_grafico = colunas_disponiveis.get(categoria, ("MUNICÍPIO DO FATO", "bar"))
    nome_arquivo = f"grafico_{categoria}"
    dados = criar_grafico(nome_coluna, nome_arquivo, tipo_grafico)
    timestamp = datetime.datetime.now().timestamp()
    return render_template("grafico.html", dados=dados, categoria=categoria, nome_arquivo=nome_arquivo, timestamp=timestamp)

if __name__ == "__main__":
    app.run(debug=True, threaded=True)
