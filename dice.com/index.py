from scrapy import Spider
from scrapy.selector import Selector
from selenium import webdriver
from scrapy.http import TextResponse
from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings

import scrapy
import unicodecsv as csv
import requests
from datetime import date
from datetime import datetime
import json
import hashlib

class Dice(scrapy.Spider):
    name = 'Dice'
    allowed_domains = ['dice.com']
    start_urls=['https://www.dice.com/jobs/q-Python-limit-120-l-New york,NY-radius-30-startPage-1-limit-120-jobs?searchid=291607343849']
    category='Python'
    def __init__(self):
        self.options = webdriver.ChromeOptions()
        # self.options.add_argument('headless')
        self.options.add_argument('--start-maximized')
        self.driver = webdriver.Chrome(chrome_options=self.options)

    def parse(self, response):

        self.driver.get(response.url)
        urls = []
        properties_list = []
        for i in range(1,2):
            AllResult=self.driver.find_elements_by_class_name("complete-serp-result-div")
            i1=0
            URLLIST=[]
            for AR in AllResult:
                ii1=str(i1)
                path="//*[@id='position"+ii1+"']/span"
                path1="//*[@id='position"+ii1+"']"
                title=''
                
                try:
                    title=AR.find_element_by_xpath(path).text
                except Exception as d:
                    print('')
                link=''
                try:
                    link=AR.find_element_by_xpath(path1).get_attribute("href")
                    
                except Exception as d:
                    print('')
                company=''
                
                try:
                    company=AR.find_element_by_class_name("compName").text
                except Exception as d:
                    print('')
                location=''
                
                try:
                    location=AR.find_element_by_class_name("jobLoc").text
                except Exception as d:
                    print('')
                posted_time=''
                try:
                    posted_time=AR.find_element_by_class_name("posted").text
                except Exception as d:
                    print('')
                description=''
                raw_desc=''
                try:
                    description=AR.find_element_by_class_name("shortdesc").text
                    raw_desc=AR.find_element_by_class_name("shortdesc").get_attribute('innerHTML')
                except Exception as d:
                    print('')

                crawled_time=str(datetime.now())
                desc_hash = hashlib.sha256(description.encode('utf-8'))
                hash_id = desc_hash.hexdigest()
                data = {'job_id': hash_id,'crawled_time':crawled_time,'category':self.category,'source':self.name,'title' : title,'company':company,'location':location,'job_date':posted_time,'description':description,'link':link}
                properties_list.append(data)
                i1=i1+1
            try:
                next_page = self.driver.find_element_by_xpath('//*[@title="Go to next page"]')
                next_page.click()
            except Exception as d:
                print('')
            
        for ro in properties_list:
            yield scrapy.Request(ro['link'], callback=self.parse_listing, meta=ro)
        self.driver.close()
    def parse_listing(self, response):
            raw_desc = response.xpath('//*[@id="bd"]/div[2]/div[1]/div[5]').extract_first()
            job_desc = response.xpath('//*[@id="jobdescSec"]').extract()
            job_type = response.xpath('//*[@id="bd"]/div[2]/div[1]/div[1]/div/div[2]/text()').extract()
            company_desc = response.xpath('//*[@id="bd"]/div[2]/div[1]/div[9]/div/div/text()').extract()

            yield {'job_id': response.meta['job_id'], 'title': response.meta['title'], 'company': response.meta['company'],
                'location': response.meta['location'], 'raw_desc': raw_desc,
                'job_desc': job_desc, 'job_type': job_type, 
                'company_desc': company_desc, 'category': response.meta['category'],
                'job_date': response.meta['job_date'], 'crawled_time': response.meta['crawled_time'], 
                'link': response.meta['link'], 'source': response.meta['source']}

FileName=input('Enter Json File Name: ')

s = get_project_settings()
s['USER_AGENT']='Mozilla/5.0'
s['FEED_FORMAT'] = 'json'
s['LOG_LEVEL'] = 'INFO'
s['FEED_URI'] = FileName+'.json'
s['LOG_FILE'] = FileName+'-Log.json'

process = CrawlerProcess(s)
process.crawl(Dice)
process.start()



