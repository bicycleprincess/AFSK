import textwrap, logging
from convertions import *

# http://codegolf.stackexchange.com/questions/94056/telegraphy-golf-decode-baudot-code

logging.basicConfig(level=logging.INFO)

SIGNS = {
	"FS": "00010",
	"LS": "00001",
	"SP": "00011",  # take fron ER
}

LETTERS = {
	"A": "10000",
	"B": "00110",
	"C": "10110",
	"D": "11110",
	"E": "01000",
	"F": "01110",
	"G": "01010",
	"H": "11010",
	"I": "01100",
	"J": "10010",
	"K": "10011",
	"L": "11011",
	"M": "01011",
	"N": "01111",
	"O": "11100",
	"P": "11111",
	"Q": "10111",
	"R": "00111",
	"S": "00101",
	"T": "10101",
	"U": "10100",
	"V": "11101",
	"W": "01101",
	"X": "01001",
	"Y": "00100",
	"Z": "11001"
}

FIGURES = {
	"0": "11110",
	"1": "10000",
	"2": "01000",
	"3": "00100",
	"4": "10100",
	"5": "11100",
	"6": "10010",
	"7": "01010",
	"8": "00110",
	"9": "10110",
	"-": "00111",
	"?": "01101",
	":": "11001",
	"(": "10011",
	")": "01011",
	".": "10001",
	",": "00101", # take from S
	"'": "11101",
	"=": "11011",
	"/": "11000",
	"+": "11111",
	"!": "11010" # take from H
}

def encodeBaudot(info):

	rst = []
	text = (info.upper()).split()

	LC = 0  # letter count
	FC = 0  # figure

	for word in text:
		s = []
		for letter in word:

			if letter in LETTERS:
				if LC > 0:
					s.append(LETTERS[letter])
				else:
					s.append(SIGNS['LS'])
					s.append(LETTERS[letter])
					LC += 1 
					FC = 0

			elif letter in FIGURES:
				if FC > 0:
					s.append(FIGURES[letter])
				else:
					s.append(SIGNS['FS'])
					s.append(FIGURES[letter])
					FC += 1
					LC = 0
	
		rst.extend(s)
		rst.append(SIGNS['SP'])

	return rst[:-1]


def decodeBaudot(s):
	#print 'baudot: ', s

	if s != None:
		WORDS = []

		flag_L = False
		flag_F = False

		data = textwrap.wrap(s, 5)

		for sign in data:

			if sign == SIGNS['LS']:
				#print 'letter'
				flag_L = True
				flag_F = False
			
			elif sign == SIGNS['FS']:
				flag_F = True
				flag_L = False
				#print 'figure'
				
			elif sign == SIGNS['SP']:
				#print 'space'
				WORDS.extend(' ')
			else:
				if flag_L:
					if sign in SIGNS.values():
						if sign == SIGNS['FS']:
							flag_L = False
							flag_F = True
						else:
							flag_F = False
							flag_L = True
					else:
						#flag_L = False
						for letter, code in LETTERS.iteritems():
							if code == sign:
								#print letter
								WORDS.extend(letter)

				elif flag_F:
					if sign in SIGNS.values():
						if sign == SIGNS['LS']:
							flag_F = False
							flag_L = True
						else:
							flag_F = True
							flag_L = False
					else:
						#flag_F = False
						for figure, code in FIGURES.iteritems():
							if code == sign:
								#print figure
								WORDS.extend(figure)

		#return list2string(WORDS)
		print list2string(WORDS)
