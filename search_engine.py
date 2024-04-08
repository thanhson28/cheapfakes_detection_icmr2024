import datetime
from selenium import webdriver
from webdriver_manager.chrome import ChromeDriverManager
from urllib.parse import urlencode, unquote
from bs4 import BeautifulSoup
import urllib.request
from selenium.webdriver.common.by import By

root_path ="./"

class SearchByImageInstance:
    url = "https://www.google.com/searchbyimage?"
    # url = "https://www.google.com/searchbyimage/upload"
    client = "firefox-b-d"
    pagination = 10
    lang = "en"

    ERROR =  "This page appears when Google "\
            +"automatically detects requests "\
            +"coming from your computer network"
    DEV_STUB = False

    def __init__(self):
        pass


    def search(self, uploaded_im_url, limit_page=None):
        # first_image = driver.find_element_by_xpath("//img[@class="rg_i"]")
        # uploaded_im_url =
        start = 0
        pages = []
        p = 0
        # import ipdb; ipdb.set_trace()
        options = webdriver.ChromeOptions()
        options.add_argument("--disable-dev-shm-usage")
        options.add_argument("--no-sandbox")
        options.add_argument("--headless")
        driver = webdriver.Chrome(
            ChromeDriverManager().install(), options=options)
        # driver.get(f"file://{uploaded_im_url}")
        # img = driver.find_element(By.TAG_NAME, "img")
        # img_src = img.get_attribute("src")
        # import ipdb; ipdb.set_trace()
        while True:
            params = {
                "hl": self.lang,
                "client": self.client,
                "image_url": uploaded_im_url,
                "start": str(start)
            }
            html = self.call_google_by_chrome(driver, params)
            # with open(root_path+"temp.html", "w") as temp:
            #     import ipdb; ipdb.set_trace()
            #     temp.write(html.encode("utf-8").strip())
            try:
                records = self.parse_html(html)
            except:
                with open("error.html", "w") as out: out.write(html)
                raise RuntimeError("Cannot parse HTML correctly")
            if records is None:
                raise ConnectionRefusedError(
                    "Google limits queries, try again later",
                )
            if len(records) == 0:
                break
            pages += records

            start += self.pagination
            p += 1
            if limit_page and p >= limit_page:
                break
        driver.close()
        return self.format(pages)


    def call_google_by_chrome(self, driver, params):
        url = self.url+urlencode(params)
        # import ipdb; ipdb.set_trace()
        driver.get(url)
        html = driver.page_source
        return html


    def format(self, data):
        return data


    def parse_html(self, html):
        if self.ERROR in html:
            return None
        soup = BeautifulSoup(html, features="html.parser")
        search_result = soup.find("div", id="rso")
        if not search_result:
            return []
        pages_including_tag = search_result.findChildren(recursive=False)[-1]
        pages_including_records = pages_including_tag.findChildren(
            recursive=False)[0].find_all("div", lang=True)

        pages_including = []
        for tag in pages_including_records:
            data = {
                "lang": tag["lang"],
            }
            a = tag.find_all("a", href=True)[0]
            data["link"] = a["href"]
            data["title"] = a.text
            info_tags = a.parent.parent.parent.findChildren(recursive=False)
            if len(info_tags) < 3:
                return []
            info_tags = info_tags[2].find_all("span")
            i_ = 0
            for i in range(1, len(info_tags)):
                size = self.find_and_format_size(info_tags[i].text)
                if size:
                    data["size"] = size
                    i_ = i+1
                    continue

                parsed_date = self.find_and_format_datetime(info_tags[i].text)
                if parsed_date:
                    data["date"] = parsed_date
                    i_ = i+1
                    continue
            if i_ < len(info_tags):
                data["content"] = info_tags[i_].text
            pages_including.append(data)
        return pages_including


    def find_and_format_size(self, s):
        try:
            return [int(v) for v in s.split(u"\u00D7")]
        except:
            return None


    def find_and_format_datetime(self, dts):
        day_units = {
            0: ["sec", "min", "hour"],
            1: ["day"],
            7: ["week"],
            30: ["month"],
            365: ["year"]
        }
        try:
            if "ago" in dts:
                for num_day, day_unit in day_units.items():
                    if any(unit in dts for unit in day_unit):
                        num = int(dts.split(" ")[0])
                        dts = (
                            datetime.today() - datetime.timedelta.days(
                                num_day*num,
                            )
                        ).strftime.isoformat()
                        return dts
            else:
                dts = datetime.datetime.strptime(dts, "%b %d, %Y").isoformat()
        except:
            return None
        return dts


class SearchByImageService:
    __instance = None

    @staticmethod
    def get_instance():
        if SearchByImageService.__instance is None:
            SearchByImageService.__instance = SearchByImageInstance()
        return SearchByImageService.__instance