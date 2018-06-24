import os

import time

from objects.aula import Aula
from objects.materia import Materia
from objects.graduation_map import GraduationMap
from selenium import webdriver
from bs4 import BeautifulSoup as Soup
from auxiliar import file, word
import re
from collections import OrderedDict

INTRANET_HOME = 'https://intranet.unifesp.br'
INTRANET_LOGIN = 'https://intranet.unifesp.br/restrict/index3.php'

INTRANET_HISTORICO = 'https://www3.unifesp.br/prograd/app_prograd/he_novo/he_aluno_cns_lista_cursos/he_aluno_cns_lista_cursos.php'

MINIMUM_MATCHING_RATIO = 95


class User:
    def __init__(self, username, password=None, subscribed=False, run=True, load=False, save=False):
        self.login = {'username': username, 'password': password}
        self.subscribed = subscribed

        self.fullname = ''
        self.course = ''
        self.id = ''
        self.last_update = ''

        self._history = {}
        self.subscriptions = {}
        self.preferences = []

        self._simulated_term = None

        self.graduation_map = None

        if run:
            if load or password is None:
                if not self.load():
                    print('Could not load data for user <{}>'.format(username))
                    if password is not None: self.update(save=save)
            else:
                if password is not None: self.update(save=save)

    def __dict__(self):
        data = dict()
        data['login'] = self.login
        data['subscribed'] = self.subscribed
        data['fullname'] = self.fullname
        data['course'] = self.course
        data['id'] = self.id
        data['history'] = self._history
        data['subscriptions'] = self.subscriptions
        data['preferences'] = self.preferences
        data['last_update'] = self.last_update

        return data

    def __iter__(self):
        yield ('login', self.login)
        yield ('subscribed', self.subscribed)
        yield ('fullname', self.fullname)
        yield ('course', self.course)
        yield ('id', self.id)
        yield ('history', self._history)
        yield ('subscriptions', self.subscriptions)
        yield ('preferences', self.preferences)
        yield ('last_update', self.last_update)

    def update(self, save=False):
        # todo Adicionar loop para caso o chrome crashe e nao abra
        chrome = webdriver.Chrome()
        chrome.get(INTRANET_HOME)

        chrome.find_element_by_name('username').send_keys(self.login['username'])
        chrome.find_element_by_name('password').send_keys(self.login['password'])
        chrome.find_element_by_name('password').submit()

        self.fetch_history(chrome)
        if self.subscribed:
            self.fetch_subscriptions(chrome)

        chrome.quit()

        self.get_preferences()

        self.last_update = time.strftime("%Y-%m-%d %H:%M:%S", time.gmtime())

        if save: self.save()

    '''UNIDADES CURRICULARES'''
    def fetch_history(self, chrome):
        chrome.get(INTRANET_HOME)
        chrome.execute_script('mostraTopico(8);')
        chrome.execute_script("mostraAplicativo('887');")

        self._history['ucs'] = []
        # todo Refinar esse sleep, tem q ser dinâmico
        time.sleep(10)
        chrome.get(INTRANET_HISTORICO)
        beau = Soup(chrome.find_element_by_tag_name('html').text, 'lxml')

        index = -1
        text_html = beau.text.split('\n')
        i = 4
        while i < len(text_html):
            if 'ALUNO EM CURSO' in text_html[i]:
                index = i - 4
            i += 1

        i = 0
        for a in chrome.find_elements_by_css_selector('a'):
            if a.text.lower().find("histórico") != -1:
                if i == index:
                    a.click()

                i += 1

        # done Do histórico, puxar as seguinter informações: Curso, Matrícula, Nome, UC's cursadas
        beau = Soup(chrome.find_elements_by_css_selector('html')[0].get_attribute('innerHTML'), 'lxml')
        td_scGridHeaderFont = beau.select('td.scGridHeaderFont')
        self.cr = float([e.text for e in td_scGridHeaderFont if e.text.lower().find("coefic.") != -1][0].lower().replace('coefic. rendimento: ', '').replace(',', '.'))

        tr_scGridLabel = beau.select('td#sc_grid_body table tr.scGridLabel > td')
        for tr in beau.select('td#sc_grid_body table tr'):  # um TR para cada informação
            if tr.get('class') is None:  # informação bruta, nao sub tabela
                tr_text = tr.text.split(': ')

                if tr_text[0].lower() == 'curso':
                    self.course = tr_text[1]
                elif tr_text[0].lower() == 'matrícula':
                    self.id = tr_text[1]
                elif tr_text[0].lower() == 'nome':
                    self.fullname = tr_text[1]

            elif 'scGridLabel' not in tr.get('class'):  # subtabela de cursos
                uc = {}
                for i, span in enumerate(tr.text.split('\n')):  # para cada coluna
                    if i-1 >= len(tr_scGridLabel): break

                    k = tr_scGridLabel[i-1].text
                    v = span

                    v = re.sub('^([\s ]+\\b)', '', v)
                    v = re.sub('(\\b[\s ]+)$', '', v)

                    uc[k] = v

                self._history['ucs'].append(uc)

    def ucs(self, status=None, model="MINIMALIST"):
        if status is None:
            status = ['APROVADO', 'REPROVADO', 'EM_CURSO']

        if model == "MINIMALIST":
            return [u['Código - Unidade Curricular'].split(' - ')[1] for u in self._history['ucs'] if u['Situação'] in status]
        elif model == "COMPLEX":
            return [[u['Código - Unidade Curricular'].split(' - ')[0],
                     u['Código - Unidade Curricular'].split(' - ')[1],
                     u['Turno'],
                     u['Carga Horária']] for u in self._history['ucs'] if u['Situação'] in status]
        elif model == "SIMPLE":
            return [[
                        u['Código - Unidade Curricular'].split(' - ')[1],
                        u['Turno']
                    ] for u in self._history['ucs'] if u['Situação'] in status]

    def past_ucs(self, model="MINIMALIST"):
        return self.ucs(status=['APROVADO', 'REPROVADO'], model=model)

    def current_ucs(self, model="MINIMALIST"):
        return self.ucs(status=['EM CURSO'], model=model)

    def link_summaries(self, catalog):
        import math
        from auxiliar.word import simplify, tokenize, similarity

        activation = lambda x: math.fabs((math.log1p(math.fabs(x - 100)) / math.log1p(100)) ** 2 - 1)

        objs = []

        for uc in self._history['ucs']:
            code = uc['Código - Unidade Curricular'][:uc['Código - Unidade Curricular'].find(' - ')]
            name = uc['Código - Unidade Curricular'][uc['Código - Unidade Curricular'].find(' - ')+3:]

            obj = {
                "object": None,
                "code": code,
                "year": uc['Ano Letivo'],
                "concept": float(uc['Conceito'].replace(',', '.')) if uc['Conceito'] != '' else 0,
                "status": uc['Situação'],
                "term": uc['Série / Termo'],
                "shift": uc['Turno']
            }

            tokens = tokenize(name)

            corr = []
            for label in tokens:
                search = catalog.find(label, limit=1, detail=True, fast=True)
                corr += [s + [label] for s in search]
                if search[0][1] == 100:  # CORRESPONDENCIA EXATA
                    break
            corr.sort(key=lambda x: x[1], reverse=True)

            if corr[0][1] >= MINIMUM_MATCHING_RATIO:
                obj['object'] = corr[0][0]
            else:
                raise NotImplementedError('Comparacao por similaridade nao implementada')
                corr_similarity = []
                for c in corr:
                    corr_similarity += [{
                        'ementa': c[0],
                        'name': a,
                        'label': c[2],
                        'ratio': c[1],
                        'similarity': similarity(a, c[2], simplify),
                        'composite_ratio': activation(similarity(a, c[2], simplify)) * 25 + c[1]
                    } for a in c[0].alternativos if similarity(a, c[2], simplify) >= 50]

                similars = {}
                for c in corr_similarity:
                    if c['ementa'].name().name not in similars.keys():
                        similars[c['ementa'].name().name] = c
                    else:
                        if similars[c['ementa'].name().name]['composite_ratio'] < c['composite_ratio']:
                            similars[c['ementa'].name().name] = c

                list_similars = list(similars.values())
                list_similars.sort(key=lambda x: x['composite_ratio'], reverse=True)


                composite_ratio = 0


            objs.append(obj)

        self._history['objects'] = objs

    def calc_total_credits(self):
        return sum([m['object'].credit for m in self._history['objects'] if m['status'] == 'APROVADO'])

    def has_requisites(self, uc):
        if isinstance(uc, str):
            rs = [r.id for r in Materia.find(uc).requisites]
        elif isinstance(uc, Materia):
            rs = [r.id for r in uc.requisites]
        elif isinstance(uc, Aula):
            rs = [r.id for r in uc.materia.requisites]
        else:
            return NotImplemented

        ids = [obj['object'].id for obj in self._history['objects'] if obj['status'] == 'APROVADO']
        return all(r in ids for r in rs)

    def get_current_term(self):
        return max([int(uc['term']) for uc in self._history['objects'] if uc['status'] != "EM CURSO"]) + 1

    def get_preferences(self, path='preferences.json'):
        pref = file.load(path)

        self.preferences = pref

    def simulate_term(self, term):
        self._simulated_term = term

    @property
    def history(self):
        if self._simulated_term is None:
            return self._history

        simulated_history = {}

        if 'ucs' in self._history:
            simulated_history['ucs'] = [uc for uc in self._history['ucs'] if int(uc['Série / Termo']) <= self._simulated_term]

        if 'objects' in self._history:
            simulated_history['objects'] = [obj for obj in self._history['objects'] if int(obj['term']) <= self._simulated_term]

        return simulated_history


    '''GRADE'''
    def fetch_subscriptions(self, chrome):
        weekday_index = {
            'SEG': 'Segunda',
            'TER': 'Terça',
            'QUA': 'Quarta',
            'QUI': 'Quinta',
            'SEX': 'Sexta',
        }

        chrome.get(INTRANET_HOME)
        chrome.execute_script('mostraTopico(8);')
        chrome.execute_script("mostraAplicativo('886');")
        time.sleep(10)

        # todo Fazer opcao para criar atestado caso o cara n tenha
        chrome.get('https://www3.unifesp.br/prograd/app/atestados/index.php/atestado')

        beau = Soup(chrome.find_elements_by_css_selector('html')[0].get_attribute('innerHTML'), 'lxml')
        rows = beau.select('div#content table tbody tr')

        header = []
        table = {}
        i = 0
        for row in rows:
            if i == 0:
                header = [th.text for th in row.select('th')]
            else:
                data = {}
                j = 0
                for td in row.select('td'):
                    h = header[j]
                    if h == 'LISTA DE UNIDADES CURRICULARES MATRICULADO':
                        h = 'UC'

                    t = td.text
                    t = re.sub('^([\s ]+\\b)', '', t)
                    t = re.sub('(\\b[\s ]+)$', '', t)

                    data[h] = t

                    # format data
                    if h == 'TURNO' and t != '':
                        data[h] = data[h][0]
                    elif h == 'DIA' and t != '':
                        data[h] = weekday_index[data[h]]
                    elif (h == 'INÍCIO' or h == 'TÉRMINO') and t != '':
                        dado = data[h]
                        dado = re.sub('([0-9]+[.][0-9])H', r'\g<1>0', dado)
                        dado = re.sub('([^.][0-9])H', r'\g<1>:00', dado)
                        dado = re.sub('[.]', ':', dado)

                        data[h] = dado
                    j += 1

                # pegar uc correspondente do historico
                uc = ''
                for nome in self.current_ucs():
                    n = word.clear(nome, singular=True)
                    u = word.clear(data['UC'], singular=True)
                    if n == u:
                        uc = nome
                        break

                if uc == '':
                    print('ERROR: Subbed UC cant find match at history')
                    print('AT: ' + str(data))
                    return None

                if uc in table:
                    table[uc].append(data)
                else:
                    table[uc] = [data]

            i += 1

        # para UCS que estao EM CURSO no historico mas não aparecem nas
        # mastriculas sabe-se la porque, tentar adivinhar o horario
        for codigo, nome, turno, carga in self.current_ucs('COMPLEX'):
            if nome not in table:  # advinhar
                data = {
                    "DIA": '',
                    "CÓDIGO": codigo,
                    "TÉRMINO": '',
                    "INÍCIO": '',
                    "UC": nome,
                    "TURNO": turno
                }

                table[nome] = [data]
                if carga in ('72', '108'):
                    table[nome].append(data)
                    if carga == '108':
                        table[nome].append(data)

        self.subscriptions = table

    def grid(self, target=''):
        if not self.subscribed:
            return None

        g = OrderedDict()

        # modelar a grade
        weekdays = ['Segunda', 'Terça', 'Quarta', 'Quinta', 'Sexta']
        times = ['08:00', '10:00', '13:30', '15:30', '19:00', '21:00']
        for wd in weekdays:
            g[wd] = OrderedDict()
            for t in times:
                g[wd][t] = {}

        for uc, classes in self.subscriptions.items():
            for c in classes:
                if c['DIA'] == "":  # colocar como desconhecido, a ser descoberto na grade expandida
                    if 'Desconhedido' not in g:
                        g['Desconhecido'] = {c['TURNO']: {}}
                    g['Desconhecido'][c['TURNO']]['uc'] = uc
                else:
                    g[c['DIA']][c['INÍCIO']]['uc'] = uc

        if target != '':
            file.save(g, target, True)

        return g

    def prepare_grid(self, catalogo):
        from september.matrix.matrix_uc import MatrixUC
        from september.matrix.lecture import Lecture
        from september.matrix.lecture_time import LectureTime

        ucs = []
        for k, list_sub in self.subscriptions.items():
            uc = MatrixUC()
            uc.tokenize_label(k)
            for sub in list_sub:
                uc.add_lecture(Lecture(time=LectureTime(sub['DIA'], sub['INÍCIO'].replace(':', 'h') + '-' + sub['TÉRMINO'].replace(':', 'h'), '', self.get_current_term()), shift=sub['TURNO']))
            uc.set_summary(catalogo.find(k))
            ucs.append(uc)

        self._history['grid'] = ucs

    def sync_agenda(self, agenda):
        from september.matrix.lecture_time import LectureTime
        from september.agenda.booking_time import BookingTime
        from fuzzywuzzy import fuzz

        history_agenda = {}
        term = self.get_current_term()

        sync_fails = []
        stack_ucs = [i for i in range(len(self._history['grid']))]

        for index_uc in stack_ucs:
            uc = self._history['grid'][index_uc]
            aftermath = index_uc in sync_fails

            possibilities = [{'booking': b, 'tags': [[t[-1], uc.summary.compareName(t[-1])] for t in b.tags], 'shifts': [[t[-1], fuzz.ratio(t[-1].upper(), 'TURMA ' + uc.shift)] for t in b.tags]} for b in agenda.reservations]
            for p in possibilities:
                valid_scores = [t[1] for t in p['tags'] if t[1] >= 60]
                valid_scores += [t[1] for t in p['shifts'] if t[1] >= 60]

                p['score'] = 0 if len(valid_scores) == 0 else sum(valid_scores)/len(valid_scores)

            possibilities = [p for p in possibilities if any(t[1] >= 95 for t in p['tags']) and any(t[1] >= 75 for t in p['shifts'])]
            possibilities.sort(key=lambda x: x['score'], reverse=True)

            exact_matches = []
            if aftermath:
                # matches nao exatos, nao tem-se a informacao especifica da classe
                inexact_matches = [p for p in possibilities if p['score'] >= 95 and all(self.is_time_avaliable(b[0]) for b in p['booking'].bookings)]

                if len(inexact_matches) != 1:
                    print("ERROR: Couldn match booking and uc even with fail syncing for <{}>".format(uc.name()))
                else:
                    exact_matches = inexact_matches[:1]
            else:
                exact_matches = [p for p in possibilities if p['score'] >= 100]

            if len(exact_matches) != 1:
                possibilities2 = []
                for lecture in uc.schedules:
                    if not lecture.isincomplete():
                        possibilities2 += [p for p in possibilities if any(any(t == list(b[0]) for b in p['booking'].bookings) for t in lecture.time)]

                if len(possibilities2) == 1:
                    exact_matches = possibilities2
                    print('WARNING: Matching entries by lecture time and booking time for <{}>'.format(str(uc.summary.name())))
                else:
                    if not aftermath:
                        print('ERROR: Multiple correspondences for <{}>'.format(uc.name()))
                        sync_fails.append(index_uc)
                        stack_ucs.append(index_uc)

            if len(exact_matches) == 1:
                booking = exact_matches[0]['booking']
                history_agenda[uc.summary.name()] = booking

                for lecture in uc.schedules:
                    # todo correlate professsor based on list
                    if not lecture.hasprofessor():
                        lecture.professor = booking.subject

                    if lecture.isincomplete() or lecture.ispartiallycomplete(uc.summary.workload):
                        lecture.time = []
                        for time, rooms in booking.bookings:
                            t = LectureTime(time.weekday, time.time, '', term)
                            t.room = rooms
                            lecture.add_time(t)
                        print("WARNING: Correcting lecture times for <{}>".format(uc.name()))
                    elif not lecture.iscorrect():
                            print("WARNING: Lecture doesn't possess consistente shift data, agenda correlation might "
                                  "be wrong")
                    elif not lecture.hasrooms():
                        for time in lecture.time:
                            booking_time = BookingTime.parse(time)
                            time.room = booking.rooms[booking_time]

            self._history['agenda'] = history_agenda

    def is_time_avaliable(self, time):
        for b in self._history['agenda'].values():
            for bt in b.bookings:
                if bt[0] == time:
                    return False

        return True

    '''PERSISTENCIA DOS DADOS'''
    def save(self, path='./out/users/'):
        if not os.path.exists(path):
            os.makedirs(path)

        file_name = '{}_{}.json'.format(self.login['username'], self.last_update.replace("-", "_").replace(':', '_'))
        file.save(dict(self), path + file_name, False)

    def load(self, path=None):
        if path is None:
            if not os.path.exists('./out/users'):
                return False

            bigger_time = None
            for f in os.listdir('./out/users'):
                m = re.match('{}_([_0-9\s]+).json'.format(self.login['username']), f)
                if m:
                    t = time.strptime(m.group(1), '%Y_%m_%d %H_%M_%S')
                    if bigger_time is None: bigger_time = t

                    if t >= bigger_time:
                        path = f
                        bigger_time = t

        if path is None:
            return False

        data = file.load('./out/users/' + path)

        self.login = data['login']
        self.subscribed = data['subscribed']
        self.fullname = data['fullname']
        self.course = data['course']
        self.id = data['id']
        self._history = data['history']
        self.subscriptions = data['subscriptions']
        self.preferences = data['preferences']
        self.last_update = data['last_update']

        return True


if __name__ == '__main__':
    from objects.materia import Materia
    from access.bridge import Bridge

    database = Bridge()
    database.sync()

    print('Accessing user...')
    u = User('dsalexandre', 'HelenOfTroy1', subscribed=True, load=True, save=True)
    # u.load('../out/users')
    u.link_summaries(Materia)
    print('total credits: {}'.format(u.calc_total_credits()))
    print(u.has_requisites(Materia.find('Análise Real II')))
    print('')
