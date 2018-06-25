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

    def __eq__(self, other):
        for g, o in zip(self.genes, other.genes):
            if g != o:
                return False

        return True

    # randomiza inteiramente um cromossomo
    def randomize(self):
        for i in range(NUMBER_OF_GENES):
            self.genes[i] = Gene(self, gene_type=(self.weekday, i), random=True)

    def crossover(self, children, other, tip=None):
        return self.uniform_crossover(children, other)

    def uniform_crossover(self, child, other):
        c = Cromossome(child, self.weekday)

        for i in range(NUMBER_OF_GENES):
            if self.genes[i] == other.genes[i]:
                c.genes[i] = self.genes[i].clone(c)
            else:
                if random.uniform(0, 1) < 0.5:
                    c.genes[i] = self.genes[i].clone(c)
                else:
                    c.genes[i] = other.genes[i].clone(c)

        return c

    # todo Escolher: tip igual pra todos os cromossomos ou diferente pra cada um
    def single_point_crossover(self, children, other, tip):
        c = Cromossome(children[0], self.weekday)
        c2 = Cromossome(children[1], self.weekday)

        for i in range(tip+1):
            c.genes[i] = self.genes[i].clone(c)
            c.genes[i].cromossome = c

            c2.genes[i] = other.genes[i].clone(c2)
            c2.genes[i].cromossome = c2

        for i in range(tip+1, NUMBER_OF_GENES):
            c.genes[i] = other.genes[i].clone(c)
            c.genes[i].cromossome = c

            c2.genes[i] = self.genes[i].clone(c2)
            c2.genes[i].cromossome = c2

        return c, c2

    def gap_size(self, gene_index):
        pre_gap = 0
        student = Gene.ref_database.student

        for k in reversed(range(gene_index)):
            if self.genes[k].isEmpty():
                pre_gap += 1

                gene_type = self.genes[k].gene_type
                if student.preferences[gene_type[1]][gene_type[0]] == '0':  # se o aluno preferir o horario vazio nao penaliza
                    pre_gap -= 1

            else:
                break

        pos_gap = 0
        for k in range(gene_index + 1, NUMBER_OF_GENES):
            if self.genes[k].isEmpty():
                pos_gap += 1

                gene_type = self.genes[k].gene_type
                if student.preferences[gene_type[1]][gene_type[0]] == '0':  # se o aluno preferir o horario vazio nao penaliza
                    pre_gap -= 1
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