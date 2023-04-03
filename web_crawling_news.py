import requests
import lxml
from bs4 import BeautifulSoup
from xlwt import *
import os
import sys

sys.stdout.reconfigure(encoding='utf-8')
os.environ['PYTHONIOENCODING'] = 'UTF-8'


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

    print(num, urls, news_date, '\n', 'Título da notícia:', title)
    print('Notícia completa:', new_content.encode('utf-8', 'ignore').decode('utf-8'))



# Adicionando linhas de código no loop para o resultado final ser salvo em um tabela Excel

workbook = Workbook(encoding = 'utf-8')

table = workbook.add_sheet('data')

# Cria o cabeçalho de cada coluna na primeira linha da tabela
table.write(0, 0, 'number')
table.write(0, 1, 'url')
table.write(0, 2, 'title')
table.write(0, 3, 'date')
table.write(0, 4, 'article')

# Iniciando o loop final

num = 0
line = 1

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
    
    # Salva o dado extraído no Excel a partir da segunda linha
    table.write(line, 0, num)
    table.write(line, 1, urls)
    table.write(line, 2, title)
    table.write(line, 3, news_date)
    table.write(line, 4, new_content)
    line += 1


# Salva o arquivo Excel no computador
workbook.save('agencia_brasil_news.xls')