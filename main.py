import random
import sys


def avalia_senha(indiv, senha):
    value = 0
    for i in range(len(senha)):
        if i < len(indiv):
            if indiv[i] == senha[i]:
                value += 1

    return value


def mutacao(ind, probMut, opcoes):
    for i in range(len(ind)):
        if random.uniform(0, 1) < probMut:
            ind[i] = random.sample(opcoes, 1)[0]

    return ind


def cruzamento(ind1, ind2):
    novo_ind = list(ind1)

    if len(ind1) < 2 or len(ind1) != len(ind2): return novo_ind
    else: corte = random.sample(range(1, len(ind1)), 1)[0]

    for i in range(corte, len(novo_ind)):
        novo_ind[i] = ind2[i]

    return novo_ind


def torneio(aptidao, tamanho):
    id_compet = list(range(len(aptidao)))
    competidores = random.sample(id_compet, tamanho)
    fit = [aptidao[idx] for idx in competidores]
    v1 = competidores[fit.index(min(fit))]

    id_compet.remove(v1)
    competidores = random.sample(id_compet, tamanho)
    fit = [aptidao[idx] for idx in competidores]
    v2 = competidores[fit.index(min(fit))]

    return v1, v2


def ga(fun, senha, nDim, opcoes, tamPop, tamTorneio, probMut, porcCr, nGeracoes):
    pop = [[random.sample(opcoes, 1)[0] for i in range(nDim)] for j in range(tamPop)]
    aptidao = [fun(indiv, senha) for indiv in pop]

    for ger in range(nGeracoes):
        for cruzamentos in range(int(tamPop * porcCr)):
            v1, v2 = torneio(aptidao, tamTorneio)

            pai1, pai2 = pop[v1], pop[v2]
            filho = mutacao(cruzamento(pai1, pai2), probMut, opcoes)

            pop.append(filho)
            aptidao.append(fun(filho, senha))

        ordem = sorted(range(len(aptidao)), key=lambda k: aptidao[k], reverse=True)

        for idx in range(tamPop):
            aptidao[idx] = aptidao[ordem[idx]]
            pop[idx] = pop[ordem[idx]]

        aptidao = aptidao[:tamPop]
        pop = pop[:tamPop]

        if aptidao[0] == nDim:
            break

    return ''.join(pop[0])

SEED = 1
random.seed(SEED)

opcoes = "abcdefghijklmnopqrstuvwxyz "
