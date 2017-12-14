from soundfilehandler import saveWav

import alsaaudio
import time, threading, Queue
import numpy as np
from sounddecoder import *
from convertions import list2string
from hamming import Hammingcorrector, Hammingdecoder
from baudot import decodeBaudot

import logging

logging.basicConfig(level=logging.INFO)

MAX_FREQUENCY = 10000
SAMPLE_RATE = 50
MAX_DURATION = 3.5
RATE = 44100
SND = Queue.Queue(maxsize=0)
BLOCKS = ''


class Recorder(object):

	def __init__(self):
		self.channels = 1
		self.rate = RATE
		self.low_threshold = 0.
		self.raw_data = SND
		self.blocks = BLOCKS
		self.size = 441
		self.pipeline = Queue.Queue(maxsize=0)
		self.hanning = windowing(100, 100)
		self.counter = 0
		self.event = threading.Event()

	def _setThreshold(self): 

		self.stream = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NORMAL, 'default')
		self.stream.setchannels(self.channels)
		self.stream.setformat(alsaaudio.PCM_FORMAT_S16_LE)
		self.stream.setrate(self.rate)
		self.stream.setperiodsize(self.size)


		for i in xrange(10):

			l, snddata = self.stream.read()
			try:
				self.low_threshold += self.getAmplitude(snddata)
			except TypeError:
				pass

		self.low_threshold = self.low_threshold/10

		logging.info(self.low_threshold)
		return self.low_threshold

	def getAmplitude(self, snddata):

		#l, snddata = self.stream.read()
		try:
			piece = np.fromstring(snddata, np.int16)
			#print len(piece)
			peak = np.max(piece)
			amplitude = peak / 32768.
			return amplitude
		except ValueError:
			pass


	def _getOnset(self, snddata):
		#l, snddata = self.stream.read()
		print len(snddata)
		if type(snddata) == 'str':
			piece = np.fromstring(snddata, np.int16)
			try:
				sp = np.fft.fft(piece)
				freqs = np.fft.fftfreq(len(sp))
				idx = np.argmax(np.abs(sp))
				peak = freqs[idx]
				freqency = int(abs(peak*RATE))
				if freqency >= 2000:
					snddata = snddata[:len(snddata)/2]
					return self.getOnset(snddata)
				#return len(snddata)
			except ValueError:
				pass
		else:
			try:
				sp = np.fft.fft(snddata)
				freqs = np.fft.fftfreq(len(sp))
				idx = np.argmax(np.abs(sp))
				peak = freqs[idx]
				freqency = int(abs(peak*RATE))

				if freqency >= 2000:
					snddata = snddata[:len(snddata)/2]
					return self.getOnset(snddata)
				
			except ValueError:
				pass

		return len(snddata)

	def _getFrequency(self, snddata):
		#l, snddata = self.stream.read()
		piece = np.fromstring(snddata, np.int16)
		try:
			
			sp = np.fft.fft(piece)
			freqs = np.fft.fftfreq(len(sp))
			idx = np.argmax(np.abs(sp))
			peak = freqs[idx]
			freqency = int(abs(peak*RATE))
			logging.info(freqency)
			return freqency
		except ValueError:
			pass

	def _openStream(self):

		self.stream = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NONBLOCK, 'default')
		self.stream.setchannels(self.channels)
		self.stream.setformat(alsaaudio.PCM_FORMAT_S16_LE)
		self.stream.setrate(self.rate)
		self.stream.setperiodsize(882)

		self.nothing = 0
		self.something = 0

		while 1:
			#time.sleep(.01)
			l, snddata = self.stream.read()
			#logging.info(self.getFrequency(snddata))
			
			if l:
				#logging.info(l)
				if self.getAmplitude(snddata) >= self.low_threshold * 1.3:
					#logging.info(self.getFrequency(snddata))
					self.something += 1
					self.nothing = 0
					self.raw_data.put(snddata)
					#logging.info('live long')

					if self.something >= 1000:
						self._setThreshold()
						self.something = 0
						self.nothing = 0

				elif self.getAmplitude(snddata) <= self.low_threshold * 0.7:
					self.nothing += 1
					self.something = 0

					if self.nothing >= 500:
						self._setThreshold()
						self.nothing = 0
						self.something = 0

	def openStream(self, event):

		self.stream = alsaaudio.PCM(alsaaudio.PCM_CAPTURE, alsaaudio.PCM_NONBLOCK, 'default')
		self.stream.setchannels(self.channels)
		self.stream.setformat(alsaaudio.PCM_FORMAT_S16_LE)
		self.stream.setrate(self.rate)
		self.stream.setperiodsize(882)

		self.nothing = 0
		self.something = 0

		# IS THIS RIGHT???
		while not event.isSet():
			logging.info('waitting')
			event.wait()

			while 1:
				time.sleep(.01)
				l, snddata = self.stream.read()
				#logging.info(self.getFrequency(snddata))
				#logging.info(f)
				if l:
					if self.getAmplitude(snddata) >= self.low_threshold * 1.3:
						#logging.info(self.getFrequency(snddata))
						self.something += 1
						self.nothing = 0
						self.raw_data.put(snddata)
						#logging.info('live long')
	
						if self.something >= 1000:
							self._setThreshold()
							self.something = 0
							self.nothing = 0
	
					elif self.getAmplitude(snddata) <= self.low_threshold * 0.7:
						self.nothing += 1
						self.something = 0
	
						if self.nothing >= 500:
							self._setThreshold()
							self.nothing = 0
							self.something = 0

	def run(self):

		self._setThreshold()
		#stream_thread = threading.Thread(target=self.openStream)
		stream_thread = threading.Thread(target=self.openStream, args=(self.event, ))
		#record_thread = threading.Thread(target=self.record)
		stream_thread.daemon = True
		#record_thread.daemon = True

		stream_thread.start()
		#record_thread.start()
		logging.info('threads begin')

		raw_input('Ready to begin! Hit the ENTER! ')
		self.event.set()
		self.record()
		#self.decode()
		#self.event.clear()
		
		#record_thread.join()
		stream_thread.join()

	def record(self):

		while 1:
			time.sleep(.01)
			if not self.raw_data.empty():
				
				block = self.raw_data.get()
				self.blocks += block
				#logging.info('and prosper')
				samples = np.fromstring(self.blocks, np.int16)
				if len(samples) >= self.rate * MAX_DURATION:
					#logging.info('get enough data')
					#logging.info(len(samples))
					self.blocks = ''
					#self.decode(samples)
					#self.event.clear()
					self.pipeline.put(samples)
					logging.info('put in pipe')
					self.decode()
			else:
				time.sleep(.01)

	def _record(self):
		while 1:
			time.sleep(.01)
			if not self.raw_data.empty():
				
				block = self.raw_data.get()
				self.blocks += block
				#logging.info('and prosper')
				samples = np.fromstring(self.blocks, np.int16)
				if len(samples) >= self.rate * MAX_DURATION:
					logging.info('get enough data')
					self._setThreshold()
					self.blocks = ''
					self.decode(samples)
					time.sleep(.01)
			else:
				time.sleep(.01)	


	#def decode(self, samples):
	def _decode(self):

		logging.info('begin decoding')
		l = []
		
		filtered = butterworth(samples, 'high')
		logging.info('filtering done')
		
		smoothed = savitzkyFilter(samples, 11, 6)
		logging.info('smoothing done')
		
		data_diff = differ(smoothed)
		logging.info('differing done')
		
		envelope = detectEnvelope(data_diff)
		logging.info('detecting done')
		
		hanning = windowing(100, 100)
		logging.info('hanning done')
		
		data_out = lowPassFilter(hanning, 1.0, envelope)
		logging.info('low pass done')

		mean = np.mean(data_out)
		sig = data_out[MAX_FREQUENCY/SAMPLE_RATE*2:len(data_out):MAX_FREQUENCY/SAMPLE_RATE*4]
		
		for bit in sig:
			l.append(0 if bit > mean else 1)

		bits = list2string(l)
		logging.info(bits)

		try:
			logging.info('Hamming process')
			corrected = Hammingcorrector(bits)
			de = Hammingdecoder(corrected)
			logging.info(de)
			return decodeBaudot(de)
		except IndexError:
			logging.info('Index Error')

	def _decode(self):
		while 1:
			if not self.pipeline.empty():

				#time.sleep(.01)

				logging.info('begin decoding')

				samples = self.pipeline.get()
				l = []
				
				filtered = butterworth(samples, 'high')
				logging.info('filtering done')
				
				smoothed = savitzkyFilter(samples, 11, 6)
				logging.info('smoothing done')
				
				data_diff = differ(smoothed)
				logging.info('differing done')
				
				#envelope = detectEnvelope(data_diff)
				#logging.info('detecting done')
				
				envelope = np.abs(data_diff)
				logging.info('detecting done')

				hanning = windowing(100, 100)
				logging.info('hanning done')
				
				data_out = lowPassFilter(hanning, 1.0, envelope)
				logging.info('low pass done')

				mean = np.mean(data_out)
				sig = data_out[MAX_FREQUENCY/SAMPLE_RATE*2:len(data_out):MAX_FREQUENCY/SAMPLE_RATE*4]
				
				for bit in sig:
					l.append(0 if bit > mean else 1)

				bits = list2string(l)
				logging.info(bits)

				try:
					logging.info('Hamming process')
					corrected = Hammingcorrector(bits)
					de = Hammingdecoder(corrected)
					logging.info(de)
					return decodeBaudot(de)
				except IndexError:
					logging.info('Index Error')
			else:
				time.sleep(.01)

	def decode(self):

		#if not self.pipeline.empty():

		#time.sleep(.01)

		logging.info('begin decoding')

		samples = self.pipeline.get()
		l = []
		
		filtered = butterworth(samples, 'high')
		logging.info('filtering done')
		
		smoothed = savitzkyFilter(samples, 11, 6)
		logging.info('smoothing done')
		
		data_diff = differ(smoothed)
		logging.info('differing done')
		
		#envelope = detectEnvelope(data_diff)
		#logging.info('detecting done')
		
		envelope = np.abs(data_diff)
		logging.info('abs done')

		#hanning = windowing(100, 100)
		#logging.info('hanning done')
		
		data_out = lowPassFilter(self.hanning, 1.0, envelope)
		logging.info('low pass done')

		mean = np.mean(data_out)
		sig = data_out[MAX_FREQUENCY/SAMPLE_RATE*2:len(data_out):MAX_FREQUENCY/SAMPLE_RATE*4]
		
		for bit in sig:
			l.append(0 if bit > mean else 1)

		bits = list2string(l)
		logging.info(bits)

		try:
			logging.info('Hamming process')
			corrected = Hammingcorrector(bits)
			de = Hammingdecoder(corrected)
			logging.info(de)
			return decodeBaudot(de)
		except IndexError:
			logging.info('Index Error')


if __name__ == '__main__':

	mic = Recorder()        
	mic.run()
