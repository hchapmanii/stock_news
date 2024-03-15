class News:

    def __init__(self, n_title, n_description):
        self.title = n_title
        self.description = n_description

    def __repr__(self):
        return f"Headline: {self.title},\nBrief: {self.description}\n\n"
