# nba-videorulebook-dl - Download the video rulebook of NBA

# ******************************************************************* #
# Copyright (C) 2021 Raffaele Mancuso
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
# ******************************************************************* #

# Call this script from the command line like
# scrapy runspider main.py
    
import scrapy
import scrapy.exceptions
import os
import subprocess
import logging

basepath = "./vids"

def norm_str(s):
    return s.replace("\n","").replace("\\","_").replace("/","_").replace("\"","").replace("'","").strip()

class NBAVRBSpider(scrapy.Spider):
    name = 'nba-vrb'
    start_urls = ['https://videorulebook.nba.com']

    def __init__(self):
        logging.getLogger('scrapy').setLevel(logging.WARNING)
        self.download_delay = 1

    def parse(self, response):
        for rule in response.css('li.menu-item-has-children'):
            self.parse(rule)
        for rule in response.css('li:not(.menu-item-has-children)'):
            yield response.follow(rule.css('a')[0], self.parseRule)

    def parseRule(self, response):
        crumbs = list()
        for crumb in response.css("div.rule-breadcrumb > div.rule-crumb"):
            crumbs.append(crumb.css("::text").get().replace("/","-"))
        path = os.path.join(*crumbs)
        print(path)
        path = os.path.join(basepath, path)
        os.makedirs(path, exist_ok=True)
        for videothumb in response.css('.video-thumbnail'):
            meta = {"path": path}
            yield response.follow(videothumb.css('a')[0], self.parseVideo, meta=meta)

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

            filepath = os.path.join(path, title + ".mp4")
            print("PATH: '{}'\nLINK: '{}'\nTITLE:\n'{}'\nFILEPATH:'{}'".format(path,link,title,filepath))

            command = ['wget','--no-check-certificate','-O',filepath,link]
            if not os.path.isfile(filepath):
                subprocess.call(command)
            else:
                print("File already exist")
            yield None
