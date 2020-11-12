import plex
class RunError(Exception):
	pass
class ParseError(Exception):
	pass

class MyParser:
	
	def __init__(self):
		letter = plex.Range('azAZ')
		digit = plex.Range('09')
		name = letter + plex.Rep(letter|digit)
		space = plex.Any(' \n\t')

		Keyword = plex.Str('print','PRINT')
		floatnum= plex.Rep(digit) +plex.Str('.') + plex.Rep1(digit)

		#gia na anagnorizi hex
		atof=plex.Range('afAF')
		equals = plex.Str( '=')
		addop = plex.Str('+','-')
		multop = plex.Str('*','/')
		parethensys1 = plex.Str('(')
		parethensys2 = plex.Str(')')
		self.st = {}

		self.lexicon = plex.Lexicon([   
			(Keyword, 'PRINT_TOKEN'),
			(name, 'ID_TOKEN'),             #name = letter + plex.Rep(letter|digit)
			(floatnum, 'FLOAT_TOKEN'),
			(equals, '='),
			(addop, plex.TEXT),
			(multop, plex.TEXT),
			(parethensys1, '('),
			(parethensys2, ')'),
			(space, plex.IGNORE)			
		])
			
	def createScanner(self,fp):
		self.scanner = plex.Scanner(self.lexicon,fp)
		self.la , self.text = self.next_token()

	def next_token(self):
		return self.scanner.read()
	
	def match(self,token):
		if self.la == token:
			self.la, self.text=self.next_token()
		else:
			raise ParseError(" waiting for something to be received ")

	def parse(self,fp):
		self.createScanner(fp)
	#	while self.la:
#			print(self.la, self.text)
#			self.la, self.text = self.next_token()
		self.stmt_list()

	def stmt_list(self):
		if self.la == 'ID_TOKEN' or self.la == 'PRINT_TOKEN':
			self.stmt()
			print(self.stmt())
			self.stmt_list()
		elif self.la == None:
			return
		else:
			raise ParseError("Expected id or print")
	def stmt(self):
		if self.la == 'ID_TOKEN':
			varname = self.text
			self.match('ID_TOKEN')
			self.match('=')
			e = self.expr()
			self.st[varname] = e
			return {'type': '=', 'text': 'ID_TOKEN', 'expr': 'e'}
		elif self.la == 'PRINT_TOKEN':
			self.match('PRINT_TOKEN')
			print(self.expr())
			return {'type': 'PRINT_TOKEN', 'expr': 'e'}
		else:
			raise ParseError("Expected id or print")
	def expr(self):
		if self.la == '(' or self.la == 'ID_TOKEN' or self.la == 'FLOAT_TOKEN':
			t = self.term()
			while self.la =='+' or self.la == '-': #oso to self einai addop
				op = self.addop()
				t2 = self.term()
				f = { 'op': op, 'left': f, 'right': f2}
				if op == '+':
					t += t2
				else:
					t-= t2
			if self.la == 'ID_TOKEN' or self.la == 'PRINT_TOKEN' or self.la == None or self.la == ')':
				return t
			else:
				raise ParseError("Expected - or +")
		else:
			raise ParseError("Expected ( or id or float")
			
	def term_tail(self):
		if self.la == '+' or self.la == '-':		
			op = self.addop()
			t = self.term()
			tt = self.term_tail()
			if tt is None:
				return op,t
			if tt[0] == '+':
				return op, t + tt[1]
			else:
				return op, t - tt[1]
		elif self.la == 'ID_TOKEN' or self.la == 'PRINT_TOKEN' or self.la == None or self.la == ')':
			return
		else:
			raise ParseError("Expected - or +") 
		
	def term(self):
		if self.la == '(' or self.la == 'ID_TOKEN' or self.la == 'FLOAT_TOKEN':		
			f = self.factor()
			'''ft = self.factor_tail()'''
			while self.la == '*' or self.la == '/':
				op = self.multop()
				f2 = self.factor()
				if op == '*':
					f = f * f2
				else:
					f = f / f2
			if self.la == '+' or self.la == '-' or self.la == 'ID_TOKEN' or self.la == 'PRINT_TOKEN' or self.la == None or self.la == ')':
				return f
			else:
				raise ParseError("Expected ")
		else:
			raise ParseError("Expected * or /") 

	def factor_tail(self):
		if self.la == '*' or self.la == '/':
			op = self.multop()
			f = self.factsor()
			t = self.factor_tail()
			if t is None:
				return op,f
			if t[0] == '*':
				return op, f * t[1]
			else:
				return op, f / t[1]
		elif self.la == '+' or self.la == '-' or self.la == 'ID_TOKEN' or self.la == 'PRINT_TOKEN' or self.la == None or self.la == ')':
			return
		else:
			raise ParseError("Expected * or /") 

	def factor(self):
		if self.la == '(':
			self.match('(')
			e = self.expr()
			self.match(')')
			return(e)
		elif self.la == 'ID_TOKEN':
			varname = self.text
			self.match('ID_TOKEN')
			return {'type': 'ID', 'text': varname} 
			#if varname in self.st:
				#return self.st[varname]
			raise RunError("no value")
		elif self.la == 'FLOAT_TOKEN':
			value = float(self.text)
			self.match('FLOAT_TOKEN')
			return  {'type': 'NUMBER','value': value} 
		elif value == None:
			raise RunError("Expected something and got something else")
		else:
			raise ParseError("Expecting ( or id or a float.")
		
	def addop(self):
		if self.la == '+':
			self.match('+')
			return('+')
		elif self.la == '-':
			self.match('-')
			return('-')
		else:
			raise ParseError("Expected - or +")		
		
	def multop(self):
		if self.la == '*':
			self.match('*')
			return('*')
		elif self.la == '/':
			self.match('/')
			return('/')
		else:
			raise ParseError("Expected * or /")		
			
parser = MyParser()

with open('serious_grammar.txt', 'r') as fp:
	parser.parse(fp)