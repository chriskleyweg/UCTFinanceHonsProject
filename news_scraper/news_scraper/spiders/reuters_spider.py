# -*- coding: utf-8 -*-
import scrapy
import os
import json

class ReutersSpider(scrapy.Spider):
    name = "reuters"

    def __init__(self, *a, **kw):
        super(ReutersSpider, self).__init__(*a, **kw)

    def start_requests(self):
        base_url = 'http://www.reuters.com/resources/archive/us/'
        # years = [2007,2008,2009,2010,2011,2012,2013,2014,2015,2016,2017]
        years = [2018]

        for year in years:
            url = base_url+str(year)+'.html'
            yield scrapy.Request(url=url, callback=self.parse_year)

    def parse_year(self, response):
        days = response.xpath("//p/a[starts-with(@href, \
                              '/resources/archive/us/')]")
        for day in days:
            day_url = day.xpath('@href').extract_first()
            date = day_url.split("/")[-1][:-5] # e.g. 20160130
            item = {'date':date}
            yield scrapy.Request(url=response.urljoin(day_url), \
                                 callback=self.parse_day, meta={'item':item})

    def parse_day(self, response):
        articles = response.xpath("//div/a[starts-with(@href, \
                              'http://www.reuters.com/article/')]")
        for article in articles:
            article_link = article.xpath("@href").extract_first()
            article_title = article.xpath("text()").extract_first()
            item = response.meta['item']
            item['title'] = article_title
            yield scrapy.Request(url=response.urljoin(article_link), \
                                 callback=self.parse_article, \
                                 meta={'item':item})

    def parse_article(self, response):
        item = response.meta['item']
        section = response.xpath("//div[contains(@class, 'ArticleHeader_channel')]\
                                 /a/text()").extract_first().replace(" ", "_")
        title = response.xpath("//h1[contains(@class, 'ArticleHeader_headline')]//text()").extract_first()
        texts = '-'.join(list(map(lambda x: x.strip(),response.xpath("//div[contains(@class, 'StandardArticleBody')]//text()").extract())))
        date = item['date']
        yield {
            'title':title, 
            'section':section,
            'date':date, 
            'text':texts,
            'url':response.url,
        }