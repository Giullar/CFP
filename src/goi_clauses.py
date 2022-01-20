class GOIClause(object):
	def __init__(self):
		pass

class GOIQImplication(GOIClause):
	def __init__(self, from_index, to_index):
		self.from_index = from_index
		self.to_index = to_index

	def __str__(self):
		return "q("+str(self.to_index)+"):-q("+str(self.from_index)+")."


class GOIAnsImplication(GOIClause):
	def __init__(self, from_index, to_index):
		self.from_index = from_index
		self.to_index = to_index

	def __str__(self):
		return "ans(B,"+str(self.to_index)+"):-ans(B,"+str(self.from_index)+")."


#Clausola GOI del tipo "associa un valore ad un tipo" o anche "una question per il tipo index restituisce una risposta value"
class GOIQAssoc(GOIClause):
	def __init__(self, index, value):
		self.index = index
		self.value = value

	def __str__(self):
		return "ans("+self.value+","+str(self.index)+"):-q("+str(self.index)+")."


class GOIQAssocProb(GOIClause):
	def __init__(self, type_index, prob_atom_id): #Indice del tipo che assumerà valore tt se l'atomo probabilistico con l'id passato risulterà vero
		self.type_index = type_index
		self.prob_atom_id = prob_atom_id

	def __str__(self):
		return "ans(tt,"+str(self.type_index)+"):-q("+str(self.type_index)+"), probatom("+str(self.prob_atom_id)+").\n" + "ans(ff,"+str(self.type_index)+"):-q("+str(self.type_index)+"), \+probatom("+str(self.prob_atom_id)+")."


class GOIProbAtomDefinition(GOIClause):
	def __init__(self, prob_atom_id, probability=0.5): #Di default assumiamo una probabilità del 50% che l'atomo si verifichi.
		self.prob_atom_id = prob_atom_id
		self.probability = probability

	def __str__(self):
		return str(self.probability)+"::probatom("+str(self.prob_atom_id)+")."



#Collegamento di tipo answer necessario per la risposta del not.
class GOIAnsNot(GOIClause):
	def __init__(self, from_index, to_index):
		self.from_index = from_index
		self.to_index = to_index

	def __str__(self):
		return "ans(X,"+str(self.to_index)+"):-ans(B,"+str(self.from_index)+"), not(B,X)."


class GOIAnsAnd(GOIClause):
	def __init__(self, first_input, second_input, output):
		self.first_input = first_input
		self.second_input = second_input
		self.output = output

	def __str__(self):
		return "ans(X,"+str(self.output)+"):-ans(A,"+str(self.first_input)+"), ans(B,"+str(self.second_input)+"), and(A,B,X)."


class GOIAnsOr(GOIClause):
	def __init__(self, first_input, second_input, output):
		self.first_input = first_input
		self.second_input = second_input
		self.output = output

	def __str__(self):
		return "ans(X,"+str(self.output)+"):-ans(A,"+str(self.first_input)+"), ans(B,"+str(self.second_input)+"), or(A,B,X)."


#Clausole che definiscono gli operatori logici di base:

class GOINOTDefinition(GOIClause):
	def __init__(self):
		pass

	def __str__(self):
		return "not(tt, ff).\nnot(ff, tt)."


class GOIANDDefinition(GOIClause):
	def __init__(self):
		pass

	def __str__(self):
		return "and(tt, tt, tt).\nand(tt, ff, ff).\nand(ff, tt, ff).\nand(ff, ff, ff)."


class GOIORDefinition(GOIClause):
	def __init__(self):
		pass

	def __str__(self):
		return "or(tt, tt, tt).\nor(tt, ff, tt).\nor(ff, tt, tt).\nor(ff, ff, ff)."


#Clausole extra:

class GOIInitialQuestion(GOIClause):
	def __init__(self):
		pass

	def __str__(self):
		return "q(1)."


class GOIInitialQuery(GOIClause):
	def __init__(self):
		pass

	def __str__(self):
		return "query(ans(B,1))."