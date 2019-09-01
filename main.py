# nba-videorulebook-dl - Download the video rulebook of NBA
# Copyright (C) 2019 Raffaele Mancuso

# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.

# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.

# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <https://www.gnu.org/licenses/>.
    
import scrapy
import scrapy.exceptions
import os
import subprocess
import logging

basepath = "./vids5"

def norm_str(s):
    return s.replace("\n","").replace("\\","_").replace("/","_").replace("\"","").replace("'","").strip()

class NBAVRBSpider(scrapy.Spider):
    name = 'nba-vrb'

    start_urls = ['http://videorulebook.nba.com']

    def __init__(self):
        logging.getLogger('scrapy').setLevel(logging.WARNING)
        self.download_delay = 1
        pass

    def parse(self, response):
        for rule in response.css('.menu-item-type-taxonomy'):
            yield response.follow(rule.css('a')[0], self.parseRule)

    def parseRule(self, response):
        for videothumb in response.css('.video-thumbnail'):
            breadcrumb = response.css('div.rule-breadcrumb')
            if breadcrumb:
                path = "./vids5"
                section_text = ""
                for text in breadcrumb.xpath("//div[contains(@class,'rule-crumb')]/text()").extract():
                    section_text += "/" + norm_str(text)
                path += section_text
                meta = {"path":path}
                print("Scraping: {}".format(section_text))
                yield response.follow(videothumb.css('a')[0], self.parseVideo, meta=meta)
            else:
                print("ERROR: breadcrumb is not valid. URL='{}'".format(response.request.url))
                raise scrapy.exceptions.CloseSpider('invalid_breadcrumb')


    def parseVideo(self, response):
        path = response.meta['path']
        for video in response.css('video'):

            link = video.css('source::attr(src)').extract_first()

            title = ""
            h1_title = response.xpath("//h1[contains(concat('  ',normalize-space(@class),'  '), ' entry-title ')]/text()")
            for text in h1_title.extract():
                title += norm_str(text)

            if title=='':
                print("FATAL ERROR: title not found. URL='{}'".format(response.request.url))
                raise scrapy.exceptions.CloseSpider('no_title')

            os.makedirs(path, exist_ok=True)

            filepath = path + "/" + title + ".mp4"
            print("PATH: '{}'\nLINK: '{}'\nTITLE:\n'{}'\nFILEPATH:'{}'".format(path,link,title,filepath))

            command = ['wget','-O',filepath, link]
            if not os.path.isfile(filepath):
                subprocess.call(command)
            else:
                print("File already exist")
            yield None
