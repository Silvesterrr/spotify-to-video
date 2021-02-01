import sys
import termios
import os
import string
import xterm.helpers as h
from threading import Thread
import time
from concurrent.futures import ThreadPoolExecutor

width, height = os.get_terminal_size()
stream = sys.stdin
mode = termios.tcgetattr(stream)
mode[3] = mode[3] &~ (termios.ECHO | termios.ICANON | termios.IEXTEN | termios.ISIG)
termios.tcsetattr(sys.stdin,1,mode)
getrgb = h.getrgb
escape = h.escape

_print = print

_print(escape('?1003h'),end='') # click detection
_print(escape('?1006h'),end='') # make it better
_print(escape('?25l'),end='') # hide cursor
_print(escape('?7l'),end='') # don't  line wrap
def clear():
	_print(escape('2J'),end=escape('H'),flush=True)
clear()
class mouse_click():
	def __init__(self,name,_id,x,y,down):
		self.type = name
		self.id = _id
		self.x = x
		self.y = y
		self.down = down
#	def __str__(self):
#		if self.type in ['mouse','mouse 2','middle mouse']:
#			return f'{self.type} {"down" if self.down else "up"}'
#		else:
#			return str(self.type)
	def __str__(self):
		if self.type in ['mouse','mouse 2','middle mouse']:
			return f'<{self.type} {"down" if self.down else "up"} ({self.x}, {self.y})>'
		else:
			return f'<{self.type} ({self.x}, {self.y})>'

def parse_mouse_sequence():
	mouseid = ''
	while True:
		text = read_stream()
		if text == ';':break
		mouseid += text
	x = ''
	while True:
		text = read_stream()
		if text == ';':break
		x += text
	y = ''
	while True:
		text = read_stream()
		if text in 'Mm':break
		y += text
	x, y, mouseid = int(x)-1, int(y)-1, int(mouseid)
	mouse_names = {
		0:'mouse',
		1:'middle mouse',
		2:'mouse 2',
		4:'forward button down',
		32:'mouse dragged',
		33:'middle mouse drag',
		34:'mouse 2 dragged',
		35:'back button down',
		36:'forward button still down',
		64:'scroll up',
		65:'scroll down'
	}
	if mouseid in mouse_names:
		return mouse_names[mouseid],mouseid,x,y,text=='M'
	else:
		return 'unknown',mouseid,x,y,text=='M'

