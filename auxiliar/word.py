from unicodedata import normalize, combining
from re import sub, search

PREPOSICOES = ["e", "de", "do", "dos", "das", "da", "em", "para", "E", "DE", "DO", "DOS", "DAS", "DA", "EM", "PARA"]


def clear(palavra, permitidos='', palavras_negadas=[], singular=False, acentos=False, genero=True):

    # Unicode normalize transforma um caracter em seu equivalente em latin.
    palavraSemAcento = palavra
    if not acentos:
        nfkd = normalize('NFKD', palavra)
        palavraSemAcento = u"".join([c for c in nfkd if not combining(c)])
    else:
        permitidos += 'áàâãéèêíïóôõöúçñÁÀÂÃÉÈÍÏÓÔÕÖÚÇÑ'

    palavraSemAcento = palavraSemAcento.replace('-', ' ')

    # Usa expressão regular para retornar a palavra apenas com números, letras e espaço
    result = sub('[^a-zA-Z0-9' + permitidos + ' \\\]', '', palavraSemAcento)
    result = sub('\\b({0})\\b'.format("|".join(palavras_negadas)), '', result)
    result = sub('\s+', ' ', result)
    result = sub('\s+', ' ', result)
    result = sub('\s+', ' ', result)

    if singular and len(result) > 3:
        replacement = ''
        for w in result.split(' '):
            if len(w) > 3:
                replacement += sub('(?<=[\w*])([sS])\\b', '', w) + ' '
            else:
                replacement += w + ' '
        result = replacement[:-1]
        # result = sub('(?<=[\w*])([sS])\\b', '', result)

    if not genero and len(result) > 4:
        result = sub('(?<=[\w*])([aAoO])\\b', '', result)

    return result


def replace(string, dicionario):
    result = string
    for original, substititute in dicionario.items():
        result = sub('\\b{0}\\b'.format(original), substititute, result)

    return result


def tokenize(string, stop=False):
    DICT_NUMERALS = {'1': 'I', '2': 'II', '3': 'III', '4': 'IV', '5': 'V'}
    if 'Linear' in string:
        aq = 'msm'


    # todo improve tokenize method
    if '(' in string and not stop:
        result = []
        result += tokenize(string, True)
        result += tokenize(string[:string.find('(')].strip())
        result += tokenize(string[string.find('(') + 1:].replace(')', '').strip())
        return result
    elif search('[{}]'.format(''.join(DICT_NUMERALS.keys())), string) and not stop:
        result = string
        for n, a in DICT_NUMERALS.items():
            result = result.replace(n, a)

        r = tokenize(string, True)
        r += tokenize(result, True)
        return r
    elif len(string.split(' ')) > 1:
        from re import split

        result = []
        versions = [string]

        # words = [w for w in split('[^áàâãéèêíïóôõöúçñÁÀÂÃÉÈÍÏÓÔÕÖÚÇÑa-zA-Z0-9]+', string) if len(w) > 3]
        words = [w for w in split('[^áàâãéèêíïóôõöúçñÁÀÂÃÉÈÊÍÏÓÔÕÖÚÇÑa-zA-Z0-9]+', string)]
        index = []
        for i in reversed(range(len(words))):
            if len(words[i]) > 3:
                words[i] = words[i][0]
                index.append(i)

                w = ''
                j = 0
                for j in range(len(words)):
                    w += words[j]
                    if j+1 < len(words):
                        if j not in index or j+1 not in index:
                            w += ' '

                versions.append(w)

        w = ''
        j = 0
        for j in range((len(words))):
            from summary.lecture_name import LectureName
            if j in index:
                w += words[j]
            elif words[j] not in LectureName.PREPOSICOES:
                w += words[j]

        if w not in versions:
            versions.append(w)

        return versions
    else:
        return [string]


def similarity(a, b, modification=None):
    wordA = a
    wordB = b

    if modification is not None:
        wordA = modification(a)
        wordB = modification(b)

    score = 0
    from summary.lecture_name import LectureName
    words_in_a = [w for w in wordA.split(' ') if len(w) > 3 or w not in LectureName.PREPOSICOES]
    words_in_b = [w for w in wordB.split(' ') if len(w) > 3 or w not in LectureName.PREPOSICOES]

    for w in words_in_a:
        if w in words_in_b:
            score += 1

    for w in words_in_b:
        if w in words_in_a:
            score += 1

    return int((score*100/2) / max(len(words_in_a), len(words_in_b)))


def simplify(name):
    return clear(name.lower(), palavras_negadas=PREPOSICOES, singular=True, genero=False).upper()


def ratio(word, other):
    from fuzzywuzzy import fuzz

    return fuzz.ratio(simplify(word), simplify(other))

# todo Adicionar a função CAPTALIZE, q eu criei no auxiliar module em matriz horaria


if __name__ == '__main__':
    from fuzzywuzzy import  fuzz
    print(tokenize('Ciencia, Tecnologia e Sociedade'))
    print(tokenize('Algoritmos e Estruturas de Dados II'))
    print(tokenize('Metodologia da Pesquisa e Comunicação Científica'))
    print(tokenize('Metodologia da Pesq e Com Científica'))
    print(tokenize('Laboratório de Sistemas Computacionais: Arquitetura e Organização de Computadores'))
    print(tokenize('Arquitetura e Organização de Computadores'))

    print(fuzz.ratio('MPCC', 'MPComC'))
    print(fuzz.ratio('AOC', 'LSCAOC'))