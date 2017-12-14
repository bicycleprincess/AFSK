import binascii, operator
import numpy as np

def string2binary(words):

	text_array = bin(int(binascii.hexlify(words), 16))
	return text_array[2:]

def binary2string(string):

	bits = int(string, 2)
	text = binascii.unhexlify('%x' % bits)
	return text

def binary2array(string):
	
	return np.array(map(int, string))

def list2string(data):

	return ''.join(map(str, data))

def ndarray2list(ary):

	x, y = np.shape(ary)

	return np.reshape(ary, (1,x*y)).tolist()