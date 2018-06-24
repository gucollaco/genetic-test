import random

from fitness.condition_map import Conditions
from fitness.evaluator import Evaluator


class Gene:
    ref_database = None

    @staticmethod
    def ref_database(ref):
        Gene.ref_database = ref

    # gene_type: (DIA_DA_SEMANA, HORA)
    def __init__(self, cromossome, gene_type=None, random=False):
        super().__init__()

        self.cromossome = cromossome
        self.data = None
        self.gene_type = gene_type

        self._evaluator = None

        if random:
            self.mutate(populate=True)

    def __repr__(self):
        if self.data is None:
            return ""
        else:
            return str(self.data)

    def __eq__(self, other):
        if self.data is None or other.data is None:
            if other.data is None and self.data is None:
                return True
            else:
                return False

        return self.data.id == other.data.id

    @staticmethod
    def __fit__(data, gene_type, cromossome):
        e = Evaluator()
        student = Gene.ref_database.student

        if data is None:  # CONDICAO <QUANTIDADE DE JANELAS ENTRE AULAS>
            gap = cromossome.gap_size(gene_type[1])

            # todo CONDITION ? (um dia vazio pode estar sujeito a condicoes)
            if gap > 0:
                e.describe(Conditions.B, gap, g=gap)

            if student.preferences[gene_type[1]][gene_type[0]] == '0':
                e.describe(Conditions.O, 'Vazio')
        else:
            aula = data
            individual = cromossome.individual
            materia = data.materia
            gene_index = individual.index

            if student.preferences[gene_type[1]][gene_type[0]] == '0':
                e.compute(Conditions.P)
            else:
                e.compute(Conditions.O)

            if materia.id in gene_index:
                qtd = len(gene_index[materia.id])
            else:
                qtd = 0

            if qtd > 1:  # se tem mais de 1 horario pra uma unica uc
                e.describe(Conditions.C, qtd)

            if materia.id in gene_index:
                if aula.id in gene_index[materia.id]:
                    workload = len(gene_index[materia.id][aula.id])
                else:
                    workload = 1
            else:
                workload = 1

            if workload < materia.credit:  # gene recessivo
                e.describe(Conditions.W, materia.carga)

            historyUC = [obj for obj in student.history['objects'] if materia.id == obj['object'].id]
            if len(historyUC) > 0:  # UC ja cursada
                if any(uc['status'] == 'APROVADO' for uc in historyUC):  # CONDICAO <UC JA CURSADA E APROVADA>
                    e.describe(Conditions.L, historyUC[0]['term'])
                    return e  # ja sai da avaliação, qqlr aula ja aprovada n tem q estar aq
                elif any('REPROVADO' == uc['status'] or 'REPROV./FREQ' == uc['status'] for uc in historyUC):  # CONDICAO <DP NA UC>
                    e.describe(Conditions.M, len(historyUC), q=len(historyUC), t=0)

            if not student.has_requisites(materia):  # CONDICAO <UC SEM PREREQUISITOS>
                e.compute(Conditions.D)
            else:  # tem requisitos, avaliar o quao boa a materia é
                if materia in student.graduation_map:  # esta no mapa de graduacao e tem os prereqs
                    dep = student.graduation_map.get_dependencies(materia)
                    if len(dep) == 0:
                        e.describe(Conditions.E, len(dep), d=len(dep))

                    lecture_term = student.graduation_map.get_term(materia)
                    if lecture_term == student.get_current_term():  # termo == atual PREENT
                        e.describe(Conditions.F, lecture_term)
                    elif lecture_term > student.get_current_term():  # termo > atual FUTURO
                        e.describe(Conditions.G, lecture_term)
                    else:  # termo < atual PASSADO
                        e.describe(Conditions.H, lecture_term)
                else:  # uc eletiva
                        e.compute(Conditions.I)

        return e

    def set_data(self, data):
        self.data = data
        self._evaluator = None
        self.cromossome.individual.recalculate = True

    @property
    def fitness(self):
        if self._evaluator is None:
            self._evaluator = Gene.__fit__(self.data, self.gene_type, self.cromossome)

        return self._evaluator.evaluate()

    @property
    def evaluator(self):
        if self._evaluator is None:
            self._evaluator = self.__fit__(self.data, self.gene_type, self.cromossome)

        return self._evaluator

    def isEmpty(self):
        return self.data is None

    # gera a gene pool pra o slot com base no dia da semana e hora
    def pool(self, level="ALL"):
        if level == 'ALL':
            return [a for a in Gene.ref_database.aulas.values() if any(self.gene_type == h for h in a.horarios)]

    # todo Melhorar mutacao
    def mutate(self, populate=False):
        empty_proportion = 0.33
        if populate:
            empty_proportion = 2.75

        # cria a variedade de genes aceitaveis
        known = self.pool()
        pool = [None] * int(len(known) * empty_proportion)
        pool += known

        self.data = random.sample(pool, 1)[0]
        self._evaluator = None
        self.cromossome.individual.recalculate = True

    def clone(self):
        g = Gene(None, self.gene_type)
        g.data = self.data

        return g