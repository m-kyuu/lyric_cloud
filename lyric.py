from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
from tqdm import tqdm
from time import sleep
import MeCab
import matplotlib.pyplot as plt
from wordcloud import WordCloud
import logging

_BASE_URL = 'http://j-lyric.net'

logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.INFO)


def get_lyric(url):
    r = requests.get(url)
    r.encoding = r.apparent_encoding
    soup = BeautifulSoup(r.text, 'html.parser')
    lyric = soup.find('p', id='Lyric')
    [br.extract() for br in lyric.find_all('br')]
    return ' '.join(lyric.get_text().split())


def get_link():
    r = requests.get('http://j-lyric.net/artist/a001c7a/')
    soup = BeautifulSoup(r.text, 'html.parser')
    url = []
    for song in soup.find_all('p', 'ttl'):
        url.append(urljoin(_BASE_URL, song.find('a').get('href')))
    return url


def tokenizer(text):
    m = MeCab.Tagger()
    tokens_raw = [raw for raw in m.parse(str(text)).split('\n') if raw not in ('EOS', '')]
    tokens = []
    for raw in tokens_raw:
        surface, feature = raw.split('\t')
        feature = feature.split(',')
        speech = feature[0]
        base_form = feature[6]
        if speech in ['名詞', '形容詞', '動詞']:
            tokens.append(surface if base_form == '*' else base_form)
    return ' '.join(tokens)


def create_cloud(text):
    stop_words = [
        'ん', 'よう', '(', ')', 'ない', 'てる', 'いる', 'なる', 'れる', 'する', 'ある',
        'こと', 'そう', 'せる', 'した', 'いい', 'くれる', 'られる'
    ]
    fpath= 'C:\\Windows\\Fonts\\HGRSGU.TTC'
    wordcloud = WordCloud(font_path=fpath, background_color="white", width=900, height=500, colormap="Pastel2", stopwords=set(stop_words))
    wordcloud.generate(text)
    wordcloud.to_file('wordcloud/mc_pastel.png')
    plt.figure()
    plt.imshow(wordcloud)
    plt.axis('off')
    plt.show()


if __name__ == '__main__':
    urls = get_link()
    lyrics = []
    logging.info('Started crawling.')
    for url in tqdm(urls):
        lyrics.append(get_lyric(url))
        sleep(2)
    lyrics = ' '.join(lyrics)
    with open('mc_lyric.txt', 'w', encoding='utf-8') as f:
        f.write(lyrics)
    logging.info('Saved lyrics.')

    with open('mc_lyric.txt', 'r', encoding='utf-8') as f:
        data = f.read()
    data = data.split()
    logging.info('Started tokenizing.')
    tokens = [tokenizer(text) for text in data]
    tokens = ' '.join([word.strip() for word in tokens])
    with open('mc_tokens.txt', 'w', encoding='utf-8') as f:
        f.write(tokens)
    logging.info('Saved tokens.')

    with open('mc_tokens.txt', 'r', encoding='utf-8') as f:
        text = f.read()
    create_cloud(text)
    logging.info('Created wordcloud.')
