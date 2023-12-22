
from clausula import csClausula
from literales import csLiteral

class solver:
    def __init__(self):
        self.literales_base = []
        self.clausulas_base = []

        self.literales = []
        self.clausulas = []

        self.backbones = []

        self.nivel_decision = 0
        self.cantidad_clausulas = 0
        self.clausulas_satisfechas = 0

        self.literales_asignados = 0

        #Variables globales para el proceso de backtrack:
        self.clausula_erronea = None

    def get_formula(self, ruta_formula):
        """
        Función que recibe la ruta donde se encuentra la fórmula a evaluar por el 
        SAT Solver.
        Además, se encarga de preparar el ambiente; clausulas y literales necesarios
        para la evaluación
        """
        #Abrir el archivo del problema
        ruta_problema = open(ruta_formula, "r")
        lineas = ruta_problema.readlines()

        literales_temp = []

        #Obtener las clausulas que son equivalentes a cada fila del archivo
        for linea in lineas:
            sep_linea = linea.split()
            n_clausula = csClausula()

            for item in sep_linea:      
                #c = comentarios, p = información del archivo
                if(item == "c" or item == "p"): break
                
                #Para facilitar la resolución más adeltante transformarlo a entero
                lit = int(item)

                #Añadir el literal a la claúsula y al resumen de los literales en fórmula
                n_clausula.literales.append(lit)
                if not abs(lit) in literales_temp: 
                    literales_temp.append(abs(lit))

            self.clausulas.append(n_clausula)

        self.cantidad_clausulas = len(self.clausulas) - 1

        self.literales_base = literales_temp
        self.clausulas_base = self.clausulas

        self.transformar_literales(literales_temp)
        self.get_backbones()     

    def transformar_literales(self, lista_literales):        
        lista_transformada = []
        cantidad_literales = len(lista_literales) + 1

        for i in range(1, cantidad_literales):
            literal = csLiteral(i)
            lista_transformada.append(i)
            self.literales.append(literal)

        for i in range(len(self.clausulas)):
            clausula = self.clausulas[i]
            clausula = self.transformar_clausula(clausula, lista_literales, lista_transformada)

    def transformar_clausula(self, clausula, literal_base, literal_transformado):
        for i in range (len(clausula.literales)):
            literal_clausula = clausula.literales[i]

            for j in range(len(literal_base)):
                literal_normal = literal_base[j]
                literal_modificado = literal_transformado[j]

                if abs(literal_clausula) == literal_normal: 
                    if literal_clausula < 0:
                        clausula.literales[i] = literal_modificado * -1
                    else:
                        clausula.literales[i] = literal_modificado
                    break
                
        return clausula

    def get_backbones(self):
        for clausula in self.clausulas:
            for literal in clausula.literales:  
                self.literales[abs(literal) - 1].presencia += 1

                if len(clausula.literales) == 1:
                    print(self.literales[abs(literal) - 1].valor)
                    self.literales[abs(literal) - 1].es_unitario = True
                else:
                    self.literales[abs(literal) - 1].es_unitario = False

    def ordenar_literales(self):
        """
        Ordenar los literales basado en los backbones y si son unitarios
        (aparecen en una claúsula como única variable)
        """
        # literales_sin_asignacion = []

        # #Obtener los literales que no han sido asignado un valor
        # for literal in self.literales:
        #     if literal.asignacion == 0: literales_sin_asignacion.append(literal)

        # literales_sin_asignacion = self.ordernar_por_presencia(literales_sin_asignacion);

        # self.backbones = literales_sin_asignacion

    def ordernar_por_presencia(self, literales):
        for i in range(len(literales)):
            for j in range(i + 1, len(literales)):
                if literales[i].presencia <= literales[j].presencia:
                    temp = literales[i]
                    literales[i] = literales[j]
                    literales[j] = temp

        return literales

    def verificar_literales_asignados(self):
        return self.literales_asignados == len(self.literales)

    def pick_literal(self, nivel_decision):
        """
        Seleccionar el literal basado en técnicas de decisiones 
        Se aplicará backbones.
        """
        for i in range(len(self.literales)):
            literal = self.literales[i]
            if literal.asignacion == 0:
                self.literales[i].asignacion = 1
                self.literales[i].nivel_de_decision = nivel_decision
                self.literales_asignados += 1
                break


    def predecir_literal(self, literal):
        return 1 if literal > 0 else -1

    def propagacion_unitaria(self, nivel_decision):
        literal_deducido = True

        while literal_deducido:
            literal_deducido = False

            for i in range(len(self.clausulas)):
                clausula = self.clausulas[i]

                ultimo_literal_sin_asignar = -1

                variables_sin_asignar = 0
                variables_falsificadas = 0

                clausula_satisfacida = False

                for literal in clausula.literales:
                    #Verificar si la clausula ya está satisfecha

                    lit = self.literales[abs(literal) - 1]
                    
                    #Si el resultado es positivo la clausula fue satisfacida
                    if lit.asignacion * literal > 0:
                        clausula_satisfacida = True
                        break

                    #Sí el valor de la asignación es 0 no ha sido asignada
                    if lit.asignacion == 0:
                        ultimo_literal_sin_asignar = literal
                        variables_sin_asignar += 1

                    if lit.asignacion * literal < 0:
                        variables_falsificadas += 1

                    if variables_falsificadas == len(clausula.literales):
                        self.clausula_erronea = clausula
                        return False
                    
                if variables_sin_asignar == 1 and not clausula_satisfacida:
                    self.literales_asignados += 1
                    valor = self.predecir_literal(ultimo_literal_sin_asignar)
                    self.literales[abs(ultimo_literal_sin_asignar) - 1].asignacion = valor
                    self.literales[abs(ultimo_literal_sin_asignar) - 1].nivel_de_decision = nivel_decision
                    self.literales[abs(ultimo_literal_sin_asignar) - 1].deducido_para_clausula = i
                    literal_deducido = True
        
        return True

    def backtrack(self, nivel_decision):
        
        literales_en_mismo_nd = 0
        nueva_clausula = self.clausula_erronea
        print("CLAUSULA CONFLICTO: ", nueva_clausula.literales)
        self.print_literales()
        while True:
            clausula_anidar = []
            literales_en_mismo_nd = 0

            #Sí la cantidad de literales en el mismo nivel de decisión es 1 entonces se 
            #encontró la nueva clausula

            for literal in nueva_clausula.literales:
                lit = self.literales[abs(literal) - 1]

                if lit.nivel_de_decision == nivel_decision: literales_en_mismo_nd += 1

                if lit.deducido_para_clausula != -1: 
                    clausula_anidar = self.clausulas[lit.deducido_para_clausula]
            
            if literales_en_mismo_nd < 2: break
            print("ERROR EN  ", nueva_clausula.literales)
            print("ANIDAR ", clausula_anidar.literales)
            nueva_clausula.literales = self.reducir_clausula(nueva_clausula, clausula_anidar)
            print("REDUCIDA  ", nueva_clausula.literales)
            print(nueva_clausula.literales, literales_en_mismo_nd)


        #Obtener el menor nivel de decisión presente en la clausula aprendida
        backtrack_nivel_decision = nivel_decision
        nivel_decision_literales = []

        for literal in nueva_clausula.literales:
            lit = self.literales[abs(literal) - 1]
            nivel_decision_literales.append(lit.nivel_de_decision)

        #Recorrer la clausula aprendida y obtener el menor nivel de decisión
        for i in range(len(nivel_decision_literales)):
            for j in range(i + 1, len(nivel_decision_literales)):
                if nivel_decision_literales[i] <= nivel_decision_literales[j] and  nivel_decision_literales[i] > -1:
                    backtrack_nivel_decision = nivel_decision_literales[i]

        for literal in self.literales:
            if self.literales[literal.valor - 1].nivel_de_decision == backtrack_nivel_decision:
                self.literales[literal.valor - 1].asignacion = 0
                self.literales[literal.valor - 1].deducido_para_clausula = -1
                self.literales[literal.valor - 1].nivel_de_decision = -1

                self.literales_asignados -= 1

        self.clausulas.append(nueva_clausula)
        print("N_CLAUSULA ", nueva_clausula.literales)
        return backtrack_nivel_decision  

    def solve(self, ruta_formula):
        self.get_formula(ruta_formula)

        if not self.propagacion_unitaria(self.nivel_decision):
            return False

        while not self.verificar_literales_asignados():
            #self.print_literales()
            self.nivel_decision += 1
            self.pick_literal(-1)

            if not self.propagacion_unitaria(self.nivel_decision):
                self.nivel_decision = self.backtrack(self.nivel_decision)

                print("BACK TO ", self.nivel_decision)
                self.propagacion_unitaria(self.nivel_decision)
                if self.nivel_decision < 0: return False
            
        return True

    def remover_literales_repetidos(self, clausula):
        clausula_depurada = []
        for i in clausula:
            if i not in clausula_depurada:
                clausula_depurada.append(i)
        return clausula_depurada
    
    def reducir_clausula(self, primera_clausula, segunda_clausula):
        #Hacer un vector general con todos los datos
        literales = primera_clausula.literales + segunda_clausula.literales

        literales = self.remover_literales_repetidos(literales)

        while(True):
            length = len(literales)
            found = False
            to_delete = -1
            for i in range(length):
                for j in range(i + 1, length):
                    if(literales[i] == -literales[j] and i != j):
                        found = True
                        to_delete = literales[i]   
                        break
                if(found): break            

            if(found):
                literales.remove(to_delete)
                literales.remove(-to_delete)
            else: break

        return literales

    def print_clausulas(self):
        for i in range(len(self.clausulas)):
            c = self.clausulas[i]
            for l in c.literales:
                print("CLAUSULA INDICE ", i, ' LITERAL ' , l)

    def print_literales(self):
        for i in range(len(self.literales)):
            c = self.literales[i]
            cb = self.literales_base[i]
            print("LITERAL: " , c.valor, " -> ", cb,  " LD: ", c.nivel_de_decision, " PRESENTE EN: ", c.presencia, " ES UNITARIO: ", c.es_unitario, " ASIGNACION: ", c.asignacion, " POR CLAUSULA: ", self.clausulas[c.deducido_para_clausula].literales if c.deducido_para_clausula >= 0 else 0)

    def print_literales_i(self, literales):
        for i in range(len(literales)):
            c = literales[i]            
            print("LITERAL: " , c.valor,  " PRESENTE EN: ", c.presencia, " ES UNITARIO: ", c.es_unitario)

solv =solver()
resultado = solv.solve('./pruebas/uf250-02.cnf')
solv.print_literales()
print("SAT" if resultado else "UNSAT")
