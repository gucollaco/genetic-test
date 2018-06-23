class Aula:
    _ref_database = None

    @staticmethod
    def ref_database(ref):
        Aula._ref_database = ref

    def __init__(self, _id, turma, termo, curso):
        super().__init__()

        self.id = _id
        self.turma = turma
        self.termo = termo
        self.curso = curso
        self.horarios = []

        self._id_materia = None
        self._id_professor = None

        self._obj_materia = None
        self._obj_professor = None

        self._ref_materias = None
        self._ref_professores = None

    def __repr__(self):
        if self.materia is None:
            return "Unknown Class #{} - {}".format(self.id, self.professor)
        else:
            return "{} - {} {}".format(self.materia.nome, self.turma, self.professor)

    def set_materia(self, id_materia):
        self._id_materia = id_materia

    def set_professor(self, id_professor):
        self._id_professor = id_professor

    def ref_materias(self, ref):
        self._ref_materias = ref

    def ref_professores(self, ref):
        self._ref_professores = ref

    @property
    def nome(self):
        m = self.materia
        if m is None:
            return "Unknown Summary #{}".format(self._id_materia)

        return m.nome

    @property
    def materia(self):
        if self._obj_materia is None:
            if self._id_materia is None or self._id_materia == -1:
                return None

            self._obj_materia = self._ref_materias[self._id_materia]

        return self._obj_materia

    @property
    def professor(self):
        if self._obj_professor is None:
            if self._id_professor is None:
                return None
            elif isinstance(self._id_professor, str):
                return self._id_professor

            self._obj_professor = self._ref_professores[self._id_professor]

        return self._obj_professor