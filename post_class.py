import requests
from bs4 import BeautifulSoup


def get_html(url):
    try:
        t = requests.get(url).text
        return t
    except:
        return ""


class Post:
    time = ""
    price = ""
    title = ""
    description = ""
    number = ""
    url = ""
    location = ""
    soup = ""
    actual = ""

    def check_actuality(self):
        if get_html(self.url).find("Anuntul este dezactivat") != -1:
            self.actual = False
        self.actual = True

    def clear_all(self):
        self.time = ""
        self.price = ""
        self.title = ""
        self.description = ""
        self.number = ""
        self.url = ""
        self.location = ""
        self.soup = ""
        self.actual = ""

    def parse_time(self):
        if self.soup.find("li", {"class": "offer-bottombar__item"}) is None:
            self.time = "None"
        else:
            self.time = str(self.soup.find("li", {"class": "offer-bottombar__item"}).em.strong.string)

    def parse_price(self):
        if self.soup.find("strong", {"class": "pricelabel__value not-arranged"}) is None:
            if self.soup.find("strong", {"class": "pricelabel__value arranged"}) is None:
                self.price = "None"
            else:
                self.price = self.soup.find("strong", {"class": "pricelabel__value arranged"}).string
        else:
            self.price = str(self.soup.find("strong", {"class": "pricelabel__value not-arranged"}).string)

    def parse_title(self):
        self.title = str(self.soup.find("h1").string).replace("  ", "").replace("\n", "")

    def parse_description(self):
        self.description = str(self.soup.find("div", {"class": "clr lheight20 large", "id": "textContent"})).replace(
            "<br/>", "").replace("  ", "").replace("</div>", "")
        self.description = self.description[self.description.find(">") + 1:len(self.description)]
        if self.description.find("<") != -1:
            phone_start = self.description.find("data-phone=") + 12
            i = phone_start
            while self.description[i].isdigit():
                i += 1
            phone_end = i
            phone = self.description[phone_start:phone_end]
            self.description = self.description[0:self.description.find("<span")] + phone + self.description[
                                                                                            self.description.find(
                                                                                                "</span></span>") + 14: len(
                                                                                                self.description)]
        self.description.replace("\n", ". ")

    def parse_number(self):
        if self.soup.find("span", {"class": "spoiler"}) is None:
            self.number = "-number"
        else:
            self.number = "+number"

    def parse_location(self):
        if self.soup.find("address") is not None:
            self.location = str(self.soup.find("address").p.string)

    # Init post with URL
    def __init__(self, url):
        self.url = url
        self.soup = BeautifulSoup(get_html(self.url), 'html.parser')
        self.check_actuality()
        if self.actual:
            self.parse_time()
            self.parse_price()
            self.parse_title()
            self.parse_description()
            self.parse_number()
            self.parse_location()

    def generate_text(self):
        to_return = "🇷🇴🇷🇴🇷🇴🇷🇴🇷🇴🇷🇴🇷🇴🇷🇴🇷🇴🇷🇴🇷🇴🇷🇴🇷🇴🇷🇴\n"
        if self.actual:
            to_return += self.time + "\n" + self.price + ": " \
                         + self.title + "\n" + self.description.replace("\n", ". ")[2:len(self.description)] \
                         + "\n" + self.location + " " + self.number \
                         + "\n" + self.url + "\n"
            to_return += "🇷🇴🇷🇴🇷🇴🇷🇴🇷🇴🇷🇴🇷🇴🇷🇴🇷🇴🇷🇴🇷🇴🇷🇴🇷🇴🇷🇴\n"
            if len(to_return) < 2000 and to_return.count("<div>") == 0:
                return to_return
            else:
                return ""
        else:
            return ""

    def __del__(self):
        self.clear_all()
