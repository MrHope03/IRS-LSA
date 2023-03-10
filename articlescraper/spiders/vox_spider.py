from pathlib import Path

import scrapy


class VoxSpider(scrapy.Spider):
    name = "vox"
    start_urls = [
        'https://www.vox.com/culture/archives',
        'https://www.vox.com/politics/archives',
        'https://www.vox.com/science/archives',
        'https://www.vox.com/technology/archives',
        'https://www.vox.com/climate/archives',
        'https://www.vox.com/health/archives',
        'https://www.vox.com/money/archives'
    ]

    def parse(self, response):
        for newsItem in response.css('div.c-compact-river__entry'):
            href = newsItem.css(
                'h2.c-entry-box--compact__title a::attr(href)').get()
            yield from self.downloader(response, newsItem, href)

    def downloader(self, response, newsItem, href):
            contentPage = response.follow(
                href, callback=self.parse_inside, cb_kwargs=dict())
            contentPage.cb_kwargs['heading'] = newsItem.css(
                'h2.c-entry-box--compact__title a::text').get()
            contentPage.cb_kwargs['author'] = newsItem.css(
                'span.c-byline__author-name::text').get()
            contentPage.cb_kwargs['publish_date'] = newsItem.css(
                'time::text').get()
            contentPage.cb_kwargs['overview'] = ""
            contentPage.cb_kwargs['link'] = newsItem.css(
                'h2.c-entry-box--compact__title a::attr(href)').get()
            yield contentPage
            yield from self.navigator(response)

    def navigator(self, response):
            nextPage = response.css(
                'nav.c-pagination a.c-pagination__next::attr(href)').get()
            if nextPage is not None:
                yield response.follow(nextPage, callback=self.parse)

    def parse_inside(self, response, heading, author, publish_date, overview, link):
        yield {
            'heading': heading,
            'author': author,
            'publish_date': publish_date,
            'overview': overview,
            'link': link,
            'content': response.css('div.c-entry-content > p::text').getall()
        }
