from fitness.condition import Condition
from fitness.singleton import Singleton

from enum import Enum


class ConditionMap(object, metaclass=Singleton):
    def __init__(self):
        super().__init__()

        self._storage = dict()

    def __getitem__(self, k) -> Condition:
        from enum import Enum

        if k is None:
            return Condition(None, 'No conditions flagged')

        if isinstance(k, str):
            if k not in self._storage:
                return Condition(k, 'Undefined Condition')
            else:
                return self._storage[k]
        elif isinstance(k, Enum):
            return self.__getitem__(k.value.id)
        else:
            return NotImplemented

    def __setitem__(self, key, value):
        self._storage[key] = value

    def __len__(self) -> int:
        return len(self._storage)

    def __iter__(self):
        return iter(self._storage)

    def __apnd__(self, cond: Condition):
        if cond.id in self._storage.keys():
            return IndexError
        self[cond.id] = cond

    def load(self, data=None):
        self._storage = dict()

        if data is not None:
            for d in data:
                self.append(d)

    def append(self, cond):
        if isinstance(cond, Condition):
            self.__apnd__(cond)
        elif isinstance(cond, dict):
            self.__apnd__(Condition(**cond))
        else:
            return NotImplemented


class Conditions(Enum):
    NONE = None
    A = 'A'
    B = 'B'
    C = 'C'
    D = 'D'
    E = 'E'
    F = 'F'
    G = 'G'
    H = 'H'
    I = 'I'
    J = 'J'
    K = 'K'
    L = 'L'
    M = 'M'
    N = 'N'
    O = 'O'
    P = 'P'
    Q = 'Q'
    R = 'R'
    S = 'S'
    T = 'T'
    U = 'U'
    V = 'V'
    W = 'W'
    X = 'X'
    Y = 'Y'
    Z = 'Z'

    def object(self) -> Condition:
        return ConditionMap()[self.value]

    def score(self, **kwargs):
        c = self.object().base()
        score = c.score(**kwargs)
        return {'condition': c, 'score': score}
