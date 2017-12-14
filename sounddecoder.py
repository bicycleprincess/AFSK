import binascii
import numpy as np
import scipy.signal as signal
import math
import scipy.signal.signaltools as sigtool
from convertions import *

MAX_FREQUENCY = 10000
SAMPLE_RATE = 50
INT_THRESHOLD = 50
LOW_THRESHOLD = 3.
HIGH_THRESHOLD = 280
RATE = 44100

LOW_PASS = 1000.
HIGH_PASS = 3000.
LOW_CUT = 900.
HIGH_CUT = 3100.

def normalize(data):
	"""Set in -1 and +1 range
	"""

	#return [float(x) / pow(2, 15) for x in data]

	l = [float(x) / pow(2, 15) for x in data]
	return np.asarray(l)

def denormalize(data):
	"""	The wave form remains,
	but the absolute amplitude changes.

	#http://stackoverflow.com/questions/10357992/how-to-generate-audio-from-a-numpy-array

	"""
	return np.int16(data/np.max(np.abs(data)) * 32767)


def windowing(numtaps, cutoff):

	return signal.firwin(numtaps, cutoff, width=None, window='hanning', pass_zero=True, scale=True, nyq=MAX_FREQUENCY/2)


def lowPassFilter(window_type, ary, data):

	return signal.lfilter(window_type, ary, data)


def butterBandFilter(snddata):

	r""" Band filters
	https://docs.scipy.org/doc/scipy/reference/generated/scipy.signal.buttord.html
	https://scipy.github.io/old-wiki/pages/Cookbook/ButterworthBandpass
	boolean can be
	0		1
	0		0
	"""
	nyq = MAX_FREQUENCY / 2.

	ws = [LOW_CUT/nyq, HIGH_CUT/nyq]
	wp = [LOW_PASS/nyq, HIGH_PASS/nyq]

	gpass = 20*np.log10(1+2*math.pi*LOW_CUT/44100)#*10
	gstop = -20*np.log10(2*math.pi*HIGH_CUT/44100)

	n, wn = signal.buttord(wp, ws, gpass, gstop, analog=0)
	b, a = signal.butter(n, wn, 'bandpass', 0)

	sig = signal.lfilter(b, a, snddata)

	return sig

def butterworth(snddata, passband):

	passbands = ('low', 'high', 'band')
	nyq = 44100. / 2
	lowcut = LOW_PASS / nyq
	highcut = HIGH_PASS / nyq

	if passband == passbands[0]:
		#print passbands[0]
		b, a = signal.butter(3, highcut, btype='lowpass')
		sig = signal.lfilter(b, a, snddata)
		return sig
	elif passband == passbands[1]:
		#print passbands[1]
		b, a = signal.butter(3, lowcut, btype='highpass')
		sig = signal.lfilter(b, a, snddata)
		return sig
	else:
		#print passbands[2]
		return butterBandFilter(snddata)


def savitzkyFilter(y, window_size, order, deriv=0, rate=1):

	try:
		window_size = np.abs(np.int(window_size))
		order = np.abs(np.int(order))
	except ValueError, msg:
		raise ValueError("window_size and order have to be of type int")

	if window_size % 2 != 1 or window_size < 1:
		raise TypeError("window_size size must be a positive odd number")

	if window_size < order + 2:
		raise TypeError("window_size is too small for the polynomials order")

	order_range = range(order+1)		
	half_window = (window_size -1) // 2

	b = np.mat([[k**i for i in order_range] for k in range(-half_window, half_window+1)])
	m = np.linalg.pinv(b).A[deriv] * rate ** deriv * math.factorial(deriv)

	firstvals = y[0] - np.abs(y[1:half_window+1][::-1] - y[0])
	lastvals = y[-1] + np.abs(y[-half_window-1:-1][::-1] - y[-1])

	y = np.concatenate((firstvals, y, lastvals))
	return np.convolve( m[::-1], y, mode='valid')


def detectEnvelope(snddata):

	return np.abs(sigtool.hilbert(snddata))

def differ(snddata):

	return np.diff(snddata, 1)
