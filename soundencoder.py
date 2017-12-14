import numpy as np
from convertions import *

from baudot import *

SAMPLE_RATE = 50      
AMPL = 1
N_AMPL = 0.1
CARRIER_FREQUENCY = 2000
MAX_FREQUENCY = 10000 
DEV_FREQUENCY = 1000

def encodeSound(data):

	nbits= len(data)

	t = np.arange(0, float(nbits)/float(SAMPLE_RATE), 1/float(MAX_FREQUENCY), dtype=np.float)
	m = np.zeros(0).astype(float)

	for bit in data:
		if bit == 0:
			m = np.hstack((m, np.multiply(np.ones(MAX_FREQUENCY/SAMPLE_RATE), CARRIER_FREQUENCY+DEV_FREQUENCY)))
		else:
			m = np.hstack((m, np.multiply(np.ones(MAX_FREQUENCY/SAMPLE_RATE), CARRIER_FREQUENCY-DEV_FREQUENCY)))

	sig = AMPL * np.cos(2 * np.pi * np.multiply(m, t)) 
	#noise = (np.random.randn(len(sig)) + 1) * N_AMPL
	
	#snr = 10 * np.log10(np.mean(np.square(data)) / np.mean(np.square(noise)))

	#sig = np.add(sig, noise)
	#sig = _sig.astype(np.int16)
	return sig

# this test is for for_all_birthday.py
#if __name__ == '__main__':
	
#	from soundfilehandler import *
#
#	#text = '192.168.2.1 is my mao address'
#	#text = 'B(x=1.234, y=4.321)E'
#
#	info = list2string(encodeBaudot(text))
#
#	ary = binary2array(info)
#	sig= encodeSound(ary)
#	
#	print len(sig)
#
#	#saveWav('hello.wav', 11025, sig)

#"""
### 	Test 	###
#if __name__ == '__main__':

#	text = '192.168.2.166 is my local git server'
	#text = 'hello'
	#length = len(string2binary(text))
	#print length
	#star = '*'
	#info = string2binary(star+text+star)
	#info = string2binary(text)

	#print info

#	data = binary2array(info)
	#print data
#	
#	sig = encodeSound(data) 	#float64

	# when converting to int16 then the signal is gone!!! WHY!!!
	#print sig.dtype, type(sig)
	#sig = sig.astype(np.int16)
	#print sig.dtype		#int16
	#print sig

	#playSound(sig)
	#import sounddevice as sd
	#sd.play(sig, 11025, blocking=True)
	#saveWav('hello_star_sample_test.wav', 11025, sig)
#
	#from sounddecode import decode
	#from readwav import *
	#from convertions import *

	#info = scipyRead('low.wav')
#	
	#data = decode(info)
	#bits = list2string(data)
	#print bits 
	#print binary2string(bits)
#"""