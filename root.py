from datetime import datetime
import random

from access.bridge import Bridge
from auxiliar.timing import timing
from fitness.condition_map import ConditionMap
from gene import Gene
from objects.memory import Memory
from population import Population, mutate
from individual import Individual, express, PHENOTYPE, GENOTYPE
from auxiliar import file

from auxiliar.timing import timing_open, timing_close


# VARIATION UNDER DOMESTICATION
def optimize(individual: Individual):
    not_so_random = []
    chance_of_tabu = 0.4

    clone = Memory(individual)
    for c in individual.cromossomes.values():
        for g in c.genes:
            not_so_random.append(random.uniform(0, 1))
            if not_so_random[-1] <= chance_of_tabu:
                neighborhood = [None] + g.pool()
                novo_s = ()
                maior_fitness = individual.fitness()

                for s in neighborhood:
                    clone.change((s, g.gene_type))

                    if clone.fitness() > maior_fitness:
                        novo_s = (s, 1)
                        maior_fitness = clone.fitness()
                        clone.persist()

                if len(novo_s) > 1:
                    clone.revert()
                    g.set_data(novo_s[0])
                else:
                    clone.reset()


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

    # VARIATION UNDER NATURE
    offspring = population.breed(optimization=optimize)

    # NATURE UNDER CONTRAINT AND VEXED
    population.merge(offspring)
    population.select()

    # ENDLESS FORMS MOST BEAUTIFUL
    population.annihilate()


print('\n================================')
print('PREPARING DATA...', end='\n   ')
print(datetime.now())
print('================================', end='\n\n')
ConditionMap().load(file.load('fitness_conditions.json'))

database = Bridge()
database.sync('dsalexandre', None, 'ECOMP')
database.student.simulate_term(3)

Individual.ref_database(database)

random.seed(1)

i = Individual(genes=[107, 189, 85, 76, 147, 109, 24])
express(i)
express(i, GENOTYPE)

print('\n================================')
print('INITIATE SIMULATION', end='\n   ')
print(datetime.now())
print('================================', end='\n\n')

pop = populate(500)

# express(pop[0])
# express(pop[0], GENOTYPE)
# pop.analyse()
evolve(pop)  # first generation
pop.analyse()

for _ in range(1, 150):
    evolve(pop)
    pop.analyse()

express(pop.best())
express(pop.best(), GENOTYPE)
fit = pop.best().fitness()

if pop.best().fitness(force=True) != fit:
    express(pop.best(), GENOTYPE)

print('')
print(datetime.now())
