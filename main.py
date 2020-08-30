import pygame
import pygame.midi
from time import sleep
import numpy as np
from random import random
from copy import deepcopy

pygame.init()
pygame.midi.init()

pygame.display.set_caption("musicmatrix")


for x in range( 0, pygame.midi.get_count() ):
    print(x,"=",pygame.midi.get_device_info(x))

port = 7#pygame.midi.get_default_output_id()
midi_out = pygame.midi.Output(port, 0)

screen = pygame.display.set_mode((640,480))

color = (255, 255, 255)

NF = 16

tones = np.array([random() for i in range(NF)], dtype=np.float)

matrix = np.array([[random() for x in range(NF)] for y in range(NF)], dtype=np.float)

for i in range(NF):
	matrix[i][i] = 1

rw = rh = 16
mx = my = 0
rx = ry = 0

mb = None

def minmax(mi, v, ma):
	return max(min(v,ma),mi)

velocity = 100
def note(i):
	return 40+i

step = 0
running = True
while running:
	screen.fill(color)
	
	for y in range(NF):
	
		pygame.draw.rect(screen, (255*tones[y], 0, 0), pygame.Rect(NF*rw+rw*y, 0, rw, rh))
	
		for x in range(NF):
			pygame.draw.rect(screen, (0, 0, 255*matrix[y][x]), pygame.Rect(x*rw, y*rh, rw, rh))
	
	#pygame.draw.rect(screen, (255, 0, 0), pygame.Rect(i, i, 40, 30))
	step += 1

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			running = False
		elif event.type == pygame.MOUSEMOTION:
			mx, my = pygame.mouse.get_pos()
		elif event.type == pygame.MOUSEBUTTONDOWN:
			mx, my = pygame.mouse.get_pos()
			mb = event.button
			
			if mb in [4,5]:
				oldmatrix = deepcopy(matrix)
				indexdelta = -1 if mb == 4 else 1
				for y in range(NF):
					for x in range(NF):
						matrix[y,x] = oldmatrix[y,(x+indexdelta)%NF]
		elif event.type == pygame.MOUSEBUTTONUP:
			mb = None

	lasttones = deepcopy(tones)

	if mb in [1,3]:
		delta = 0.5 if mb == 1 else -0.5
		rx, ry = mx//rw, my//rh
		if 0 <= rx < NF and 0 <= ry < NF:
			matrix[ry,rx] = minmax(0, matrix[ry][rx]+delta, 1)

		elif ry == 0 and NF <= rx < NF+NF:
			delta = 1 if mb == 1 else -1
			tones[rx-NF] = minmax(0, tones[rx-NF]+delta, 1)

	alive = 0
	for y in range(NF):
		for x in range(NF):
			if matrix[y,x] > 0.5:
				alive += 1
	
	aliveperc = alive/NF**2
	

	tones = [minmax(0,v/aliveperc,1) for v in matrix.dot(tones)]#v/NF*2#v/NF*8
	
	if step % 10 == 0:
		# Game of life
		oldmatrix = deepcopy(matrix)
		for y in range(NF):
			for x in range(NF):
				alive = 0
				for dy in range(-1,2):
					for dx in range(-1,2):
						if dy == 0 and dx == 0:
							continue
						if oldmatrix[(y+dy)%NF,(x+dx)%NF] >= 0.5:
							alive += 1
				if oldmatrix[y,x] >= 0.5:
					matrix[y,x] = 1 if 1 < alive < 4 else 0#1-oldmatrix[y,x]
				else:
					matrix[y,x] = 1 if alive == 3 else 0 
	
	for i in range(NF):
		if tones[i] >= 0.5:
			if lasttones[i] < 0.5:
				midi_out.note_on(note(i), velocity)
		else:
			if lasttones[i] >= 0.5:
				midi_out.note_off(note(i))
	
	pygame.display.flip()
	sleep(0.04)

