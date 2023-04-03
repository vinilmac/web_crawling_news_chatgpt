import requests
import lxml
from bs4 import BeautifulSoup
from xlwt import *
import os
import sys
import openai
from textblob import TextBlob
import pandas as pd
import nltk
from nltk.corpus import stopwords
from nltk.tokenize import word_tokenize
from collections import Counter



# Configuraçoes de encoding para caracteres especiais nos textos dos outputs
sys.stdout.reconfigure(encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'UTF-8'

# Chave API do OpenAI
openai.api_key = "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"


# Site que queremos realizar o Web Crawling
url = "https://agenciabrasil.ebc.com.br/ultimas?page=5"

# As vezes a página possui um "anti-crawler setting" para evitar coleta maliciosa de dados da página
# Para resolver, utilizamos o parâmetro de headers que irá simular a informação inicial da página
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE'}

# Resposta do link dado com uso do 'requests'
f = requests.get(url, headers = headers)

# Conteúdo da resposta do link dado
page_content = f.content

# Criando um objeto em BeautifulSoup do HTML do site. Ele irá pegar o HTML do site e quebrar em objetos Python
soup = BeautifulSoup(f.content,'lxml')

# Na inspeção do site, procurar a celula HTLM que contém as informações que queremos
# O "find_all" irá encontrar todas as tags "div" que encontrar no site, com o atributo de "class" especificado
news = soup.find_all('div', {'class': 'row my-4 d-flex'})

# Verificando se a variável está vazia
# for n in news:
#     print(n.encode('utf-8'))



# Criando função que solicita uso da API do OpenAI pelo ChatGPT

def generate_summary(prompt):
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=2048,
        n=1,
        stop=None,
        temperature=0.5,
    )
    return response.choices[0].text.strip()


# Definindo os parâmetros para o loop do Web Crawling

### Iniciando o número como indexador/ranking da lista
num = 0

### Variável de lista vazia onde serão alocados os resumos de cada noticia
resumos = []

### Adicionando linhas de código no loop para o resultado final ser salvo em um tabela Excel

workbook = Workbook(encoding = 'utf-8')
table = workbook.add_sheet('data')
line = 1

### Cria o cabeçalho de cada coluna na primeira linha da tabela

table.write(0, 0, 'number')
table.write(0, 1, 'url')
table.write(0, 2, 'title')
table.write(0, 3, 'category')
table.write(0, 4, 'date')
table.write(0, 5, 'summary')
table.write(0, 6, 'sentiment_score')
table.write(0, 7, 'sentiment')

### Baixando o conjunto de palavras irrelevantes (stop words) em português par análise de palavras-chave das notícias
nltk.download('stopwords')
nltk.download('punkt')

stop_words = set(stopwords.words('portuguese'))

### Criando função de tokeniza as palavras já retirando as stop words
def keyword_frequency(text):
    words = word_tokenize(text)
    words = [word.lower() for word in words if word.isalnum()]
    filtered_words = [word for word in words if word not in stop_words]
    return Counter(filtered_words)

# Cria uma lista vazia que irá conter todo o conteúdo das notícias compiladas
all_contents = []



# Agora realizando um loop para entrar no link de cada notícia e buscar seu conteúdo

for new in news:

    # Verificando se a tag 'h4' existe
    if new.find('h4', {'class': 'alt-font font-weight-bold my-2'}) is not None:
        # Adiciona o título dentro da classe externa da lista "news"
        title = new.find('h4', {'class': 'alt-font font-weight-bold my-2'}).get_text().strip()
    else:
        title = ''

    # Verificando se a tag 'h4' existe
    if new.find('span', {'class': 'badge badge-pill badge-primary mr-2 alt-font'}) is not None:
        # Adiciona o título dentro da classe externa da lista "news"
        category = new.find('span', {'class': 'badge badge-pill badge-primary mr-2 alt-font'}).get_text().strip()
    else:
        category = ''

    # Verificando se a tag 'em' existe
    if new.find('em', {'class': 'placeholder'}) is not None:
        # Adiciona a data dentro da classe externa da lista "news"
        news_date = new.find('em', {'class': 'placeholder'}).text.strip()
        # Formata para pegar apenas a informação da data dd/mm/YY
        news_date_parts = news_date.split(' ')
        news_date = news_date_parts[1]
    else:
        news_date = ''

    # Verificando se a tag 'a' e o atributo 'href' existem
    if new.find('a') is not None and 'href' in new.find('a').attrs:
        # Adiciona a URL da notícia dentro da classe externa da lista "news"
        urls = 'https://agenciabrasil.ebc.com.br' + new.find('a')['href']
    else:
        urls = ''

    # Para cada loop completo adiciona mais um número no indexador/ranking
    num += 1

    # Aloca em variável a resposta do link de cada notícia com uso do 'requests'
    new_f = requests.get(urls, headers=headers)

    # Transforma em objeto BeautifulSoup
    new_soup = BeautifulSoup(new_f.content, 'lxml')

    # Verificando se a tag 'div' e o atributo 'class' existem
    if new_soup.find('div', {'class': 'post-item-wrap'}) is not None:
        # Busca o conteúdo da notícia pelo trecho do HTML devido
        new_content = new_soup.find('div', {'class': 'post-item-wrap'}).get_text().strip()
        # Limita o conteúdo a 4090 caracteres devido ao limite do modelo GPT
        new_content = new_content[:4090]
        # Compila a notícia na lista para a análise de palavras-chave
        all_contents.append(new_content)

    else:
        new_content = ''

    # Cria resumo de cada notícia com a função do ChatGPT
    resumo = generate_summary(f"Esta é uma notícia do dia. Resuma os acontecimentos mais relevantes em um breve parágrafo: {new_content}")
    # resumos.append(resumo)

    # Calcula a análise de sentimento com base no texto da notícia
    sentiment_score = TextBlob(new_content).sentiment.polarity

    # Classifica a análise de sentimento (polarity)
    if sentiment_score >= 0.05:
        sentiment = 'positive'
    
    elif -0.05 < sentiment_score < 0.05:
        sentiment = 'neutral'
    
    else:
        sentiment = 'negative'

    # Salva o dado extraído no Excel a partir da segunda linha
    table.write(line, 0, num)
    table.write(line, 1, urls)
    table.write(line, 2, title)
    table.write(line, 3, category)
    table.write(line, 4, news_date)
    table.write(line, 5, resumo)
    table.write(line, 6, sentiment_score)
    table.write(line, 7, sentiment)
    line += 1

# Salva o arquivo Excel no computador
workbook.save('agencia_brasil_news_chatgpt_5.xls')


# ----- ANÁLISE DE PALAVRAS-CHAVE -----

## Cria um DataFrame a partir da lista all_contents
content_df = pd.DataFrame(all_contents, columns=['new_content'])

## Calcula a frequência das palavras-chave com função de tokenização criada
content_df['keywords'] = content_df['new_content'].apply(keyword_frequency)

## Combina as frequências de palavras-chave de todas as notícias
combined_keywords = content_df['keywords'].sum()

## Salve a frequência das palavras-chave em um arquivo Excel
keywords_df = pd.DataFrame(combined_keywords.most_common(), columns=['Keyword', 'Frequency'])
keywords_df.to_excel('keywords_frequency_5.xlsx', index=False)