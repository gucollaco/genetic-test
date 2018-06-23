from objects.aula import Aula
from objects.materia import Materia


class GraduationMap(list):
    def __init__(self, name=None):
        list.__init__(self)

        self.name = name
        self.index = {}

        self.specials = {}

    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self)

    def __contains__(self, item):
        if isinstance(item, Materia):
            return list.__contains__(self, item)
        elif isinstance(item, str):
            return self.__contains__(Materia.find(item))
        elif isinstance(item, int):
            return item in self.index.keys()
        else:
            return NotImplemented

    def set_data(self, catalog, data):
        self.name = data['name']

        for i, item in enumerate(data['ucs'].items()):
            term, ucs = item
            for uc_name_raw in ucs:
                uc_name = uc_name_raw
                if uc_name[0] == '*':
                    uc_name = uc_name[1:]
                elif uc_name[0] == '[' and uc_name[-1] == ']':
                    uc_name = uc_name[1:-1]

                    if uc_name not in self.specials.keys():
                        self.specials[uc_name] = []
                    self.specials[uc_name].append({'term': term})

                    continue

                materia = catalog.find(uc_name, minimum=95)

                if materia is None:
                    print("ERROR: Couldn't find summary for <{}>".format(uc_name))
                else:
                    if materia.nome in self.index.keys():
                        print('ERROR: Same summary appears multiple times at graduation map')

                    self.append(materia)
                    self.index[materia.id] = {'term': term}

        self.sort(key=lambda x: self.get_term(x))

    def get_term(self, uc):
        id = ''
        if isinstance(uc, (Materia, Aula)):
            id = uc.id
        elif isinstance(uc, str):
            id = Materia.find(uc).id
        elif isinstance(uc, int):
            id = uc
        else:
            return NotImplemented

        if id in self.index.keys():
            return int(self.index[id]['term'].lower().replace('termo ', ''))
        else:
            return -1

    def get_dependencies(self, item, height=-1):

        e = item

        dependencies = []
        for i in self:
            if e in i.requisites:
                dependencies.append(i)
                if height != 1:
                    dependencies += self.get_dependencies(i, height-1)

        return dependencies

    @staticmethod
    def excel(path='mapa_graduacao.xlsx') -> dict():
        from xlrd import open_workbook

        wb = open_workbook(path)

        sheet = wb.sheets()[0]
        for sheet in wb.sheets():
            if sheet.name == 'Mapas':
                break

        mapas = []
        for c in range(sheet.ncols):
            mapa = dict()
            mapa['name'] = sheet.cell(0, c).value
            mapa['ucs'] = {}

            ucs = []
            termo = 1
            for r in range(2, sheet.nrows):
                value = sheet.cell(r, c).value

                if value != "":
                    ucs.append(value)
                elif len(ucs) > 0:
                    mapa['ucs']['Termo ' + str(termo)] = list(ucs)

                    ucs = []
                    termo += 1

            mapas.append(mapa)

        return mapas

    @staticmethod
    def generate(catalog, dataList, filter=None) -> list():
        result = {}
        for data in dataList:
            if filter is not None:
                if data['name'] not in filter:
                    continue

            gp = GraduationMap()
            gp.set_data(catalog, data)
            result[gp.name] = gp

        return result


if __name__ == '__main__':
    from objects.materia import Materia
    from access.bridge import Bridge

    database = Bridge()
    database.fetch()
    Materia.ref_database(database)

    GRAD_MAPS = GraduationMap.generate(Materia, GraduationMap.excel(path='..\mapa_graduacao.xlsx'), ('ECOMP'))

    print('')
    print(Materia.find('Análise Real II') in GRAD_MAPS['ECOMP'])
    print('')