# 📊 Painel de Violência Doméstica

Este é um aplicativo web desenvolvido com **Flask** para análise e visualização de dados sobre violência doméstica a partir de um arquivo Excel. A ferramenta oferece **gráficos interativos**, **mapas** e **ferramentas de comparação** que permitem explorar os dados por município, região, data, natureza da ocorrência e muito mais.  
Ideal para pesquisadores, gestores públicos ou qualquer pessoa interessada em entender melhor os padrões da violência doméstica em Pernambuco.

---

## 🚀 Tecnologias Utilizadas

- 🔧 **Backend**: Python, Flask, Pandas, Unidecode  
- 📊 **Visualização**: Matplotlib, Folium  
- 📁 **Dados**: Excel (.xlsx), GeoJSON

---

## 🛠️ Funcionalidades

- ✅ Visualização de gráficos (pizza, barras, linha)
- ✅ Filtro por **município**, **região**, **data**, **sexo**, **idade** e **natureza**
- ✅ Geração de **mapa coroplético** com dados municipais
- ✅ Comparação entre dois municípios ou regiões
- ✅ Geração dinâmica de múltiplos gráficos
- ⚙️ Exportação automática de gráficos para a pasta `static/`

---

## 📁 Estrutura do Projeto

📁 projeto/
├── app.py                  # Arquivo principal (rota: ./app.py)
├── .gitignore
├── README.md
├── geojs-26-mun.json
├── Microdados Sobre Violencia Domestica.xlsx
├── static/
│   ├── script/             # JS files
│   ├── styles/             # CSS files
│   ├── *.png               # Gráficos gerados
│   └── mapa_pernambuco.html
├── templates/              # HTMLs renderizados pelo Flask


---

## ⚙️ Como Executar

### 1. **Clone o repositório ou baixe os arquivos**

### 2. **Crie e ative um ambiente virtual** (recomendado)

### 3. **Instale as dependências** 

- pip install flask pandas openpyxl matplotlib folium unidecode

### 4. **Coloque os arquivos necessários no diretório raiz:**

- Microdados Sobre Violencia Domestica.xlsx
- geojs-26-mun.json

### 5. **Execute a aplicação**

- python app.py
    ou 
- flask run

- Acesse via navegador: http://localhost:5000

## 🧩 Pré-requisitos

- Python 3.8+
- pip

## 🧠 Observações Importantes

- A aplicação cria automaticamente a pasta static/ com os gráficos e o mapa.
- Certifique-se de que os nomes dos municípios no GeoJSON correspondam aos do Excel.
- Para ambiente de produção, remova debug=True e use um servidor como o Gunicorn.

## ❓ Solução de Problemas

- 🔍 Erro de dependência: Verifique com pip install -r requirements.txt.
- 📂 Arquivos ausentes: Confirme se os dados estão no diretório correto.
- 🔄 Porta em uso: Altere para app.run(port=5001) ou outra porta disponível.

## 📄 Licença
Este projeto é de uso educacional e analítico, distribuído de forma livre para estudos, pesquisas e aprimoramentos.

## Desenvolvido com 🖥️ por Caio Medeiros.




