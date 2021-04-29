import json

import requests
import validators
from ibm_cloud_sdk_core import ApiException
from ibm_watson import NaturalLanguageUnderstandingV1
from ibm_cloud_sdk_core.authenticators import IAMAuthenticator
from ibm_watson.natural_language_understanding_v1 import Features, SentimentOptions
from bs4 import BeautifulSoup
from texttable import Texttable


def hacker_news():
    res = requests.get('https://news.ycombinator.com/')
    res2 = requests.get('https://news.ycombinator.com/news?p=2')

    soup = BeautifulSoup(res.text, 'lxml')
    soup2 = BeautifulSoup(res2.text, 'lxml')
    soup.extend(soup2)

    table = Texttable()
    table.header(["Title", "Score", "Label", "Url"])
    new = {}
    for row in soup.select('.storylink'):
        new['title'] = row.text
        if validators.url(row['href']):
            new['link'] = row['href']
        else:
            new['link'] = 'https://news.ycombinator.com/'

        try:
            sentiment = watson_sentiment(new['title'], new['link'])
        except ApiException:
            pass

        sentiment_parsed = json.loads(sentiment)
        document = sentiment_parsed.get('sentiment').get('document')
        new['score'] = document.get('score')
        new['label'] = document.get('label')

        table.add_row([new.get('title'), new.get('score'), new.get('label'), new.get('link')])

    print(table.draw())


def watson_sentiment(text, url):
    authenticator = IAMAuthenticator('0_SepkwXTRuZRpteu33Nvaysd9_9RsHau0agMWM55cTR')
    natural_language_understanding = NaturalLanguageUnderstandingV1(
        version='2020-08-01',
        authenticator=authenticator
    )
    natural_language_understanding.set_service_url(
        'https://api.us-east.natural-language-understanding.watson.cloud.ibm.com/instances/e033c704-a77e-4890-9397-1ebffdba0a98')
    response = natural_language_understanding.analyze(
        url=url,
        features=Features(sentiment=SentimentOptions(targets=text.split(' ')))).get_result()
    return json.dumps(response, indent=2)


if __name__ == '__main__':
    hacker_news()
