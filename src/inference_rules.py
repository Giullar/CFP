#import lambda_types
from lambda_types import *


class Environment(object):
	def __init__(self, var_dict):
		self.var_dict = var_dict #dizionario nella forma nomevar:OggettoDiTipoType


class Term(object):
	def __init__(self, text):
		self.text = text

	def __str__(self):
		return self.text


class TermAbstraction(Term):
	def __init__(self, var_name, inner_term:Term):
		self.var_name = var_name
		self.inner_term = inner_term

	def __str__(self):
		return "lambda "+self.var_name+" . "+str(self.inner_term)


class TermProbAtom(Term):
	def __init__(self, prob_atom_id):
		self.prob_atom_id = prob_atom_id

	def __str__(self):
		return "ProbabilityAtom:"+str(self.prob_atom_id)


class Expression(object):
	'''Oggetto costituito da Environment+lambdaTermine+Type'''
	def __init__(self, env:Environment, term:Term, term_type:Type):
		self.env = env #dizionario nella forma nomevar:OggettoDiTipoType
		self.term = term
		self.term_type = term_type 

	def __str__(self):
		env_string = ""
		for key, value in self.env.var_dict.items():
			env_string += key +":"+ str(value) + ", "
		return "ENV: " + env_string + " TERM: " +str(self.term) + " TYPE: " + str(self.term_type)

###############

class InferenceRule(object):
	"""Classe nodo dell'albero"""
	def __init__(self, conclusion:Expression):
		self.conclusion = conclusion


class AbstractionRule(InferenceRule):
	def __init__(self, conclusion:Expression, premise_one:InferenceRule):
		super().__init__(conclusion)
		self.premise_one = premise_one


class ApplicationRule(InferenceRule):
	def __init__(self, conclusion:Expression, premise_one:InferenceRule, premise_two:InferenceRule):
		super().__init__(conclusion)
		self.premise_one = premise_one
		self.premise_two = premise_two


class TTRule(InferenceRule):
	def __init__(self, conclusion:Expression):
		super().__init__(conclusion)


class FFRule(InferenceRule):
	def __init__(self, conclusion:Expression):
		super().__init__(conclusion)


class VariableRule(InferenceRule):
	def __init__(self, conclusion:Expression):
		super().__init__(conclusion)


class NotRule(InferenceRule):
	def __init__(self, conclusion:Expression):
		super().__init__(conclusion)


class AndRule(InferenceRule):
	def __init__(self, conclusion:Expression):
		super().__init__(conclusion)


class OrRule(InferenceRule):
	def __init__(self, conclusion:Expression):
		super().__init__(conclusion)


class ProbAtomRule(InferenceRule): #Probabilistic Atom Rule
	def __init__(self, conclusion:Expression):
		super().__init__(conclusion)