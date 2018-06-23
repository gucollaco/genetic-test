import psycopg2


class Postgre:
    def __init__(self):
        super().__init__()

        self.connection = psycopg2.connect(host='localhost',
                           database='september',
                           user='postgres',
                           password='thinker')

    def kill(self):
        self.connection.close()

    def query(self, sql):
        result = []

        cur = self.connection.cursor()
        cur.execute(sql)
        recset = cur.fetchall()
        for rec in recset:
            result.append(rec)

        return result

    def execute(self, sql):
        cur = self.connection.cursor()
        cur.execute(sql)

        self.connection.commit()


if __name__ == '__main__':
    con = psycopg2.connect(host='localhost',
                           database='objects',
                           user='postgres',
                           password='thinker')

    cur = con.cursor()
    sql = "INSERT INTO materias VALUES (1, 'materia', '72h')"
    cur.execute(sql)

    con.commit()

    cur.execute('SELECT * FROM materias')
    recset = cur.fetchall()
    for rec in recset:
        print(rec)

    con.close()
    print('\nHold your breath and count to ten')