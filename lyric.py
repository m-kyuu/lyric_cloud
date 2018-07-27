from bs4 import BeautifulSoup
import requests
from urllib.parse import urljoin
from tqdm import tqdm
from time import sleep
import MeCab

_BASE_URL = 'http://j-lyric.net'


def get_lyric(url):
    r = requests.get(url)
    r.encoding = r.apparent_encoding
    soup = BeautifulSoup(r.text, 'html.parser')
    lyric = soup.find('p', id='Lyric')
    [br.extract() for br in lyric.find_all('br')]
    return ' '.join(lyric.get_text().split())


def get_link():
    r = requests.get('http://j-lyric.net/artist/a000eac/')
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
        if speech in ['名詞', '形容詞']:
            tokens.append(surface if base_form == '*' else base_form)
    return ' '.join(tokens)


if __name__ == '__main__':
    # urls = get_link()
    # lyrics = []
    # for url in tqdm(urls):
    #     lyrics.append(get_lyric(url))
    #     sleep(2)
    # lyrics = ' '.join(lyrics)
    # with open('arashi_lyric.txt', 'w', encoding='utf-8') as f:
    #     f.write(lyrics)
    with open('arashi_lyric.txt', 'r', encoding='utf-8') as f:
        data = f.read()
    data = data.split()
    tokens = [tokenizer(text) for text in data]
    tokens = ' '.join([word.strip() for word in tokens])
    with open('lyric_tokens.txt', 'w', encoding='utf-8') as f:
        f.write(tokens)

