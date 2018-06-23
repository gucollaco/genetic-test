from objects.graduation_map import GraduationMap
from objects.user import User
from postgre import Postgre
from objects.aula import Aula
from objects.professor import Professor
from objects.materia import Materia

TABLE_CONVERSAO_HORARIOS = {"8h00-10h00": 0, "10h00-12h00": 1, "13h30-15h30": 2, "15h30-17h30": 3, "19h00-21h00": 4, "21h00-23h00": 5}


class Bridge:
    def __init__(self):
        super().__init__()

        self.materias = {}
        self.professores = {}
        self.aulas = {}

        self.student = None

        self.connection = None

    def kill(self):
        self.connection.kill()

    def sync(self, user, password, curso):
        self.fetch()
        self.intranet(user, password)

        Materia.ref_database(self)
        Professor.ref_database(self)
        Aula.ref_database(self)

        GRAD_MAPS = GraduationMap.generate(Materia, GraduationMap.excel(), (curso))

        self.student.link_summaries(Materia)
        self.student.graduation_map = GRAD_MAPS[curso]

    def fetch(self):
        self.connection = Postgre()

        materias = self.connection.query("SELECT * FROM materias")
        for m in materias:
            obj = Materia(m[0], m[1], m[2])

            requisitos = self.connection.query("SELECT requisito "
                                               "FROM pre_requisitos "
                                               "WHERE dependencia = {}".format(obj.id))
            for r in requisitos:
                obj.add_requisite(r[0])

            alternativos = self.connection.query("SELECT nome "
                                                 "FROM alternativos "
                                                 "WHERE materia = {}".format(obj.id))

            for a in alternativos:
                obj.alternativos.append(a[0])

            obj.ref_materiais(self.materias)
            self.materias[obj.id] = obj

        professores = self.connection.query("SELECT * FROM professores")
        for p in professores:
            obj = Professor(p[0], p[1], p[2], p[3])
            self.professores[obj.id] = obj

        aulas = self.connection.query("SELECT * FROM aulas")
        for a in aulas:
            obj = Aula(a[0], a[3], a[4], a[5])

            horarios = self.connection.query("SELECT dia, horario "
                                             "FROM horarios "
                                             "WHERE aula = {}".format(obj.id))
            for h in horarios:
                obj.horarios.append((h[0], TABLE_CONVERSAO_HORARIOS[h[1]]))

            obj.set_materia(a[1])
            obj.set_professor(a[2])

            obj.ref_materias(self.materias)
            obj.ref_professores(self.professores)
            self.aulas[obj.id] = obj

    def intranet(self, user, password):
        self.student = User(user, password, subscribed=True, load=True, save=True)


if __name__ == "__main__":
    db = Bridge()

    db.sync('dsalexandre', 'HelenOfTroy1', 'ECOMP')

    print(db)