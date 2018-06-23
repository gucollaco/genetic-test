from datetime import datetime
import random

from access.bridge import Bridge
from fitness.condition_map import ConditionMap
from population import Population, mutate
from individual import Individual, express, PHENOTYPE, GENOTYPE
from auxiliar import file


# VARIATION UNDER DOMESTICATION
def optimize(individual: Individual):
    pass


# THE DESIGN OF NATURAL OBJECTS
def populate(size):
    pop = Population(size=size)

    for _ in range(size):
        i = Individual(random=True)
        pop.append(i)

    return pop


# BY MEANS WHICH HAVE NEVER YET BEEN TRIED
def evolve(population):
    # TO RIGHT THE WRONGS OF MANY
    offspring = population.breed()

    # VARIATION UNDER NATURE
    mutate(offspring)

    # NATURE UNDER CONTRAINT AND VEXED
    population.merge(offspring)
    population.select()
    population.generation += 1


print('\n================================')
print('PREPARING DATA...', end='\n   ')
print(datetime.now())
print('================================', end='\n\n')
ConditionMap().load(file.load('fitness_conditions.json'))

database = Bridge()
database.sync('dsalexandre', None, 'ECOMP')

Individual.ref_database(database)

random.seed(1)

print('\n================================')
print('INITIATE SIMULATION', end='\n   ')
print(datetime.now())
print('================================', end='\n\n')

pop = populate(100)
# express(pop[0])
# express(pop[0], GENOTYPE)
pop.analyse()
evolve(pop)  # first generation
pop.analyse()

for _ in range(1, 1000):
    evolve(pop)
    pop.analyse()

express(pop.best())
express(pop.best(), GENOTYPE)

print('')
print(datetime.now())