class FilaPrioridade:
    def __init__(self):
        self._heap = []

    def __len__(self):
        return len(self._heap)

    def vazia(self):
        return len(self._heap) == 0

    def inserir(self, chave, item):
        self._heap.append((chave, item))
        self._subir(len(self._heap) - 1)

    def remover(self):
        if self.vazia():
            raise IndexError("Fila vazia")
        topo = self._heap[0]
        ultimo = self._heap.pop()
        if self._heap:
            self._heap[0] = ultimo
            self._descer(0)
        return topo[1]

    def espiar(self):
        return self._heap[0][1] if self._heap else None

    def ordenada(self):
        copia = FilaPrioridade()
        copia._heap = list(self._heap)
        saida = []
        while not copia.vazia():
            saida.append(copia.remover())
        return saida

    def _subir(self, i):
        while i > 0:
            pai = (i - 1) // 2
            if self._heap[i][0] < self._heap[pai][0]:
                self._heap[i], self._heap[pai] = self._heap[pai], self._heap[i]
                i = pai
            else:
                break

    def _descer(self, i):
        n = len(self._heap)
        while True:
            esq, dir_ = 2 * i + 1, 2 * i + 2
            menor = i
            if esq < n and self._heap[esq][0] < self._heap[menor][0]:
                menor = esq
            if dir_ < n and self._heap[dir_][0] < self._heap[menor][0]:
                menor = dir_
            if menor == i:
                break
            self._heap[i], self._heap[menor] = self._heap[menor], self._heap[i]
            i = menor
