import time
import pickle
import pathlib
import aiohttp
import asyncio
import requests
import xmltodict

import utils

from bs4 import BeautifulSoup

sem = asyncio.Semaphore(5)


async def text_from_url(session, url):
    async with sem:
        async with session.get(url["loc"]) as response:
            raw_html = await response.text()
            soup = BeautifulSoup(raw_html, "html.parser")
            article_lead = soup.find(attrs={"class": "article-lead"})
            article_body = soup.find(attrs={"class": "article__body"})
            article_text = ""

            if article_lead:
                article_text += article_lead.text

            if article_body:
                article_text += article_body.text

            if len(article_text) > 1:
                return article_text
            return None


def get_xml_content(xml_url: str):
    response = requests.get(xml_url)
    return xmltodict.parse(response.content)


async def main():
    async with aiohttp.ClientSession() as session:
        config = utils.load_config()

        lsm_text_path = config["lsm-text-path"]
        if pathlib.Path(lsm_text_path).exists():
            pathlib.Path.unlink(lsm_text_path)

        sitemap_url = config["sitemap"]
        root = get_xml_content(sitemap_url)

        article_texts = []

        # -1 ignores master.xml
        branches = root["sitemapindex"]["sitemap"][:-1]

        num_branches = len(branches)
        print(f"Number of branches: {num_branches}")
        for bcount, branch in enumerate(branches[::-1][:1]):
            print(f"Branch {bcount + 1}/{num_branches}")
            loc_xml = branch["loc"]

            loc_leaves = get_xml_content(loc_xml)

            urlset = loc_leaves["urlset"]

            urls = urlset["url"]
            if type(urls) == dict:
                urls = [urls]

            num_urls = len(urls)
            print(f"Number of articles to review: {num_urls}")

            results = await asyncio.gather(
                *[text_from_url(session, url) for url in urls]
            )

            with open(lsm_text_path, "a", encoding="utf-8") as file:
                for text in results:
                    if text:
                        file.write(text)
                        file.write("\n")

            article_texts = [text for text in results if text]
            print(f"Read {len(article_texts)} urls")


if __name__ == "__main__":
    time_start = time.time()
    asyncio.run(main())
    time_end = time.time()

    print(f"Execution time: {time_end - time_start}s")
