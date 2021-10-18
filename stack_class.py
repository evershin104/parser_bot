class Stack:
    stack = []
    current_urls = []
    max_size = 100

    def __init__(self):
        self.stack = []
        self.current_urls = []

    def add_urls_to_stack(self, urls):
        self.current_urls.clear()
        for url in urls:
            self.current_urls.append(url)
        for url in self.stack:
            if self.current_urls.count(url) != 0:
                self.current_urls.remove(url)
        for url in self.current_urls:
            self.stack.append(url)
        if len(self.stack) > self.max_size:
            self.stack = self.stack[len(self.stack) - self.max_size: self.max_size]
