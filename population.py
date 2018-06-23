from individual import Individual
import random


def mutate(offspring):
    for i in offspring:
        i.mutate()


class Population(object):
    def __init__(self, size=100, breading=0.25):
        super().__init__()

        self.initial_size = size
        self.items = list()

        self.chance_of_breading = breading

        self.offspring_rejection_ratio = 0

        self.generation = 1

    def __iter__(self):
        self.items.__iter__()

    def __getitem__(self, item):
        return self.items.__getitem__(item)

    def __len__(self):
        return self.items.__len__()

    # LIST WISE METHODS
    @property
    def size(self):
        return len(self)

    def append(self, item):
        self.items.append(item)

    def merge(self, other):
        if type(other) is list:
            for individual in other:
                self.append(individual)
        elif type(other) is Population:
            for individual in other.items:
                self.append(individual)

    @property
    def ordered(self):
        ordered_items = list(self.items)
        ordered_items.sort(key=lambda x: x.fitness(), reverse=True)

        return ordered_items

    # INDIVIDUALS METHODS
    def fittest(self, rank=1) -> Individual:
        ordered_individuals = sorted(self.items, key=lambda x: x.fitness)

        return ordered_individuals[rank - 1]

    def pick(self) -> tuple:
        mom, dad = None, None

        sum_fitness = sum([i.fitness() for i in self.items])
        wheel = [[i.fitness(sum_fitness), i] for i in self.ordered]

        chance_of_picking = random.uniform(0, 1)
        acumulated_fitness = 0.0
        for fitness, i in wheel:
            acumulated_fitness += fitness

            if chance_of_picking <= acumulated_fitness:
                mom = i
                break

        sum_fitness = sum([i.fitness() for i in self.items if i != mom])
        wheel = [[i.fitness(sum_fitness), i] for i in self.ordered if i != mom]

        chance_of_picking = random.uniform(0, 1)
        acumulated_fitness = 0.0
        for fitness, i in wheel:
            acumulated_fitness += fitness

            if chance_of_picking <= acumulated_fitness:
                dad = i
                break

        return mom, dad

    # GENETIC METHODS
    def breed(self, optimization=None):
        offspring = []

        # for each mating
        for _ in range(int(self.size * self.chance_of_breading)):
            parent, other_parent = self.pick()
            offspring.append(parent.mate(other_parent, optimization))

        return offspring

    def select(self):
        removals = self.size - self.initial_size

        worse = sorted([[i, individual] for i, individual in enumerate(self.items)], key=lambda x: x[1].fitness())[:25]
        worse.sort(key=lambda x: x[0], reverse=True)
        self.offspring_rejection_ratio = len([w for w in worse if w[0] >= self.initial_size])/removals

        for i, individual in worse:
            del self.items[i]
            removals -= 1

            if removals <= 0:
                break

    def best(self):
        return self.ordered[0]

    def analyse(self):
        import numpy

        fts = [i.fitness() for i in self.items]
        print('#{} GEN'.format(self.generation), end=' | ')
        print('max: {:.3f}  min: {:.3f}  avg: {:.3f}'.format(max(fts), min(fts), numpy.mean(fts)))
        # print(sorted(fts))
