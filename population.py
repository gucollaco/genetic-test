import itertools

from individual import Individual, MAX_LIFESPAN
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
        self.chance_of_annihilation = 0.3

        self.rejection_history_size = 10
        self.rejection_limit = 0.92

        self.annihilation_ratio = 0.0
        self.offspring_rejection_ratio = 0.0
        self.elders_rejection_ratio = 0.0

        self.offspring_rejection_history = []

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
                individual.reset()
                self.append(individual)
        elif type(other) is Population:
            for individual in other.items:
                individual.reset()
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

        sample = list(self.ordered)[:int(self.initial_size/2)]

        sum_fitness = sum([i.fitness() for i in sample])
        wheel = sample

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
        elders = []
        worse = []
        maximum_rejection = self.size - self.initial_size
        j = 0
        for i in reversed(self.ordered):
            i.timespan += 1
            if i.timespan > MAX_LIFESPAN:
                # elders.append(i)
                continue

            if j < maximum_rejection:
                worse.append(i)
                j += 1

        removals = self.size - self.initial_size - len(elders)

        worse = sorted(worse, key=lambda x: x.fitness())[:removals]

        self.offspring_rejection_ratio = 0 if maximum_rejection == 0 else len([w for w in worse if w.origin >= self.generation])/maximum_rejection
        self.elders_rejection_ratio = len(elders)/self.size

        worse += elders
        for individual in worse:
            self.items.remove(individual)

    def best(self):
        return self.ordered[0]

    def analyse(self):
        import numpy

        if self.generation % 1 == 0:
            print('#{} GEN'.format(self.generation), end=' | ')
            fts = [i.fitness() for i in self.items]
            print('max: {:.3f} min: {:.3f} avg: {:.3f} var: {:.2f} rej: {:.3f} anh: {:.3f} pop: {}'.format(max(fts), min(fts), numpy.mean(fts), self.variability() * 100, self.offspring_rejection_ratio, self.annihilation_ratio, len(self)))
            # print(sorted(fts))

    def variability(self) -> float:
        uniques = set(self.items)
        return len(uniques)/len(self.items)

    def annihilate(self):
        if len(self.offspring_rejection_history) == self.rejection_history_size:
            self.offspring_rejection_history.pop(0)
        self.offspring_rejection_history.append(self.offspring_rejection_ratio)

        avg = sum(self.offspring_rejection_history)/self.rejection_history_size

        if avg > self.rejection_limit:
            chosen = (1 - self.chance_of_annihilation) * 0.1

            pool = list(self.ordered)[int(len(self) * chosen):int(len(self) * chosen * -1)]
            worse = list(self.ordered)[int(len(self) * chosen * -1):]

            pool = [i for i in pool if random.uniform(0, 1) < self.chance_of_annihilation]
            pool += worse

            hole_size = len(pool)

            self.annihilation_ratio = len(pool)/len(self)

            for individual in pool:
                self.items.remove(individual)
            for _ in range(hole_size):
                i = Individual(random=True, generation=self.generation)
                self.append(i)
        else:
            self.annihilation_ratio = 0.0
