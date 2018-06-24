from datetime import datetime
import random

from access.bridge import Bridge
from auxiliar.timing import timing
from fitness.condition_map import ConditionMap
from gene import Gene
from population import Population, mutate
from individual import Individual, express, PHENOTYPE, GENOTYPE
from auxiliar import file

from auxiliar.timing import timing_open, timing_close


# VARIATION UNDER DOMESTICATION
@timing
def optimize(individual: Individual):
    changes = []
    t = None
    not_so_random = []

    chance_of_tabu = 0.2
    for c in individual.cromossomes.values():
        for g in c.genes:
            not_so_random.append(random.uniform(0, 1))
            if not_so_random[-1] <= chance_of_tabu:
                neighborhood = [None] + g.pool()
                novo_s = ()
                maior_fitness = individual.fitness()

                for s in neighborhood:
                    bob = individual.clone((s, g.gene_type))

                    if bob.fitness() > maior_fitness:
                        novo_s = (s, 1)
                        maior_fitness = bob.fitness()

                if len(novo_s) > 1:
                    g.set_data(novo_s[0])


# THE DESIGN OF NATURAL OBJECTS
def populate(size):
    pop = Population(size=size)

    for _ in range(size):
        i = Individual(random=True, generation=pop.generation)
        pop.append(i)

    return pop


# BY MEANS WHICH HAVE NEVER YET BEEN TRIED
def evolve(population):
    population.generation += 1

    # TO RIGHT THE WRONGS OF MANY
    offspring = population.breed(optimization=optimize)

    # VARIATION UNDER NATURE
    mutate(offspring)

    # NATURE UNDER CONTRAINT AND VEXED
    population.merge(offspring)
    population.select()


print('\n================================')
print('PREPARING DATA...', end='\n   ')
print(datetime.now())
print('================================', end='\n\n')
ConditionMap().load(file.load('fitness_conditions.json'))

database = Bridge()
database.sync('dsalexandre', 'HelenOfTroy1', 'ECOMP')
database.student.simulate_term(3)

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

for _ in range(1, 200):
    if _ == 50:
        pass
    evolve(pop)
    pop.analyse()

express(pop.best())
express(pop.best(), GENOTYPE)
fit = pop.best().fitness()

if pop.best().fitness(force=True) != fit:
    express(pop.best(), GENOTYPE)

print('')
print(datetime.now())
