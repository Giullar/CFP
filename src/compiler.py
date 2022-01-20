#Compilatore dal linguaggio funzionale probabilistico al linguaggio Problog.
#Autore: Giulio Vaccari



from inference_rules import *
from goi_clauses import *


#DEBUG
def traverse(inf_rule:InferenceRule):
	print(str(inf_rule.conclusion))
	if isinstance(inf_rule, ApplicationRule):
		traverse(inf_rule.premise_one)
		traverse(inf_rule.premise_two)
	elif isinstance(inf_rule, AbstractionRule):
		traverse(inf_rule.premise_one)


#Enumera i tipi contenuti in un albero di regole di inferenza, la cui radice è inf_rule
#Input: Regola + numero da cui partire per enumerare
#Restituisce: il prossimo numero utile per continuare la numerazione
def enumerate_rule(inf_rule:InferenceRule, index):

	#Enumero il tipo della conclusione della mia regola
	index = enumerate_type(inf_rule.conclusion.term_type, index)
	#Enumero i tipi delle variabili contenute nell'environment della conclusione
	for key, value in inf_rule.conclusion.env.var_dict.items():
		index = enumerate_type(value, index)

	#Rircorsivamente mi richiamo sui sottoalberi (sottoregole), se sono presenti.
	if isinstance(inf_rule, ApplicationRule):
		#enumero il sottoalbero sinistro, poi prendo l'indice che mi dice fin dove è arrivato ad assegnare i numeri, e lo passo come inizo della numerazione per il sottoalbero destro.
		index = enumerate_rule(inf_rule.premise_one, index)
		index = enumerate_rule(inf_rule.premise_two, index)
	elif isinstance(inf_rule, AbstractionRule):
		index = enumerate_rule(inf_rule.premise_one, index)

	return index


#Enumera un tipo
#Nota:Il tipo stesso è visto come un albero (binario).
#Input: tipo + numero da cui partire per enumerare
#Restituisce: il prossimo numero utile per continuare la numerazione
def enumerate_type(term_type: Type, index):

	if isinstance(term_type, SimpleType):
		term_type.index = index
		index += 1
	elif isinstance(term_type, Arrow):
		#enumero il sottoalbero destro, poi prendo l'indice che mi dice fin dove è arrivato ad assegnare i numeri, e lo passo come inizo della numerazione per il sottoalbero sinistro.
		index = enumerate_type(term_type.right, index)
		index = enumerate_type(term_type.left, index)

	return index


#Aggiunge alcune clausole extra da integrare alle clausole che saranno generate dal processo di compilazione GOI
def generate_extra_clauses(goi_clauses):

	goi_clauses.append(GOIInitialQuestion())
	goi_clauses.append(GOINOTDefinition())
	goi_clauses.append(GOIANDDefinition())
	goi_clauses.append(GOIORDefinition())
	goi_clauses.append(GOIInitialQuery())



def compile(inf_rule: InferenceRule):

	goi_clauses = [] #Lista che conterrà le clasole GOI generate dalla compilazione
	prob_atom_dict = {} #Dizionario che conterrà gli atomi probabilistici contenuti nell'albero in input

	#Enumera i tipi dell'albero in input
	enumerate_rule(inf_rule, 1)

	#Genera le clasole extra che risulteranno dalla traduzione. Ad esempio le definizioni in problog degli operatori logici not, and, or.
	generate_extra_clauses(goi_clauses)
	#Genera le definizioni problog degli atomi probabilistici
	get_prob_atom_dict(inf_rule, prob_atom_dict)
	generate_prob_atom_definitions(prob_atom_dict, goi_clauses)

	#Genera le clausole GOI che rappresentano la traduzione in linguaggio problog dell'albero in input
	generate_clauses(inf_rule, goi_clauses)

	return goi_clauses


