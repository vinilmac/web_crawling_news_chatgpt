import requests
import lxml
from bs4 import BeautifulSoup
from xlwt import *
import os
import sys
import openai


sys.stdout.reconfigure(encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'UTF-8'

# Inserir chave API do OpenAI
openai.api_key = "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"


# Site que queremos realizar o Web Crawling
url = "https://agenciabrasil.ebc.com.br/ultimas"

# As vezes a página possui um "anti-crawler setting" para evitar coleta maliciosa de dados da página
# Para resolver, utilizamos o parâmetro de headers que irá simular a informação inicial da página
headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/63.0.3239.132 Safari/537.36 QIHU 360SE'}

# Resposta do link dado com uso do 'requests'
f = requests.get(url, headers = headers)

# Conteúdo da resposta do link dado
page_content = f.content

# Criando um objeto em BeautifulSoup do HTML do site. Ele irá pegar o HTML do site e quebrar em objetos Python
soup = BeautifulSoup(f.content,'lxml')


# movies = soup.find('table',{'class':'table'}).find_all('a')

# O "find_all" irá encontrar todas as tags "div" que encontrar no site, com o atributo de "class" especificado
news = soup.find_all('div', {'class': 'row my-4 d-flex'})

# for n in news:
#     print(n.encode('utf-8'))


# Agora realizando um loop para entrar no link de cada notícia e buscar seu conteúdo

# Iniciando o número como indexador/ranking da lista
num = 0


# Inicializa a variável para armazenar todas as notícias em um texto único
all_news = ""

for new in news:

    # Verificando se a tag 'h4' existe
    if new.find('h4', {'class': 'alt-font font-weight-bold my-2'}) is not None:
        # Adiciona o título dentro da classe externa da lista "news"
        title = new.find('h4', {'class': 'alt-font font-weight-bold my-2'}).get_text().strip()
    else:
        title = ''

    # Verificando se a tag 'em' existe
    if new.find('em', {'class': 'placeholder'}) is not None:
        # Adiciona a data dentro da classe externa da lista "news"
        news_date = new.find('em', {'class': 'placeholder'}).text.strip()
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
    else:
        new_content = ''

    # Adiciona o título e o conteúdo da notícia ao texto único
    all_news += f"{title}: {new_content}\n\n"


# Solicita o resumo das notícias usando a API do OpenAI
def generate_summary(prompt):
    response = openai.Completion.create(
        engine="text-davinci-002",
        prompt=prompt,
        max_tokens=150,
        n=1,
        stop=None,
        temperature=0.5,
    )
    return response.choices[0].text.strip()

# Prepara o prompt com todas as notícias
prompt = f"Estas são as notícias do dia. Resuma os acontecimentos mais relevantes em poucos bullet points: {all_news}"

# Gera o resumo
summary = generate_summary(prompt)

print("\nResumo dos acontecimentos mais relevantes:")
print(summary)