#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import re

class LPD8806:

	spidev = "spidev" #"/dev/spidev0.0"

	def __init__(self,nLeds):

		self.nLeds = nLeds
		self.reset()

	def reset(self):
		data = [0x00]					# Set ledstrip in "data-accept" mode
		for i in range(0,self.nLeds):
			data += [0x80,0x80,0x80]	# Set G,R,B with each MSB set high
										# (representing a color byte)
										# and remaining bits to 0
										# (the intensity bits)
										# resulting in a blank led

		data += [0x00]					# Already set ledstrip in "data-accept" mode + final latch
										# to speed-up next data push

		self.pushdata(data)

	def pushdata(self,data):
		with open(self.spidev,"wb") as l:
			l.write(bytes(data))
			l.flush()

	def rgbToLedGrb(self,rgb):
		if not 0 <= rgb[0] <= 255:
			raise Exception("r out of bounds (%i)" % (rgb[0]))
		elif not 0 <= rgb[1] <= 255:
			raise Exception("g out of bounds (%i)" % (rgb[1]))
		elif not 0 <= rgb[2] <= 255:
			raise Exception("b out of bounds (%i)" % (rgb[2]))

		return [((rgb[1]//2)+128),((rgb[0]//2)+128),((rgb[2]//2)+128)] #GRB

	def hexToLedGrb(self,hexc):
		m = re.findall("(\w\w)",hexc)
		return self.rgbToLedGrb([ int(m[0],16), int(m[1],16), int(m[2],16) ])

	def setPixels(self,pixelcolors,colorFormat):
		if len(pixelcolors) > self.nLeds:
			raise Exception("pixelcolors out of bounds")

		data = [0x00]
		for i in range(0,len(pixelcolors)):
			if colorFormat == "rgb":
				data += self.rgbToLedGrb(pixelcolors[i])
			elif colorFormat == "hex":
				data += self.hexToLedGrb(pixelcolors[i])
			else:
				raise Exception("unknown color format")


		data += [0x00]
		self.pushdata(data)


