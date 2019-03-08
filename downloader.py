#!/usr/bin/env python3

import asyncio
import os
import pyppeteer
import random
import re
import requests
import shutil
import time

comic_url = 'https://manhua.dmzj.com/qybsdyj'
download_path = '~/Downloads'
max_sleep_time = 10

BASE_HEADERS = { 'user-agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_14_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/72.0.3626.119 Safari/537.36', 'referer': comic_url }
BASE_URL = 'https://manhua.dmzj.com'
REG_TIT = r'<span class="anim_title_text"><a href=".*?"><h1>(.*?)</h1></a></span>' # comic name
REG_DES = r'<meta name=\'description\' content=".*?(介绍.*?)"/>' # description
REG_COV = r'src="(.*?)" id="cover_pic"/></a>' # conver
REG_CHA = r'<li><a title="(.*?)" href="(.*?)" .*?>.*?</a>' # chapters

def mkdir(name):
    try:
        os.mkdir(name, 0o755)
    except FileExistsError:
        pass

def sleep(n=max_sleep_time):
    waiting = random.randrange(1, n)
    print('waiting for %d seconds' % waiting)
    time.sleep(waiting)

def download_img(full_url, save_path, headers=BASE_HEADERS):
    sleep()
    print('downloading %s...' % save_path)
    r = requests.get(full_url, headers=headers, stream=True)
    if r.status_code == 200:
        with open(save_path, 'wb') as f:
            r.raw.decode_content = True
            shutil.copyfileobj(r.raw, f)

async def get_pages(url):
    browser = await pyppeteer.launch()
    page = await browser.newPage()
    await page.goto(url)
    pages = await page.evaluate('''() => {
        const options = document.querySelectorAll('#page_select option')
        return Array.prototype.map.call(options, option => option.value)
    }''')
    await browser.close()
    return list(map(lambda page: 'http:%s' % page, pages))

async def main():
    comic_res = requests.get(comic_url, headers=BASE_HEADERS).text
    comic_title = re.findall(REG_TIT, comic_res)[0]
    comic_description = re.findall(REG_DES, comic_res)[0]
    comic_cover = re.findall(REG_COV, comic_res)[0]
    comic_chapters = re.findall(REG_CHA, comic_res)
    comic_path = os.path.expanduser('%s/%s' % (download_path, comic_title))

    mkdir(comic_path)
    download_img(comic_cover, '%s/cover.jpg' % comic_path)
    with open('%s/about.txt' % comic_path, 'w') as out:
        out.write(comic_description + '\n')

    for (chapter_name, chapter_url) in comic_chapters:
        chapter_path = '%s/%s' % (comic_path, chapter_name)
        chapter_full_url = '%s%s' % (BASE_URL, chapter_url)
        mkdir(chapter_path)

        sleep()
        print('dealing with %s...' % chapter_name)

        chapter_pages = await get_pages(chapter_full_url)
        page_num = 0
        for page_url in chapter_pages:
            page_path = '%s/%d.jpg' % (chapter_path, page_num)
            page_header = { **BASE_HEADERS, 'referer': '%s#@page=%d' % (chapter_full_url, page_num + 1) }
            download_img(page_url, page_path, page_header)
            page_num += 1

asyncio.get_event_loop().run_until_complete(main())
