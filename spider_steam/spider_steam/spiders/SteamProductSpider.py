import scrapy
from bs4 import BeautifulSoup as BS
import requests
from spider_steam.items import SpiderSteamItem


def get_urls():
    start_urls = set()
    queries = ['america', 'vs', 'ussr']
    for query in queries:
        for i in range(1, 3):
            page = 'https://store.steampowered.com/search/?term=' + str(query) + '&ignore_preferences=1&page=' + str(i)
            soup = BS(requests.get(page).content.decode('utf-8'), 'html.parser')
            root = soup.find('div', {'id': 'search_resultsRows'})
            for game_tag_a in root.find_all('a'):
                game_url = game_tag_a.get('href')
                if game_url is not None and game_url not in start_urls:
                    start_urls.add(game_url)
    return list(start_urls)


class SteamproductspiderSpider(scrapy.Spider):
    name = 'SteamProductSpider'
    allowed_domains = ['store.steampowered.com']
    start_urls = get_urls()

    def parse(self, response):
        games = SpiderSteamItem()

        name = list(map(lambda x: x.strip(), response.xpath('//div[@id="appHubAppName"][@class="apphub_AppName"]/text()').extract()))
        category = list(map(lambda x: x.strip(), response.xpath('//div[@class="blockbg"]/a/text()').extract()))
        review_number = list(map(lambda x: x.strip(), response.xpath(
            '//div[@itemprop="aggregateRating"]/div[@class="summary column"]/span[@class="responsive_hidden"]/text()').extract()))
        total_review = list(map(lambda x: x.strip(), response.xpath(
            '//div[@itemprop="aggregateRating"]/div[@class="summary column"]/span[@class="game_review_summary positive"]/text()').extract()))
        release_date = list(map(lambda x: x.strip(), response.xpath('//div[@class="release_date"]/div[@class="date"]/text()').extract()))
        developer = list(map(lambda x: x.strip(), response.xpath('//div[@class="dev_row"]/div[@id="developers_list"]/a/text()').extract()))
        tags = list(map(lambda x: x.strip(), response.xpath('//div[@class="glance_tags popular_tags"]/a/text()').extract()))
        price = list(map(lambda x: x.strip(), response.xpath('//div[@class="game_purchase_price price"]/text()').extract()))
        platforms = list(map(lambda x: x.strip(), response.xpath('//div[@class="sysreq_tabs"]/div/text()').extract()))
        games['name'] = ''.join(name)
        games['category'] = '/'.join(category[1:])
        games['review_cnt'] = ''.join(str(review_number).strip('(\'[').strip(']\')'))
        games['total_review'] = ''.join(total_review)
        games['release_date'] = ''.join(release_date)
        games['developer'] = ','.join(developer)
        games['tags'] = ', '.join(tags)
        games['price'] = ''.join(price).replace('\u0443\u0431', '')
        games['platforms'] = ', '.join(platforms)

        if len(name) != 0 and len(name[0]) != 0 and len(games['release_date']) > 0 and games['release_date'].split()[-1] > '2000':
            yield games