def parse_combo(esccode):
	escapetype = esccode[-1]
	esccode = esccode[:-1]
	data = esccode.split(';')
	extrakeys = ''
	if len(data) == 2:
		arg = int(data[1])
		codes={
			2:'SHIFT',
			3:'ALT',
			5:'CTRL',
			6:'CTRL+SHIFT',
			7:'CTRL+ALT',
			8:'CTRL+SHIFT+ALT',
			9:'CMD',
			13:'CMD+CTRL',
			16:'CTRL+SHIFT+ALT+CMD'
		}
		if arg in codes:
			extrakeys = codes[arg]+'+'
		else:
			extrakeys = f'{arg}+'

	if escapetype == '~':
		arg = int(data[0])
		codes = {
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
		if arg in codes:
			return extrakeys+codes[arg]
	else:
		other_keys = {
			'A':'UP',
			'B':'DOWN',
			'C':'RIGHT',
			'D':'LEFT',
			'H':'HOME',
			'F':'END'
		}
		if escapetype in other_keys:
			return extrakeys + other_keys[escapetype]

	return 'idk '+str(esccode)+' '+str(data)+' '+str(escapetype)+' '+extrakeys

def parse_csi_sequence():
	esccode=''
	while True:
		text = read_stream()
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
				f = read_stream()
				return f'F{ord(f)-79}'
			elif esccode == '[<':#better mouse
				mousedata = parse_mouse_sequence()
				mousedata = mouse_click(*mousedata)
				return mousedata
			elif esccode[-1] in '~ABCDFH':#idek what these do
				return parse_combo(esccode[1:])
			else:
				_print(f'WARNING: Unknown escape code: {esccode}')
			esccode = ''
			break
def read_stream():
	return stream.read(1)
def readchr():
	c = read_stream()
	keycode = ord(c)
	if keycode < 32 or keycode >= 127:
		codes = {
			8:'SHIFT+BACKSPACE',
			9:'TAB',
			10:'ENTER',
			127:'BACKSPACE'
		}
		if keycode==27:#escape
			key = parse_csi_sequence()
			return key
		else:
			if keycode in codes:
				return codes[keycode]
			else:
				return keycode
	else:
		return c
def readchrs():
	while True:
		yield readchr()

class data:
	x,y=1,1
	xtmp,ytmp=1,1
	eventlisteners = []
	eventtypes = ('all','key','mouse','chr','click','drag','arrow','frame')

def goto(x,y):
	data.xtmp,data.ytmp=x,y
def move(direction,amount=1):
	direction = direction.lower()
	if direction in ['up','north']:
		data.ytmp -= amount
	elif direction in ['down','south']:
		data.ytmp += amount
	elif direction in ['right','east']:
		data.xtmp += amount
	elif direction in ['left','west']:
		data.xtmp -= amount
	else:
		raise ReferenceError('please enter a valid direction')
	return data.xtmp,data.ytmp

def print(*content,x=None,y=None,end='\n\r',clearline=False,modifier=None):
	if x!=None:data.xtmp=x
	if y!=None:data.ytmp=y
	content=' '.join(str(c) for c in content)
	#_print('[',data.x,data.y,data.xtmp,data.ytmp,end='',flush=True)
	escapecode = h.optimizemove(data.x,data.y, data.xtmp,data.ytmp)
	data.x, data.y = data.xtmp, data.ytmp
	content = content+end
	end=''
	if clearline:
		escapecode += escape('2K')
	if modifier != None:
		escapecode += h.modifier(modifier)
	_print(escapecode+content,end='',flush=True)
	inescape = False
	escaped = ''
	escapechars = '@ABCDEFGHIJKLMPSTXZ`abcdefglmnpqrsu'
	for c in content:
		if ord(c) == 27:
			inescape = True
			continue
		if inescape:
			if c in escapechars:
				inescape = False
				escaped += c
				continue
			else:
				escaped += c
		else:
			data.xtmp += 1
			if c == '\n':
				data.ytmp += 1
			elif c == '\r':
				data.xtmp = 1
	data.x=data.xtmp
	data.y=data.ytmp

	if modifier != None:
		escapecode += h.modifier('reset')
#_print(data.x,data.y,data.xtmp,data.ytmp,end=']',flush=True)


def is_event(eventtype,char):
	if eventtype in ['mouse','click','drag']:
		if type(char) != str:
			if eventtype == 'click':
				return char.type == 'mouse' and char.down
			elif eventtype == 'drag':
				if char.type == 'mouse' and char.down:
					return True
				elif char.type == 'mouse dragged':
					return True
			else:
				return True
	elif eventtype in ['key','chr','arrow']:
		if type(char) == str:
			if eventtype == 'chr':
				return len(char) == 1
			elif eventtype == 'arrow':
				return char in ['UP','DOWN','LEFT','RIGHT']
			else:
				return True
	else:
		if eventtype=='all':
			return True
		else:
			return False

def readchrs_thread():
	for char in readchrs():
		for listener in data.eventlisteners:
			func = listener[0]
			eventtype = listener[1]
			if is_event(eventtype,char):
				func(char)

def event(arg='all'):
	if arg not in data.eventtypes:
		raise ReferenceError(f'Unknown event type. Please choose one of the following: {data.eventtypes}')
	def createlistener(func):
		data.eventlisteners.append((func,arg))
		if len(data.eventlisteners) == 1:
			Thread(target=readchrs_thread).start()
	return createlistener

def run_forever(fps=10):
	while True:
		t1 = time.time()
		for listener in data.eventlisteners:
			func = listener[0]
			eventtype = listener[1]
			if eventtype == 'frame':
				func()
		t2 = time.time()
		time.sleep((1/fps)-(t2-t1))
def wait_for_key(key):
	while readchr() != key:pass
color = h.color