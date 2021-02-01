'''
Asynchronous fork of xTerm module
'''

import sys
import termios
import os
import string
import xterm.helpers as h
from concurrent.futures import ThreadPoolExecutor
import asyncio


executor = ThreadPoolExecutor(1)
loop = asyncio.get_event_loop()

width, height = os.get_terminal_size()
stream = sys.stdin
mode = termios.tcgetattr(stream)
mode[3] = mode[3] &~ (termios.ECHO | termios.ICANON | termios.IEXTEN | termios.ISIG)
termios.tcsetattr(sys.stdin,1,mode)
print(h.escape('?1003h'),end='') # click detection
print(h.escape('?1006h'),end='') # make it better
print(h.escape('?25l'),end='') # hide cursor
print(h.escape('?7h'),end='') # don't  line wrap
def clear():
	print(h.escape('2J'),end=h.escape('H'),flush=True)
clear()
class mouseClick():
	def __init__(self,name,_id,x,y,clicking):
		self.type = name
		self.id = _id
		self.x = x
		self.y = y
		self.down = clicking
	def __str__(self):
		if self.type in ['mouse','mouse 2','middle mouse']:
			return f'{self.type} {"down" if self.down else "up"}'
		else:
			return str(self.type)
	def __repr__(self):
		return f'<{self.type} ({self.x}, {self.y})>'

async def parseMouseCode():
	mouseid = ''
	while True:
		text = await streamread()
		if text == ';':break
		mouseid += text
	x = ''
	while True:
		text = await streamread()
		if text == ';':break
		x += text
	y = ''
	while True:
		text = await streamread()
		if text in 'Mm':break
		y += text
	x, y, mouseid = int(x)-1, int(y)-1, int(mouseid)
	mousenames = {0:'mouse',32:'mouse dragged',2:'mouse 2',34:'mouse 2 dragged',64:'scroll up',65:'scroll down',1:'middle mouse',33:'middle mouse drag',4:'forward button down',36:'forward button still down',35:'back button down'}
	if mouseid in mousenames:
		return mousenames[mouseid],mouseid,x,y,text=='M'
	else:
		return 'unknown',mouseid,x,y,text=='M'

async def parseMagicKeys(esccode):
	oof = esccode[-1]
	esccode = esccode[:-1]
	data = esccode.split(';')
	foo = '' #quality variable naming, ik
	if len(data) == 2:
		things={2:'SHIFT',3:'ALT',5:'CTRL',6:'CTRL+SHIFT',7:'CTRL+ALT',8:'CTRL+SHIFT+ALT',9:'CMD',13:'CMD+CTRL',16:'CTRL+SHIFT+ALT+CMD'}
		if data[1] in things:
			foo = things[data[1]]+'+'
		else:
			foo = data[1]+'+'

	if oof == '~':
		if len(data) == 1:
			things2 = {
				2:'INSERT',
				3:'DELETE',
				5:'PAGEUP',
				6:'PAGEDOWN',
				15:'F5',
				17:'F6',
				18:'F7',
				19:'F8',
				20:'F9',
				21:'F10',
				23:'F11',
				24:'F12'
			}
			if data[0] in things2:
				return things2[data]
	elif oof == 'A':
		return foo+'UP'
	elif oof == 'B':
		return foo+'DOWN'
	elif oof == 'C':
		return foo+'RIGHT'
	elif oof == 'D':
		return foo+'LEFT'
	elif oof == 'H':
		return foo+'HOME'


	return 'idk '+str(esccode)+' '+str(data)+' '+str(oof)+' '+foo

async def parseEscapeCode():
	esccode=''
	while True:
		text = await streamread()
		esccode += text
		if text in string.ascii_letters+'<~':
			if esccode == '[D':#left arrow
				return 'LEFT'
			elif esccode == '[C':#right arrow
				return 'RIGHT'
			elif esccode == '[A':#up arrow
				return 'UP'
			elif esccode == '[B':#down arrow
				return 'DOWN'
			elif esccode == '[O':#unfocus
				return 'UNFOCUS'
			elif esccode == '[I':#focus
				return 'FOCUS'
			elif esccode == '[F':#end
				return 'END'
			elif esccode == '[Z':#end
				return 'SHIFT+TAB'
			elif esccode == 'O':#f 1-4
				f = await streamread()
				return f'F{ord(f)-79}'
			elif esccode == '[<':#better mouse
				mousedata = await parseMouseCode()
				mousedata = mouseClick(*mousedata)
				return mousedata
			elif esccode[-1] in '~ABCDFH':#idek what these do
				return await parseMagicKeys(esccode[1:])
			else:
				raise NameError(f'Unknown escape code: {esccode}')
			esccode = ''
			break
def readstream():
	return stream.read(1)
async def streamread():
	return await loop.run_in_executor(executor,readstream)
async def readchr():
	c = await streamread()
	if ord(c)==27:#escape
		key = await parseEscapeCode()
		return key
	elif ord(c)==8:
		return 'SHIFT+BACKSPACE'
	elif ord(c)==127:
		return 'BACKSPACE'
	elif ord(c)==10:
		return 'ENTER'
	elif ord(c)==9:
		return 'TAB'
	else:
		return c
async def readchrs():
	while True:
		yield await readchr()
getrgb = h.getrgb
escape = h.escape