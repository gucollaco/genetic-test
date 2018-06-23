import random

from cromossome import CROMOSSOME_KEYS, Cromossome

GENOTYPE = 1
PHENOTYPE = 2


def express(obj, type=PHENOTYPE):
    if type == PHENOTYPE:
        print(obj.__expression__())
    else:
        print(obj.__desc__())


class Individual:

    @staticmethod
    def ref_database(ref):
        Cromossome.ref_database(ref)

    def __init__(self, random=False, genes=None):
        super().__init__()

        self.cromossomes = dict()
        self.chance_of_mutating = 0.1

        if random:
            self.randomize()

    def __repr__(self):
        try:
            return str(self.fitness())
        except:
            return 'Unknown'

    def __expression__(self):
        from texttable import Texttable
        DAYS = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta']
        TIMES = ["8h00-10h00", "10h00-12h00", "13h30-15h30", "15h30-17h30", "19h00-21h00", "21h00-23h00"]
        HEADERS = ['Horário'] + DAYS

        rows = []
        for t in range(len(TIMES)):
            row = [TIMES[t]]

            for d in DAYS:
                c = self.cromossomes[d]
                row.append("{}".format(c.genes[t]))

            rows.append(row)

        t = Texttable()
        t.add_rows([HEADERS] + rows)
        t.set_cols_width([11] + [30] * 5)
        return t.draw()

    def __desc__(self):
        from texttable import Texttable

        tablething = []
        evals = [[g.evaluator, g] for c in self.cromossomes.values() for g in c.genes]
        tablething.append(['Score', 'Target', 'Slot', 'Condition', 'Detail'])
        tablething.append([self.fitness(), 'Grade', '', '', 'TOTAL'])

        # zipped_data = sorted(zip(fitness_scores[0], fitness_scores[1], fitness_scores[2]), key=lambda x: (x[2], x[0]))
        data = [[es, str(g.data), ec, ed, g.gene_type] for ev, g in evals for es, ed, ec in ev.items]
        data = sorted(data, key=lambda x: (x[1], x[0]))
        data = sorted(data, key=lambda x: sum([c[0] for c in data if x[1] == c[1]]), reverse=True)

        for i in range(len(data)):
            col = data[i]

            resumed_col_2 = col[1]
            if i >= 1:
                if resumed_col_2 == data[i-1][1]:
                    resumed_col_2 = ''
                else:
                    if len([c[0] for c in data if data[i-1][1] == c[1]]) > 1:
                        tablething.append([sum([c[0] for c in data if data[i-1][1] == c[1]]), '', '', '', ''])

            tablething.append([col[0], resumed_col_2, col[4], col[2], col[3]])

        b = Texttable()
        b.add_rows(tablething)
        b.set_cols_width([10, 65, 30, 40, 20])
        return b.draw()

    # randomiza inteiramente todos os cromossomos de um individuo
    def randomize(self):
        for weekday in CROMOSSOME_KEYS:
            self.cromossomes[weekday] = Cromossome(self, weekday, random=True)

    def fitness(self, normalized=1):
        total = sum([g.fitness for c in self.cromossomes.values() for g in c.genes])

        return total/normalized

    def mutate(self):
        for cromossome in self.cromossomes.values():
            for gene in cromossome.genes:
                if random.uniform(0, 1) < self.chance_of_mutating:
                    gene.mutate()

    # todo Melhorar mating
    def mate(self, other, optimization=None):
        child = Individual()

        for k in CROMOSSOME_KEYS:
            profase = self.cromossomes[k].crossover(other.cromossomes[k])
            profase.individual = child
            child.cromossomes[k] = profase

        if optimization is not None:
            child = optimization(child)

        return child

    @property
    def index(self):
        # retornar um indice com todas as materias que estao no genotipo
        # algo como {id_materia: [lista com as aulas com esse id materia]}
        # return {g.data.materia.id: [] for c in self.cromossomes.values() for g in c.genes}
        idx = {}
        for c in self.cromossomes.values():
            for g in c.genes:
                if g.data is not None:
                    if g.data.materia.id not in idx:
                        idx[g.data.materia.id] = {}

                    aula = g.data
                    if aula.id not in idx[g.data.materia.id]:
                        idx[aula.materia.id][aula.id] = []

                    idx[aula.materia.id][aula.id].append(g.gene_type)

        return idx

