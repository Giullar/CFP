class Type(object):
	def __init__(self):
		pass

	def __str__(self):
		pass

class Arrow(Type):
	def __init__(self, left:Type, right:Type):
		self.left = left
		self.right = right

	def __str__(self):
		return str(self.left) + "->" + str(self.right)

class SimpleType(Type):
	def __init__(self):
		self.index = None

class Bool(SimpleType):
	def __init__(self):
		super().__init__()

	def __str__(self):
		return "Bool:"+str(self.index)