#Input:La radice dell'albero di regole di cui si vogliono generare le clusole goi (di cui si vuole fare la traduzione) + un insieme di clausole goi.
#Output:Insieme contenente le clasuole goi passate come parametro più le nuove clausole goi generate dalla traduzione appena effettuata.
def generate_clauses(inf_rule: InferenceRule, goi_clauses):

	#Pattern matchin sulla forma della regola di inferenza
	if isinstance(inf_rule, TTRule): #tt
		goi_clauses.append(GOIQAssoc(inf_rule.conclusion.term_type.index, "tt"))
	elif isinstance(inf_rule, FFRule): #ff
		goi_clauses.append(GOIQAssoc(inf_rule.conclusion.term_type.index, "ff"))
	elif isinstance(inf_rule, VariableRule): #Variable
		link_types(inf_rule.conclusion.term_type, inf_rule.conclusion.env.var_dict[str(inf_rule.conclusion.term)], goi_clauses)
	elif isinstance(inf_rule, NotRule): #Not
		goi_clauses.append(GOIQImplication(inf_rule.conclusion.term_type.right.index, inf_rule.conclusion.term_type.left.index))
		goi_clauses.append(GOIAnsNot(inf_rule.conclusion.term_type.left.index, inf_rule.conclusion.term_type.right.index))
	elif isinstance(inf_rule, AndRule): #And
		indexes_list = []
		get_list_of_index_from_type(inf_rule.conclusion.term_type, indexes_list)
		goi_clauses.append(GOIQImplication(indexes_list[0], indexes_list[1]))
		goi_clauses.append(GOIQImplication(indexes_list[0], indexes_list[2]))
		goi_clauses.append(GOIAnsAnd(indexes_list[1], indexes_list[2], indexes_list[0]))
	elif isinstance(inf_rule, OrRule): #Or
		indexes_list = []
		get_list_of_index_from_type(inf_rule.conclusion.term_type, indexes_list)
		goi_clauses.append(GOIQImplication(indexes_list[0], indexes_list[1]))
		goi_clauses.append(GOIQImplication(indexes_list[0], indexes_list[2]))
		goi_clauses.append(GOIAnsOr(indexes_list[1], indexes_list[2], indexes_list[0]))
	elif isinstance(inf_rule, ProbAtomRule): #ProbAtom
		goi_clauses.append(GOIQAssocProb(inf_rule.conclusion.term_type.index, inf_rule.conclusion.term.prob_atom_id))
	elif isinstance(inf_rule, ApplicationRule): #Application
		link_types(inf_rule.conclusion.term_type, inf_rule.premise_one.conclusion.term_type.right, goi_clauses)
		link_types(inf_rule.premise_one.conclusion.term_type.left, inf_rule.premise_two.conclusion.term_type, goi_clauses)
		#Genero i collegamenti fra gli environment:
		generate_environment_clauses(inf_rule.premise_one.conclusion.env, inf_rule.conclusion.env, goi_clauses)
		generate_environment_clauses(inf_rule.premise_two.conclusion.env, inf_rule.conclusion.env, goi_clauses)
		#Chiamate induttive
		generate_clauses(inf_rule.premise_one, goi_clauses)
		generate_clauses(inf_rule.premise_two, goi_clauses)
	elif isinstance(inf_rule, AbstractionRule): #Abstraction
		var_name = inf_rule.conclusion.term.var_name
		link_types(inf_rule.premise_one.conclusion.env.var_dict[var_name], inf_rule.conclusion.term_type.left, goi_clauses)
		link_types(inf_rule.conclusion.term_type.right, inf_rule.premise_one.conclusion.term_type, goi_clauses)
		#Genero i collegamenti fra gli environment:
		generate_environment_clauses(inf_rule.premise_one.conclusion.env, inf_rule.conclusion.env, goi_clauses)
		#Chiamata induttiva
		generate_clauses(inf_rule.premise_one, goi_clauses)


#Effettua il copycat tra 2 tipi aventi la stessa struttura, creando i relativi collegamenti goi ed aggiungendoli alla lista di clausole goi passata come terzo parametro.
def link_types(first_type:Type, second_type:Type, goi_clauses):
	link_types_internal(first_type, second_type, goi_clauses, True)

