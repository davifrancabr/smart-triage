import heapq

class Triagem:
    def __init__(self):
        self.__fila = []
        self.__contador = 0

    def adicionar(self, paciente, prioridade):
        self.__contador = self.__contador + 1
        heapq.heappush(self.__fila, (prioridade, self.__contador, paciente))

    def chamarProximo(self):
        if len(self.__fila) == 0:
            return None
        item = heapq.heappop(self.__fila)
        return item[2]

    def mostrar(self):
        _int = None
        for a in self.__fila:
            _int =  {a["nome"], a["idade"], a["sintoma"]}
        return _int

    def quantidade(self):
        return len(self.__fila)
