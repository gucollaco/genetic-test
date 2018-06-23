import random

from gene import Gene

CROMOSSOME_KEYS = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta']
NUMBER_OF_GENES = 6


class Cromossome:

    @staticmethod
    def ref_database(ref):
        Gene.ref_database(ref)

    def __init__(self, individual, day, random=False):
        super().__init__()

        self.individual = individual
        self.weekday = day
        self.genes = []

        for i in range(NUMBER_OF_GENES):
            self.genes.append(Gene(self, gene_type=(self.weekday, i), random=False))

        if random:
            self.randomize()

    def __repr__(self):
        s = []
        for g in self.genes:
            if g.data is None:
                s.append("(Vazio)")
            else:
                s.append(g.data.nome)

        return ", ".join(s)

    # randomiza inteiramente um cromossomo
    def randomize(self):
        for i in range(NUMBER_OF_GENES):
            self.genes[i] = Gene(self, gene_type=(self.weekday, i), random=True)

    # todo Melhorar crossingover
    def crossover(self, other):
        tip = random.sample(range(NUMBER_OF_GENES), 1)[0]
        c = Cromossome(None, self.weekday)
        for i in range(tip+1):
            c.genes[i] = self.genes[i].clone()
            c.genes[i].cromossome = c

        for i in range(tip+1, NUMBER_OF_GENES):
            c.genes[i] = other.genes[i].clone()
            c.genes[i].cromossome = c

        return c

    def gap_size(self, gene_index):
        pre_gap = 0
        for k in reversed(range(gene_index)):
            if self.genes[k].isEmpty():
                pre_gap += 1
            else:
                break

        pos_gap = 0
        for k in range(gene_index + 1, NUMBER_OF_GENES):
            if self.genes[k].isEmpty():
                pos_gap += 1
            else:
                break

        if pre_gap == gene_index and pos_gap == NUMBER_OF_GENES - gene_index + 1:
            gap = 0  # nao tem aulas no dia
        else:
            if pre_gap == gene_index:
                gap = 0  # nao existem aulas ainda pre posicao atual
            elif pos_gap == NUMBER_OF_GENES - (gene_index + 1):
                gap = 0  # nao existem aulas apos a posicao atual
            else:
                gap = pre_gap + 1 + pos_gap

        return gap