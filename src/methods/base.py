class ParserBase:


    def __init__(self, query: str, per_page: int = 50):
        self.query = query
        self.per_page = per_page


    def fetch(self):
        raise NotImplementedError("Метод fetch() должен быть реализован в наследнике.")
