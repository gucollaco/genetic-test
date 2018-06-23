class Condition(object):
    def __init__(self, id, name, score=None, extra=None, obs=None):
        super().__init__()
        self.id = id
        self.name = name
        self.score_model = score
        self.extra = extra
        self.obs = obs

    def __str__(self):
        return self.name

    def __repr__(self):
        return self.__str__()

    def __eq__(self, other):
        from grid.condition_map import Conditions

        if isinstance(other, Condition):
            return self.id == other.id
        elif isinstance(other, Conditions):
            if self.id is None and other.value is None:
                return True
            return self.id == other.value
        else:
            return NotImplemented

    def base(self):
        return Condition(self.id, self.name, self.score_model, self.extra, self.obs)

    def score(self, **k):
        if self.score_model is None:
            return 0

        return eval(self.score_model)