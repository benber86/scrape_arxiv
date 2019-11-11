import requests
import lxml.html
import unicodedata
import re
import unidecode
import os
import json

METADATA_FILE_NAME = 'metadata.json'
ARTICLE_FILE_NAME = 'article.pdf'

class ArxScraper():
    
    def __init__(self, save_folder):
        
        self.save_folder = save_folder
        
    @staticmethod
    def sanitize_name(value):
        value = unicodedata.normalize('NFKD', value).encode('ascii', 'ignore').decode('utf8')
        value = unidecode.unidecode(re.sub('[^\w\s-]', '', value).strip().lower())
        value = unidecode.unidecode(re.sub('[-\s]+', '-', value))
        return value[:250]
        
    def fetch_all(self, link):
        r = requests.get(link)
        tree = lxml.html.fromstring(r.content)
        metadata = {}
        metadata['title'] = tree.xpath('//meta[@name="citation_title"]')[0].get("content")
        metadata['authors'] = [author.get("content") for author in tree.xpath('//meta[@name="citation_author"]')]
        metadata['date'] = tree.xpath('//meta[@name="citation_date"]')[0].get("content")
        metadata['abstract'] = tree.xpath('//meta[@property="og:description"]')[0].get("content")
        pdf_link = tree.xpath('//meta[@name="citation_pdf_url"]')[0].get("content")
        pdf_data = requests.get(pdf_link).content
        folder_name = self.sanitize_name(metadata['date'][:4] + metadata['title'])
        save_path = os.path.join(self.save_folder, folder_name)
        os.makedirs(save_path, exist_ok=True)
        pdf_file_path = os.path.join(save_path, ARTICLE_FILE_NAME)
        json_file_path = os.path.join(save_path, METADATA_FILE_NAME)
        with open(pdf_file_path, 'wb') as fp:
            fp.write(pdf_data)
            
        with open(json_file_path, 'w') as fp:
            json.dump(metadata, fp)
        
    
    def scrape(self, link_list):

        if type(link_list) is str:
            link_list = [link_list]

        for link in link_list:
            print('fetching %s' % link)
            try:
                self.fetch_all(link)
            except Exception as e:
                print('Error with %s' % link)
            
            
        
        