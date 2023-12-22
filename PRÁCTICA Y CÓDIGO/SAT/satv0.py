class solver:
    #Things that makes the solver works:
    clauses  = []
    literals = []
    variable = []

    #start quantity
    s_quantity_clauses = 0    
    
    #The level decision of the literal
    decision_level_for_literal = []

    #Save the index of the clause, too called the reason or the trail
    index_clause_of_deduce_literal = []

    #Index to acces to the literals and vars (values assigned)
    index_literals_and_var = []
    #Count the assigned literals
    count_assigned_literals = 0

    #Variable to save the clause which generate a conflict
    incident_clause = -1
    
    #Variable for heuristic
    literals_polarity = []

    relevance_literal = []

    #Method to get each clause, reading a txt or other file (default a txt)
    def get_problem(self, pathfile):
        #Open the file
        problem_file = open(pathfile, "r")
        lines = problem_file.readlines()

        #Use a cycle to get each line and save the clauses
        for line in lines:
            add = False
            clause = line.split()
            for i in range(len(clause)):       
                #If a line contains a "c" then that line doesn't matter
                if(clause[i] == "c" or clause[i] == "p"):
                    break
                clause[i] = int(clause[i])
                #If the line contains a 0, then that line doesn't matter
                if(clause[i] == 0):
                    clause.pop()
                add = True
            if(add):
                self.clauses.append(clause)
                self.clauses = sorted(self.clauses, key = len)
                self.get_literals(-1)

        #Save the index of each literal
        self.literals_to_vector_index()
        
        self.s_quantity_clauses = len(self.clauses)

    #Method to save every literal
    def get_literals(self, index):
        #Run the clause and save the literals
        for i in range(len(self.clauses[index])):
            if(not self.literals.__contains__(abs(self.clauses[index][i]))):
                #Set the literals, polarity, values, ld and trail to default
                self.literals.append(abs(self.clauses[index][i]))
                self.literals_polarity.append(0)
                self.variable.append(0)
                self.relevance_literal.append(0)
                self.decision_level_for_literal.append(0)
                self.index_clause_of_deduce_literal.append(0)

            #For and check if the literal is equal than a literal saved in the vector
            #then check if is negative (-), minus the polarity else increase (+) by 1
            for j in range(len(self.literals)):
                if self.literals[j] == abs(self.clauses[index][i]):
                    if self.clauses[index][i] < 0:
                        self.literals_polarity[j] -= 1
                    else:
                        self.literals_polarity[j] += 1

                    #The literal is founded, then break the cycle.
                    break

    #Method that save in a vector the index of the literals
    def literals_to_vector_index(self):
        #Save the max value of the literal in vector
        max_number_literal = max(self.literals)   

        #The vector saves the index of the literals, then the size is equal to the max number + 1
        for i in range(max_number_literal + 1):
            self.index_literals_and_var.append(None)

        for i in range(max_number_literal + 1):
            for j in range(len(self.literals)):
                #If is equal the index has founded, then break
                if(i == self.literals[j]):
                    self.index_literals_and_var[i] = j
                    break

    #Method that recieve the literal signed and return the index of the literal in the vector.
    def get_index_of_literal(self, literal_number):
        return self.index_literals_and_var[literal_number]

    #Method to check if all the literals was asigned, if that happens the process end.
    def check_literals_assigned(self):
        return (self.count_assigned_literals == len(self.literals))

    def set_value_to_var(self, var_index, sign):
        #Add one to the count of the assigned variables
        self.count_assigned_literals += 1
        #Assign value based on the sign or the value recieved by argument
        self.variable[var_index] = 1 if sign > 0 else -1 
    
    def reduce_clause(self, clause):
        clause = [*set(clause)]
        
        while(True):           
            length = len(clause)
            found = False
            to_delete = -1
            for i in range(length):
                for j in range(length):
                    if(clause[i] == -clause[j] and i != j):                                            
                        found = True
                        to_delete = clause[i]   
                        break
                if(found): break            

            if(found):
                clause.remove(to_delete)
                clause.remove(-to_delete)
            else: break
        return clause

    def pick_literal_and_assign(self, decision_level):
        #Save the index of the max value
        max_value = -1
        max_value_index = -1

        #Get the max relevance literal
        for i in range(len(self.literals)):
            if(self.relevance_literal[i] > max_value and self.variable[i] == 0):
                max_value = self.relevance_literal[i]
                max_value_index = i
                break

        #Save the vars
        selected_lit = max_value_index 
        assign_value = self.literals_polarity[selected_lit]         
        
        self.set_value_to_var(selected_lit, assign_value)

        #Set the decision level
        self.decision_level_for_literal[selected_lit] = decision_level

        #Set to -1 the clause because it is a decision variable 
        self.index_clause_of_deduce_literal[selected_lit] = -1
        
        return self.literals[selected_lit]
            
        # #Search for a literal which var was not assigned
        # for i in range(len(self.literals)):
        #     #If the value of the variable is equal than 0, means the var
        #     #doesn't have a value assigned
            
        #     if(self.variable[i] == 0):                
        #         selected_lit = i if not possible_deduce_decision else index_literal
        #         assign_value = self.literals_polarity[selected_lit] if not possible_deduce_decision else value_literal
                
        #         self.set_value_to_var(selected_lit, assign_value)
        #         self.decision_level_for_literal[selected_lit] = decision_level
        #         self.index_clause_of_deduce_literal[selected_lit] = -1

        #         #print("LITERAL DE DECISION: ", self.literals[selected_lit], ": ", self.variable[selected_lit])                
        #         return self.literals[selected_lit]

    def unit_propagation(self, decision_level):
        #Flag to check if is possible to deduce any value in the decision level
        #entered by argument.
        unit_literal_founded = True        

        while(unit_literal_founded == True):    
            unit_literal_founded = False
            
            for i in range(len(self.clauses)):
                #Count he falsified variables in the clause
                falsified_variables = 0
                #Count the unsetted variables in the clause (is useful to possible deduce other literal)
                unsetted_variables  = 0
                #Index of the last var which doesn't have a value assigned
                last_unset_var = -1

                #Flago to check if the clause is already satisfied
                satisfied_check = False

                for j in range(len(self.clauses[i])):
                    #get the index of the literal
                    literal_index = self.get_index_of_literal(abs(self.clauses[i][j]))                                   

                    #if the value asigned to the literal is positive and the literal is positive, is satisfied
                    #if the value is negative and the value is negative the clause is satisfied
                    #else is unsatisfied
                    value_of_var = self.variable[literal_index] * self.clauses[i][j]
                    
                    #If the value of the var is greater than 0 the clause is satisfied, thats mean
                    #we can go to the next clause = break
                    if(value_of_var > 0):   
                        satisfied_check = True        
                        break
                    
                    #If is 0, the literal don't have a value
                    if(value_of_var == 0):                        
                        unsetted_variables += 1
                        last_unset_var = literal_index                        
                        origin_literal_unsetted = self.clauses[i][j]

                    #If is negative the literal is falsified
                    if(value_of_var < 0):                            
                        falsified_variables += 1
                    
                    if(falsified_variables == len(self.clauses[i])):
                        #A conflict has founded because all the variables all falsified, return false because
                        #the propagation cause the error.                        
                        self.incident_clause = i
                        return False                        
                
                #if(satisfied_check): continue
                if(not satisfied_check):                     
                    #If the unsetted count is equal than 1, is possible to deduce a variable, but we don't need to 
                    #interrupt the deduncing run for each literal in each clause.
                    if(unsetted_variables == 1):                    
                        
                        #Deduce the last var on the clause                            
                        self.set_value_to_var(last_unset_var, origin_literal_unsetted)         
                        #Set the decision level where is deduced
                        self.decision_level_for_literal[last_unset_var] = decision_level     
                        #Save the clause which is going to deduce
                        self.index_clause_of_deduce_literal[last_unset_var] = i                     

                        #print("LITERAL DEDUCIDO: ", self.literals[last_unset_var], ": ", self.variable[last_unset_var], " IN ", i, self.clauses[i], " LD ", decision_level)                                          
                        #We are the deducing, that means a unit_literal exists
                        unit_literal_founded = True
                
        self.incident_clause = -1
        return True
   
    #This method apply the CDCL when a error is founded
    def solve_conflict_and_backtrack(self, clause_incident, conflict_decision_level):
        #print("ERROR CLAUSE => ", clause_incident, " LEVEL DECISION => ", conflict_decision_level, " LITERALS = ", self.clauses[clause_incident])

        #Repeat process while the new clause which is based on the two clauses which generate the conflict
        #only have one literal of the decision level of the error
        counter_literals_in_dl = 0

        #Make a copy of the clause which generate the conflict
        learnt_clause = self.clauses[clause_incident].copy()

        #Vars to save the index of the clause which is going to be appended
        index_of_clause_to_append = -1

        while(True):
            counter_literals_in_dl = 0

            #Run each literal in the learnt clause
            for i in range(len(learnt_clause)):
                #Get the index of the literal
                literal_index = self.get_index_of_literal(abs(learnt_clause[i]))
                
                #Check if the literal in the clause was deduced in the same level decision
                #than the conflict ld.
                if(self.decision_level_for_literal[literal_index] == conflict_decision_level):
                    #If is in the same level decision, plus one to the counter
                    counter_literals_in_dl += 1
                
                #If have a trail then save the index
                if(self.decision_level_for_literal[literal_index] == conflict_decision_level
                    and self.index_clause_of_deduce_literal[literal_index] != -1):

                    #Get the clause used to deduce the literal
                    index_of_clause_to_append = self.index_clause_of_deduce_literal[literal_index]                    

            #If the literals in the same level decision is equal to 1 end the process.    
            if(counter_literals_in_dl == 1): break

            #else append the literals to the conflict clause
            for i in range(len(self.clauses[index_of_clause_to_append])):
                learnt_clause.append(self.clauses[index_of_clause_to_append][i])

            #Reduce the clause:
            learnt_clause = self.reduce_clause(learnt_clause)
            
        #Backtrack and learn process:
        #var to save the new level decision
        minor_level_decision = conflict_decision_level
        
        #Set the new level decision
        for i in range(len(learnt_clause)):            
            lit_index = self.get_index_of_literal(abs(learnt_clause[i]))
            
            if(self.decision_level_for_literal[lit_index] < minor_level_decision and self.decision_level_for_literal[lit_index] != 0):                
                minor_level_decision = self.decision_level_for_literal[lit_index]
       
        #Backtrack settings values of the vars, index of clauses, and decision levels
        for i in range(len(self.literals)):
            if(self.decision_level_for_literal[i] > minor_level_decision):
                self.variable[i] = 0
                self.decision_level_for_literal[i] = 0
                self.index_clause_of_deduce_literal[i] = -1
                self.count_assigned_literals -= 1
        
        #Add the new clause in the start of the list of clauses
        self.clauses.insert(0, learnt_clause)

        #Update information to the heuristic decision of the literals
        for j in range(len(self.clauses[0])):
            literal_index = self.get_index_of_literal(abs(self.clauses[0][j]))

            #Increase the relevance of the literal by 0.1
            self.relevance_literal[literal_index] += 0.1

            #Updating the polarity of the literals
            if(self.clauses[0][j] > 0): self.literals_polarity[literal_index] += 1
            else: self.literals_polarity[literal_index] -= 1

        #Return the new level decision
        return minor_level_decision

    #Method to print the results
    def show_results(self):
        message_result = "The results are: "
        for i in range(len(self.literals)):
            message_result += str(self.literals[i] * self.variable[i]) + " "
            self.results.append(self.literals[i] * self.variable[i])
        print(message_result)

        print("The total clauses learned was ", len(self.clauses) - self.s_quantity_clauses)

    #Apply everything of the sat solver using CDCL
    def solve(self):
        decision_level = 0

        #If is possible to make a unit_propagation in dl = 0, 
        #means exists a clause with one literal and if this returns false
        #the formula doesn't have a solution
        if(self.unit_propagation(decision_level) == False):            
            return False
        
        #Check if all the literals was not assigned
        while(not self.check_literals_assigned()):            
            decision_level += 1
            self.pick_literal_and_assign(decision_level)
            
            #With the literal assigned, make the unit propagation to check if is possible
            #deduce other literal and assign a value
            if(self.unit_propagation(decision_level) == False):
                decision_level = self.solve_conflict_and_backtrack(self.incident_clause, decision_level)

                #If the decision level is equal to 0, then the Formula is UNSAT
                if(decision_level == 0):
                    return False
        
        #If we reach this point of the code, the formula is SAT
        return True

    results = []
    def execute_solver(self):        
        #Save the result of execute the solver
        result = self.solve()

        #If returns true then SAT else the formula is UNSAT, and late show the results
        print("SAT") if result else print("UNSAT")
        self.show_results()
        return self.results

test = solver()
#test.get_problem(input("Insert the path of the problem or formula: "))
test.get_problem("./pruebas/1.txt")
test.execute_solver()