# MEMO
# this decode version is associating with real time version
# TRY origindecodeBaudot
def _decodeBaudot(s):

	if s != None:
		WORDS = []
		flag_L = False
		flag_F = False
		length = len(s)
		n_FS = s.count(SIGNS['FS'])
		n_LS = s.count(SIGNS['LS'])
		#print n_LS
		if n_LS > n_FS :
	
			try:    
				begin = s.index(SIGNS['FS'])
				s = s[begin:length]
				data = tuple(textwrap.wrap(s, 5))
				for sign in data:
					if sign == SIGNS['LS']:
						flag_L = True
						flag_F = False
					elif sign == SIGNS['FS']:
						flag_F = True
						flag_L = False
					elif sign == SIGNS['SP']:
						WORDS.extend(' ')
					else:
						if flag_L:
							if sign in SIGNS.values():
								if sign == SIGNS['FS']:
									flag_L = False
									flag_F = True
								else:
									flag_F = False
									flag_L = True
							else:
								for letter, code in LETTERS.iteritems():
									if code == sign:
										WORDS.extend(letter)
						elif flag_F:
							if sign in SIGNS.values():
								if sign == SIGNS['LS']:
									flag_F = False
									lag_L = True
								else:
									flag_F = True
									flag_L = False
							else:
								for figure, code in FIGURES.iteritems():
									if code == sign:
										WORDS.extend(figure)
			except ValueError:
				logging.info('baudot -- error in first if')
				pass
	
		elif n_FS > n_LS:
	
			try:    
				begin = s.index(SIGNS['LS'])
				s = s[begin:length]
				data = tuple(textwrap.wrap(s, 5))
				#n = data.count(SIGNS['SP'])
				#if n == 1:
				for sign in data:
					if sign == SIGNS['LS']:
						flag_L = True
						flag_F = False
					elif sign == SIGNS['FS']:
						flag_F = True
						flag_L = False
					elif sign == SIGNS['SP']:
						WORDS.extend(' ')
					else:
						if flag_L:
							if sign in SIGNS.values():
								if sign == SIGNS['FS']:
									flag_L = False
									flag_F = True
								else:
									flag_F = False
									flag_L = True
							else:
								for letter, code in LETTERS.iteritems():
									if code == sign:
										WORDS.extend(letter)
	
						elif flag_F:
							if sign in SIGNS.values():
								if sign == SIGNS['LS']:
									flag_F = False
									lag_L = True
								else:
									flag_F = True
									flag_L = False
							else:
								for figure, code in FIGURES.iteritems():
									if code == sign:
										WORDS.extend(figure)
			except ValueError:
				logging.info('baudot -- error in elif')
				pass
	
		else:
			try:
				index_FS = s.index(SIGNS['FS'])
				index_LS = s.index(SIGNS['LS'])
		
				#print index_LS, index_FS
		
				if index_LS < index_FS:
		
					begin = s.index(SIGNS['LS'])
					s = s[begin:length]
					data = tuple(textwrap.wrap(s, 5))
					for sign in data:
						if sign == SIGNS['LS']:
							flag_L = True
							flag_F = False
						elif sign == SIGNS['FS']:
							flag_F = True
							flag_L = False
						elif sign == SIGNS['SP']:
							WORDS.extend(' ')
						else:
							if flag_L:
								if sign in SIGNS.values():
									if sign == SIGNS['FS']:
										flag_L = False
										flag_F = True
									else:
										flag_F = False
										flag_L = True
								else:
									for letter, code in LETTERS.iteritems():
										if code == sign:
											WORDS.extend(letter)
		
							elif flag_F:
								if sign in SIGNS.values():
									if sign == SIGNS['LS']:
										flag_F = False
										lag_L = True
									else:
										flag_F = True
										flag_L = False
								else:
									for figure, code in FIGURES.iteritems():
										if code == sign:
											WORDS.extend(figure)
		
				else:
					begin = s.index(SIGNS['FS'])
					s = s[begin:length]
					data = tuple(textwrap.wrap(s, 5))
					for sign in data:
						if sign == SIGNS['LS']:
							flag_L = True
							flag_F = False
						elif sign == SIGNS['FS']:
							flag_F = True
							flag_L = False
						elif sign == SIGNS['SP']:
							WORDS.extend(' ')
						else:
							if flag_L:
								if sign in SIGNS.values():
									if sign == SIGNS['FS']:
										flag_L = False
										flag_F = True
									else:
										flag_F = False
										flag_L = True
								else:
									for letter, code in LETTERS.iteritems():
										if code == sign:
											WORDS.extend(letter)
		
							elif flag_F:
								if sign in SIGNS.values():
									if sign == SIGNS['LS']:
										flag_F = False
										lag_L = True
									else:
										flag_F = True
										flag_L = False
								else:
									for figure, code in FIGURES.iteritems():
										if code == sign:
											WORDS.extend(figure)
			except ValueError:
				logging.info('baudot -- error in else')
		
		geo = []
		gym = (".", "+", "-", ' ')
	
		for i in WORDS:
			if i.isdigit():
				geo.extend(i)
			elif i in gym:
				geo.extend(i)
		
		print list2string(geo)
	#else:
	#	print 'nothing in baudot'
	#	return None

def main():
	#text = str(raw_input('input the info:'))
	#text = 'x=1.23 y=4.56'
	#text = 'B(x=493.60, y=352.8)E'
	text = 'x=1234567890'
	info = list2string(encodeBaudot(text))
	print info
	decodeBaudot(info)
	print originaldecodeBaudot(info)    


if __name__ == '__main__':
	#main()
	pass