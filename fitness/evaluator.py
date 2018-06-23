class Evaluator:
    def __init__(self):
        super().__init__()

        self.scores = []
        self.descriptions = []

    def __repr__(self):
        return str(self.evaluate())

    def compute(self, condition, **kwargs):
        self.scores.append(condition.score(**kwargs))
        self.descriptions.append('')

    def describe(self, condition, description, **kwargs):
        self.scores.append(condition.score(**kwargs))
        self.descriptions.append(str(description))

    def evaluate(self):
        return sum([s['score'] for s in self.scores])

    @property
    def items(self) -> list:
        return [[s['score'], d, s['condition'].name] for s, d in zip(self.scores, self.descriptions)]