#Assegna le polarità effettuando una semplice visita in-ordine dell'albero binario dei tipi: ogni volta che incontra una nuova foglia gli assegna una polarità (crea il collegamento goi)
#Nota: la visita è effettuata visitando le foglie da destra verso sinistra.
#La regola per assegnare la polarità è: 
#caso base: la polarità è quella passata come parametro.
#caso freccia: la polarità della parte destra è quella passata come parametro, la polarità della parte sinistra è quella passata come parametro negata.
def link_types_internal(first_type:Type, second_type:Type, goi_clauses, polarity):

	if isinstance(first_type, Arrow): #Caso freccia (implicazione)
		link_types_internal(first_type.right, second_type.right, goi_clauses, polarity)
		link_types_internal(first_type.left, second_type.left, goi_clauses, (not polarity))

	if isinstance(first_type, SimpleType): #Caso base
		if(polarity):
			goi_clauses.append(GOIQImplication(first_type.index, second_type.index))
			goi_clauses.append(GOIAnsImplication(second_type.index, first_type.index))
		else:
			goi_clauses.append(GOIQImplication(second_type.index, first_type.index))
			goi_clauses.append(GOIAnsImplication(first_type.index, second_type.index))


#Genera i collegamenti GOI tra le variabili aventi lo stesso nome (in 2 environment) da un nodo all'altro dell'albero
def generate_environment_clauses(from_env, to_env, goi_clauses):
	for key, value in from_env.var_dict.items():
		if key in to_env.var_dict:
			link_types(from_env.var_dict[key], to_env.var_dict[key], goi_clauses)


#input: un tipo
#output: una lista contenente gli indici dei tipi semplici che compaiono nella struttura ad albero che è il tipo.
#L'algoritmo effettua una in-visita ed ogni volta che trova un tipo semplice (foglia), l'aggiunge alla lista.
#Esempio: 3->2->1 diventa [1,2,3].
def get_list_of_index_from_type(my_type, indexes_list):
	if isinstance(my_type, Arrow):
		get_list_of_index_from_type(my_type.right, indexes_list)
	if isinstance(my_type, SimpleType): #Caso base
		indexes_list.append(my_type.index)
	if isinstance(my_type, Arrow):
		get_list_of_index_from_type(my_type.left, indexes_list)


#Attraversa l'albero e crea un dizionario contenente tutte le associazioni nella forma: id_atomo_probabilistico_utilizzato : riferimento_al_termine_ProbAtomRule
def get_prob_atom_dict(inf_rule:InferenceRule, prob_atom_dict):
	if isinstance(inf_rule, ProbAtomRule):
		prob_atom_dict[inf_rule.conclusion.term.prob_atom_id] = inf_rule.conclusion.term
	elif isinstance(inf_rule, ApplicationRule):
		get_prob_atom_dict(inf_rule.premise_one, prob_atom_dict)
		get_prob_atom_dict(inf_rule.premise_two, prob_atom_dict)
	elif isinstance(inf_rule, AbstractionRule):
		get_prob_atom_dict(inf_rule.premise_one, prob_atom_dict)


#Genera le definizioni problog degli atomi probabilistici contenuti nel dizionario prob_atom_dict
def generate_prob_atom_definitions(prob_atom_dict, goi_clauses):
	for key, value in prob_atom_dict.items():
		goi_clauses.append(GOIProbAtomDefinition(key))


#########################

#è possibile costruire alberi da dare in input al compilatore solo definendoli tramite codice all'interno di questo stesso programma.

#Test Uno:

A = TTRule(Expression(Environment({}), Term("tt"), Bool()))

B = AndRule(Expression(Environment({}), Term("and"), Arrow(Bool(), Arrow(Bool(), Bool()))))

C = ApplicationRule(Expression(Environment({}), Term("and tt"), Arrow(Bool(), Bool())), B, A)

E = TTRule(Expression(Environment({}), Term("tt"), Bool()))

D = ApplicationRule(Expression(Environment({}), Term("(and tt) tt"), Bool()), C, E)

#D è il nostro albero


#problog_program = compile(D)


#Test Due:

A = NotRule(Expression(Environment({}), Term("not"), Arrow(Bool(), Bool())))

B = VariableRule(Expression(Environment({"x":Bool()}), Term("x"), Bool()))

C = ApplicationRule(Expression(Environment({"x":Bool()}), Term("not x"), Bool()), A, B)

D = AbstractionRule(Expression(Environment({}), TermAbstraction("x", Term("not x")), Arrow(Bool(), Bool())), C)

E = TTRule(Expression(Environment({}), Term("tt"), Bool()))

F = ApplicationRule(Expression(Environment({}), Term("(lambda x . not x) tt"), Bool()), D, E)

#problog_program = compile(F)

#Test Tre: (Variante del test 1)

A = ProbAtomRule(Expression(Environment({}), TermProbAtom(1), Bool()))

