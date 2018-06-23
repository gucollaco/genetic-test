import random

from fitness.condition_map import Conditions
from fitness.evaluator import Evaluator


class Gene:
    _ref_database = None

    @staticmethod
    def ref_database(ref):
        Gene._ref_database = ref

    # gene_type: (DIA_DA_SEMANA, HORA)
    def __init__(self, cromossome, gene_type=None, random=False):
        super().__init__()

        self.cromossome = cromossome
        self.data = None
        self.gene_type = gene_type

        self._evaluator = None

        if random:
            self.mutate()

    def __repr__(self):
        if self.data is None:
            return ""
        else:
            return str(self.data)

    def __fit__(self):
        e = Evaluator()

        if self.data is None:  # CONDICAO <QUANTIDADE DE JANELAS ENTRE AULAS>
            gap = self.cromossome.gap_size(self.gene_type[1])

            # todo CONDITION ? (um dia vazio pode estar sujeito a condicoes)
            if gap > 0:
                e.describe(Conditions.B, gap, g=gap)
        else:
            aula = self.data
            individual = self.cromossome.individual
            materia = self.data.materia
            student = Gene._ref_database.student
            gene_index = individual.index

            qtd = len(gene_index[materia.id])
            if qtd > 1:  # se tem mais de 1 horario pra uma unica uc
                e.describe(Conditions.C, qtd)

            workload = len(gene_index[materia.id][aula.id])
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

    @property
    def fitness(self):
        if self._evaluator is None:
            self._evaluator = self.__fit__()

        return self._evaluator.evaluate()

    @property
    def evaluator(self):
        if self._evaluator is None:
            self._evaluator = self.__fit__()

        return self._evaluator

    def isEmpty(self):
        return self.data is None

    # gera a gene pool pra o slot com base no dia da semana e hora
    def pool(self, level="ALL"):
        if level == 'ALL':
            return [a for a in Gene._ref_database.aulas.values() if any(self.gene_type == h for h in a.horarios)]

    # todo Melhorar mutacao
    def mutate(self):
        # cria a variedade de genes aceitaveis
        known = self.pool()
        pool = [None] * int(len(known) * 0.1)
        pool += known

        self.data = random.sample(pool, 1)[0]

    def clone(self):
        g = Gene(None, self.gene_type)
        g.data = self.data

        return g