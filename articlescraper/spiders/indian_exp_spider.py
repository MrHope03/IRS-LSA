from pathlib import Path

import scrapy


class IndianExpSpider(scrapy.Spider):
    name = "indian-express"
    start_urls = [
        'https://indianexpress.com/section/india/',
        'https://indianexpress.com/section/entertainment/',
        'https://indianexpress.com/section/political-pulse/',
        'https://indianexpress.com/section/technology/',
        'https://indianexpress.com/section/sports/'
    ]

    def parse(self, response):
        for newsItem in response.css('div.articles'):
            href = newsItem.css('h2 a::attr(href)').get()
            yield from self.downloader(response, newsItem, href)

    def downloader(self, response, newsItem, href):
            contentPage = response.follow(
                href, callback=self.extractor, cb_kwargs=dict())
            contentPage.cb_kwargs['heading'] = newsItem.css(
                'h2.title a::text').get()
            contentPage.cb_kwargs['author'] = ""
            contentPage.cb_kwargs['publish_date'] = newsItem.css(
                'div.date::text').get()
            contentPage.cb_kwargs['overview'] = newsItem.css(
                'p::text').get()
            contentPage.cb_kwargs['link'] = newsItem.css(
                'h2.title a::attr(href)').get()
            yield contentPage
            yield from self.navigator(response)

    def navigator(self, response):
            nextPage = response.css(
                'ul.page-numbers a.next::attr(href)').get()
            if nextPage is not None:
                yield response.follow(nextPage, callback=self.parse)

    def extractor(self, response, heading, author, publish_date, overview, link):
        yield {
            'heading': heading,
            'author': author,
            'publish_date': publish_date,
            'overview': overview,
            'link': link,
            'content': response.css('div.full-details p::text').getall()
        }
