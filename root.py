from datetime import datetime
import random

from access.bridge import Bridge
from fitness.condition_map import ConditionMap
from gene import Gene
from population import Population, mutate
from individual import Individual, express, PHENOTYPE, GENOTYPE
from auxiliar import file


# VARIATION UNDER DOMESTICATION
def optimize(individual: Individual):
    previous_fitness = individual.fitness()

    chance_of_tabu = 0.2
    for c in individual.cromossomes.values():
        for g in c.genes:
            if random.uniform(0, 1) <= chance_of_tabu:
                neighborhood = [None] + g.pool()
                novo_s = ()
                maior_fitness = g.fitness

                for s in neighborhood:
                    s_evaluator = Gene.__fit__(s, g.gene_type, c)
                    if s_evaluator.evaluate() > maior_fitness:
                        novo_s = (s, s_evaluator)
                        maior_fitness = s_evaluator.evaluate()

                if len(novo_s) > 1:
                    g.data = novo_s[0]
                    g._evaluator = novo_s[1]
                    individual.recalculate = True

    if previous_fitness > individual.fitness():
        rt = individual.fitness() - previous_fitness
        rt /= abs(previous_fitness)
        print('      OPTIMIZING <{:.2f}%>'.format(rt * 100))


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

for _ in range(1, 1000):
    if _ == 50:
        pass
    evolve(pop)
    pop.analyse()

express(pop.best())
express(pop.best(), GENOTYPE)

print('')
print(datetime.now())
