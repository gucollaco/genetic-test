WORKLOAD_TO_CREDIT = {'36h': 1, '72h': 2, '108h': 3}


class Materia(object):
    _ref_database = None

    @staticmethod
    def ref_database(ref):
        Materia._ref_database = ref

    @staticmethod
    def find(obj, minimum=None, limit=None, detail=False, fast=False):
        from auxiliar.word import ratio

        if not fast:
            result = [[m, max([ratio(a, obj) for a in m.alternativos])] for m in Materia._ref_database.materias.values()]
        else:
            result = []
            for m in Materia._ref_database.materias.values():
                r = [m, max([ratio(a, obj) for a in m.alternativos])]
                result += [r]
                if r[1] == 100:  # correspondencia exata
                    break

        result.sort(key=lambda x: x[1], reverse=True)

        if minimum is not None:
            result = list(filter(lambda x: x[1] >= minimum, result))

        if limit is not None:
            return result[:limit if limit >= len(result) else len(result)]

        if len(result) == 0:
            return None
        elif len(result) == 1:
            if detail:
                return result[0]

            return result[0][0]
        else:
            if result[0][1] == result[1][1]:
                raise ValueError('Multiple correspondences for: <{}>'.format(obj))
            else:
                if detail:
                    return result[0]
                return result[0][0]

    def __init__(self, _id, nome, carga):
        super().__init__()

        self.id = _id
        self.nome = nome
        self.alternativos = []
        self.carga = carga

        self._ids_requisites = []
        self._objs_requisites = []
        self._ref_materias = None

        self.extra = None

    def __repr__(self):
        return "({}) {}".format(self.id, self.nome)

    def __eq__(self, other):
        return self.id == other.id

    def add_requisite(self, other):
        if isinstance(other, (int, str)):
            self._ids_requisites.append(other)
        else:
            self._objs_requisites.append(other)
            self._ids_requisites.append(other.id)

    def ref_materiais(self, ref):
        self._ref_materias = ref

    @property
    def requisites(self) -> list:
        if not self._ref_materias is None:
            self._objs_requisites = []
            for id_requisite in self._ids_requisites:
                self._objs_requisites.append(self._ref_materias[id_requisite])

        return self._objs_requisites

    @property
    def credit(self):
        return WORKLOAD_TO_CREDIT[self.carga]


if __name__ == "__main__":
    from access.bridge import Bridge

    database = Bridge()
    database.sync()
    Materia.ref_database(database)

    print(Materia.find('Teoria Numerica e Criptografia'))
    print('')