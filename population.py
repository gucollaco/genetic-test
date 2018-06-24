import itertools

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
        wheel = list(self.ordered)

        chance_of_picking = random.uniform(0, 1)
        acumulated_fitness = 0.0
        for i in wheel:
            acumulated_fitness += i.fitness(sum_fitness)

            if chance_of_picking <= acumulated_fitness:
                mom = i
                break

        wheel.remove(mom)
        sum_fitness -= mom.fitness()

        chance_of_picking = random.uniform(0, 1)
        acumulated_fitness = 0.0
        for i in wheel:
            acumulated_fitness += i.fitness(sum_fitness)

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
            offspring += parent.mate(other_parent, optimization, generation=self.generation)

        return offspring

    def select(self):
        removals = self.size - self.initial_size

        worse = sorted(self.items, key=lambda x: x.fitness())[:removals]
        self.offspring_rejection_ratio = len([w for w in worse if w.origin >= self.generation])/removals

        for individual in worse:
            self.items.remove(individual)

    def best(self):
        return self.ordered[0]

    def analyse(self):
        import numpy

        if self.generation % 1 == 0:
            print('#{} GEN'.format(self.generation), end=' | ')
            fts = [i.fitness() for i in self.items]
            print('max: {:.3f}  min: {:.3f}  avg: {:.3f} var: {:.2f} rej: {:3f}'.format(max(fts), min(fts), numpy.mean(fts), self.variability() * 100, self.offspring_rejection_ratio))
            # print(sorted(fts))

    def variability(self) -> float:
        return len(set(self.items))/len(self.items)