class csLiteral:
    def __init__(self, valor):
        self.valor = valor
        self.polaridad = 1 if valor > 0 else -1
        self.asignacion = 0
        
        self.presencia = 0

        self.es_unitario = False
        self.nivel_de_decision = -1
        self.deducido_para_clausula = -1