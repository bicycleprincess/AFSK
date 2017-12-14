from baudot import encodeBaudot
from soundencoder import encodeSound
from convertions import list2string, binary2array 
from sounddecoder import denormalize
from soundplayer import Audio
from hamming import Hammingencoder


text = str(raw_input('input the data: '))
baudot = list2string(encodeBaudot(text))
hamming = Hammingencoder(baudot)
data = binary2array(hamming)
signal = encodeSound(data)
sound = denormalize(signal) 
player = Audio()
player.play(sound, 3, 3)
