import pandas as pd
from wordcloud import WordCloud
import matplotlib.pyplot as plt

# Carrega o arquivo Excel
df = pd.read_excel('keywords_frequency_all_pages.xlsx')

# Cria um dicionário de palavras e suas frequências
word_freq = dict(zip(df['Keyword'], df['Frequency']))

# Cria a nuvem de palavras com cores pastéis
wordcloud = WordCloud(background_color='white',
                      colormap=plt.cm.inferno,
                      width=800, height=400).generate_from_frequencies(word_freq)

# Plota a nuvem de palavras
plt.figure(figsize=(12,6))
plt.imshow(wordcloud, interpolation='bilinear')
plt.axis('off')
plt.tight_layout()

# Salva a imagem na pasta atual
plt.savefig('nuvem_palavras.png', dpi=300)
