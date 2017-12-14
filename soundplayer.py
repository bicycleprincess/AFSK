import pyaudio

import alsaaudio

RATE = 44100
CHANNELS = 1
BUFFER = 1024

class Audio(object):

	def __init__(self):

		self.p = pyaudio.PyAudio() 
		self.stream = self.p.open(format=pyaudio.paInt16, channels=CHANNELS, rate=RATE, output=True, frames_per_buffer=BUFFER)

	def play(self, signal, loop=1):

		for i in range(loop):
			self.stream.write(signal, len(signal))

		#self.stream.close()
		#self.p.terminate()
		

# alsaaudio version
def alsaplay(signal, channels, rate):

	#device = alsaaudio.PCM(mode=alsaaudio.PCM_PLAYBACK)
	#device = alsaaudio.PCM(type=alsaaudio.PCM_PLAYBACK, mode=alsaaudio.PCM_NORMAL)
	device = alsaaudio.PCM(mode=alsaaudio.PCM_NORMAL)
	try:
		device.setchannels(channels)
		device.setrate(rate)
		device.setformat(alsaaudio.PCM_FORMAT_S16_LE)

	except ValueError:
		pass
	else:
		device.setchannels(CHANNELS)
		device.setrate(RATE)
		device.setformat(alsaaudio.PCM_FORMAT_S16_LE)
		
	device.write(signal)
