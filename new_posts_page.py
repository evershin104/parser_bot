from bs4 import BeautifulSoup
from post_class import get_html

class NewPosts:

    url = 'link'
    posts = []

    def parse_page(self):
        self.posts.clear()
        soup = BeautifulSoup(get_html(self.url), 'html.parser')
        for link in soup.find_all('a'):
            # Грязь
            if str(link.get('href')).count('link') != 0 and str(link.get('href')).count(
                    ';promoted') == 0 and self.posts.count(link.get('href')) == 0 and len(self.posts) < 15:
                self.posts.append(link.get('href'))
