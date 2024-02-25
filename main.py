from flask import Flask, render_template, request, jsonify
import pandas as pd
from unidecode import unidecode

app = Flask(__name__, static_url_path='/static')

# Carregar os dataframes
df_tokens = pd.read_csv('web_tokens.csv')
df_links = pd.read_csv('web_links.csv')

def calc_tx_pesq(df_pesquisa):
    df_final = pd.DataFrame(columns=['id', 'tokens', 'qtd_token', 'taxa_pesquisa'])

    for id in df_pesquisa['id'].drop_duplicates():
        df = df_pesquisa[df_pesquisa['id'] == id]
        count = len(df_pesquisa[df_pesquisa['id'] == id])
        taxa_pesquisa = 0

        for i in range(count):
            for j in range(count):
                if i != j:
                    if taxa_pesquisa == 0:
                        if df['qnt_rep'].iloc[j] != 0:
                            taxa_pesquisa = int(df['qnt_rep'].iloc[i]) / int(df['qnt_rep'].iloc[j])
                        else:
                            taxa_pesquisa = int(df['qnt_rep'].iloc[i])
                    else:
                        if df['qnt_rep'].iloc[j] != 0:
                            taxa_pesquisa = int(df['qnt_rep'].iloc[i]) / int(df['qnt_rep'].iloc[j])
                        else:
                            taxa_pesquisa = int(df['qnt_rep'].iloc[i])

        df2 = df['token'].tolist()
        string = ','.join(df2)

        valores = pd.DataFrame({'id': [id], 'tokens': [string], 'qtd_token':count, 'taxa_pesquisa': [abs(taxa_pesquisa)]})
        df_final = pd.concat([df_final, valores], ignore_index=True)

    return df_final.sort_values(by=['qtd_token', 'taxa_pesquisa'], ascending=[False, True])

# Função para realizar a pesquisa
def realizar_pesquisa(palavras_pesquisa):
    # Normaliza as palavras (remove acentuação e converte para minúsculas)
    palavras_normalizadas = [unidecode(palavra.lower()) for palavra in palavras_pesquisa]

    # Filtra o DataFrame com base nas palavras normalizadas da pesquisa
    df_pesquisa = df_tokens[df_tokens['token'].isin(palavras_normalizadas)]

    # Realiza um inner join com o DataFrame de links para obter os títulos dos links correspondentes
    resultados = pd.merge(df_pesquisa[['id', 'token', 'qnt_rep']], df_links[['id', 'title', 'link']], on='id', how='inner').drop_duplicates()

    df = calc_tx_pesq(resultados)

    resultados = df

    return pd.merge(resultados, df_links, on='id', how='inner')

# Rota principal
@app.route('/')
def index():
    return render_template('index.html')

# Rota de pesquisa
@app.route('/search')
def search():
    pesquisa = request.args.get('q', '').lower()
    keywords = pesquisa.split()
    resultados = realizar_pesquisa(keywords)

    # Retorna os resultados em formato JSON
    return jsonify(render_template('results.html', resultados=resultados, palavras_pesquisa=keywords))

# Rota para a página de resultados
@app.route('/results')
def results():
    return render_template('results.html')

# Rota para a página de pesquisa (se necessário)
@app.route('/search-page')
def search_page():
    return render_template('search.html')

if __name__ == '__main__':
    app.run(debug=True)
