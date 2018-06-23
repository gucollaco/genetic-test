class Professor:
    _ref_database = None

    @staticmethod
    def ref_database(ref):
        Professor._ref_database = ref

    def __init__(self, _id, nome, avaliacao, falta):
        super().__init__()

        self.id = _id
        self.nome = nome
        self.avaliacao = avaliacao
        self.falta = falta

    def __repr__(self):
        return "{}".format(self.nome)