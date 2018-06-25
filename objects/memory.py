from individual import Individual, NUMBER_OF_GENES


class Memory(Individual):
    def __init__(self, original: Individual):
        super().__init__(generation=original.origin)

        self.reverts = []
        self.original = []
        self.original_index = []

        for k, c in self.cromossomes.items():
            for j in range(NUMBER_OF_GENES):
                self.cromossomes[k].genes[j] = c.genes[j].clone(cromossome=self.cromossomes[k])

    def change(self, *args):
        for data, gene_type in args:
            if gene_type not in self.original_index:
                self.original.append((self.cromossomes[gene_type[0]].genes[gene_type[1]].data, gene_type))
                self.original_index.append(gene_type)

            self.reverts.append((self.cromossomes[gene_type[0]].genes[gene_type[1]].data, gene_type))

            self.cromossomes[gene_type[0]].genes[gene_type[1]].set_data(data, False)

        self.recalculate = True
        self.calculate()

    def revert(self):
        for data, gene_type in self.reverts:
            self.cromossomes[gene_type[0]].genes[gene_type[1]].set_data(data, False)

        self.recalculate = True
        self.calculate()

    def persist(self):
        self.reverts = []

    def reset(self):
        for data, gene_type in self.original:
            self.cromossomes[gene_type[0]].genes[gene_type[1]].set_data(data, False)

        self.recalculate = True
        self.calculate()
