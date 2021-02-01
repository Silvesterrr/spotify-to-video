def escape(code):
	return '\033['+code
def getrgb(r,g,b,background=False):
	return escape(f'{4 if background else 3}8;2;{r};{g};{b}m')
def gethex(hexdata,background=False):
	return getrgb(*tuple(int(hexdata[i:i+2], 16) for i in (0, 2 ,4)),background=background)
def modifier(_id):
	names = {
		'reset':0,
		'bold':1,
		'faint':2,
		'italic':3,
		'reverse':7,
		'conceal':8,
		'reveal':28,
		'black':30,
		'darkred':31,
		'darkgreen':32,
		'orange':33,
		'darkblue':34,
		'darkmagenta':35,
		'darkcyan':36,
		'gray':37,
		'gray2':90,
		'red':91,
		'green':92,
		'yellow':93,
		'blue':94,
		'magenta':95,
		'cyan':96,
		'white':97
	}
	if str(_id).lower() in names:
		_id = names[_id]
	return escape(f'{_id}m')
def color(col,text):
	return modifier(col)+str(text)+modifier('reset')


def optimizemove(x1,y1,x2,y2):
	x1,y1,x2,y2=int(x1),int(y1),int(x2),int(y2)
	if x1 == x2:
		if y1 == y2:
			escapecode= ''
		else:
			if y2-y1>0:
				poschange = y2-y1
				if poschange == 1:
					escapecode=escape('B')
				else:
					escapecode=escape(f'{poschange}B')
			else:
				poschange = y1-y2
				if poschange == 1:
					escapecode=escape('A')
				else:
					escapecode=escape(f'{poschange}A')
			escapecode+=escape('D')
	elif y1 == y2:
		if x2-x1 == 1:
			escapecode= ''
		elif x2-x1>0:
			poschange = x2-x1
			if poschange == 0:
				escapecode=escape('C')
			else:
				escapecode=escape(f'{poschange-1}C')
		else:
			poschange = x1-x2+1
			if poschange == 1:
				escapecode=escape('D')
			else:
				escapecode=escape(f'{poschange-1}D')
	else:
		escapecode=escape(f'{y2};{x2}H')
	return escapecode