B = AndRule(Expression(Environment({}), Term("and"), Arrow(Bool(), Arrow(Bool(), Bool()))))

C = ApplicationRule(Expression(Environment({}), Term("and tt"), Arrow(Bool(), Bool())), B, A)
#C = ApplicationRule(Expression(Environment({}), Term("and "+str(TermProbAtom(1))), Arrow(Bool(), Bool())), B, A)

E = TTRule(Expression(Environment({}), Term("tt"), Bool()))

D = ApplicationRule(Expression(Environment({}), Term("(and tt) tt"), Bool()), C, E)
#D = ApplicationRule(Expression(Environment({}), Term("(and "+str(TermProbAtom(1))+") tt"), Bool()), C, E)

#problog_program = compile(D)

#Test 4: semplice var rule
A = VariableRule(Expression(Environment({"x":Arrow(Bool(), Bool())}), Term("x"), Arrow(Bool(), Bool())))

#problog_program = compile(A)
#traverse(A)

#Test 5:

A = VariableRule(Expression(Environment({"x":Bool()}), Term("x"), Bool()))

B = NotRule(Expression(Environment({}), Term("not"), Arrow(Bool(), Bool())))

C = NotRule(Expression(Environment({}), Term("not"), Arrow(Bool(), Bool())))

D = ApplicationRule(Expression(Environment({"x":Bool()}), Term("not x"), Bool()), B, A)

E = ApplicationRule(Expression(Environment({"x":Bool()}), Term("not not x"), Bool()), C, D)

F = AbstractionRule(Expression(Environment({}), TermAbstraction("x", Term("not not x")), Arrow(Bool(), Bool())), E)

G = TTRule(Expression(Environment({}), Term("tt"), Bool()))

H = ApplicationRule(Expression(Environment({}), Term("(lambda x . not not x) tt"), Bool()), F, G)

#problog_program = compile(H)
#traverse(H)


#Test 6:

A = TTRule(Expression(Environment({}), Term("tt"), Bool()))

B = VariableRule(Expression(Environment({"x":Arrow(Bool(), Arrow(Bool(), Bool()))}), Term("x"), Arrow(Bool(), Arrow(Bool(), Bool()))))

C = ApplicationRule(Expression(Environment({"x":Arrow(Bool(), Arrow(Bool(), Bool()))}), Term("x tt"), Arrow(Bool(), Bool())), B, A)

D = FFRule(Expression(Environment({}), Term("ff"), Bool()))

E = ApplicationRule(Expression(Environment({"x":Arrow(Bool(), Arrow(Bool(), Bool()))}), Term("(x tt) ff"), Bool()), C, D)

F = AbstractionRule(Expression(Environment({}), TermAbstraction("x", Term("(x tt) ff")), Arrow(Arrow(Bool(), Arrow(Bool(), Bool())), Bool())), E)

G = AndRule(Expression(Environment({}), Term("and"), Arrow(Bool(), Arrow(Bool(), Bool()))))

H = ApplicationRule(Expression(Environment({}), Term("(lambda x .(x tt) ff) (and)"), Bool()), F, G)

#problog_program = compile(H)
#traverse(H)

#Test 7: (Variante del test 1)

A = ProbAtomRule(Expression(Environment({}), TermProbAtom(1), Bool()))

B = AndRule(Expression(Environment({}), Term("and"), Arrow(Bool(), Arrow(Bool(), Bool()))))

C = ApplicationRule(Expression(Environment({}), Term("and tt"), Arrow(Bool(), Bool())), B, A)
#C = ApplicationRule(Expression(Environment({}), Term("and "+str(TermProbAtom(1))), Arrow(Bool(), Bool())), B, A)

E = ProbAtomRule(Expression(Environment({}), TermProbAtom(2), Bool()))

D = ApplicationRule(Expression(Environment({}), Term("(and tt) tt"), Bool()), C, E)
#D = ApplicationRule(Expression(Environment({}), Term("(and "+str(TermProbAtom(1))+") "+str(TermProbAtom(1))), Bool()), C, E)

problog_program = compile(D)


#DEBUG
for clause in problog_program:
	print(str(clause))




#Salva su file l'output della compilazione
with open("output.pl", "w") as output_file:
	#Write the core program clauses
	for clause in problog_program:
		output_file.write(str(clause)+"\n")
