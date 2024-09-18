import tkinter as tk
import tkinter.ttk as ttk
import subprocess
from pathlib import Path
import re
from time import sleep
import random
from functools import partial
import sv_ttk

"""
#
#
#new file template
#
#
"""

template = """'
public class {0} {1}
	public static void main(String[] s) {1}
		System.out.println("hello, world!");
	{2}
{2}
'"""

"""
#
#Input
#Handlers
#
#
"""

def filltext(event=None):
	global txt
	#file = cb.get()          #
	#f = Path(file).open()#keep for future windows compatability
	#n = f.read()             #
	#f.close()	          #
	txt.delete('1.0', 'end')
	txt.insert('end',subprocess.run("cat " + cb.get(),shell=True,capture_output=True).stdout)
	updatehighlight()

def fetchfiles(event=None):
	cb['values'] = list(Path('.').glob('*.java'))
	file = cb.get()
	  

def compile(event=None):
	save()
	file = cb.get()
	print("compiling\n")
	r = subprocess.run("javac " + file,shell=True,capture_output=True)
	if not r.stderr:
		subprocess.run("java " + file[0:-5],shell=True)
	else:
		print(r.stderr.decode())

def makenew(event):
	file = cb.get()
	if not Path(file) in list(Path('.').glob('*.java')):
		subprocess.run("echo " + template.format(file[0:-5],'{','}') + " > " + file,shell=True)
	filltext()

def flatten_helper(l):
	s = ""
	for i in l:
		s += i
	return s

def save(event=None):
	global txt 
	subprocess.run("(cat <<\\END\n" + txt.get("1.0", tk.END) + "\nEND\n) > " + cb.get(), shell=True)

def run(event=None):
	file = cb.get()
	subprocess.run("java " + file[0:-5],shell=True)

def togglemod(event):
	global mod
	global window
	global pastebin2
	global cursorpos
	global txt
	try:
		pastebin2 = txt.selection_get()
	except tk.TclError as e:
		pastebin2 = ""
	cursorpos = txt.index(tk.INSERT)
	window.focus_set()
	mod = not mod

def copy():
	global pastebin
	global pastebin2
	global txt
	if pastebin2 != "":
		pastebin = pastebin2

def paste():
	global pastebin
	global txt
	global cursorpos
	txt.insert(cursorpos,pastebin)

def warnshortcut():
	print("Leapcode: Warning: Unrecognized Shortcut\n")

def pressedkey(event):
	global mod
	global keymap
	global txt
	updatehighlight(start=txt.index(tk.INSERT + "-9c"),end=txt.index(tk.INSERT + "+9c"),inputupdate=True)
	#removehighlight(backspace=-1)
	print(event.char.encode())
	try:
		if chr(event.char.encode()[0] + 96) != event.char and chr(int.from_bytes(event.char.encode()) + 96) in keymap:
			keymap[keymap.index(chr(int.from_bytes(event.char.encode()) + 96))+1]()	
	except(IndexError):
		print("")
def processmatches(mo,startm,update=False):
	global txt
	global upar
	mtch = mo.group(0)
	(start, end) = mo.span()
	starts = startm + "+" + str(start) + "c"
	ends = startm + "+" + str(end) + "c"
	openpar = "({["
	closepar = ")}]"
	if mtch[-1] == '"':
		#if  (len(txt.tag_names(starts)) > 0 and not txt.tag_names(starts)[0] == 'string') or not len(txt.tag_names(starts)) > 0:
		txt.tag_remove("ustring", starts, tk.END)
		txt.tag_add("string", starts, ends)
		print(mtch)
		#	if len(txt.tag_names(starts)) > 0:
		#		print(txt.tag_names(starts)[0])
	elif mtch[0] == '"':
		txt.tag_remove("string", txt.index(starts).split('.')[0] + ".0", ends)
		txt.tag_add("ustring", starts, tk.END)
	elif mtch in openpar:
		upar[openpar.index(mtch)].append(starts)
	elif ((mtch in closepar) and (len(upar[closepar.index(mtch)]) > 0)):
		s = upar[closepar.index(mtch)].pop()
		txt.tag_remove("unmp", s)
		txt.tag_remove("unmp", starts)
		txt.tag_add(mtch, s)
		txt.tag_add(mtch, starts)
	elif mtch in closepar:
		txt.tag_add("unmp", starts)
	else:
		r = re.search("([a-zA-Z0-9]+)",mtch)
		starts += "+" + str(r.span()[0]) + "c"
		ends += "-" + str(len(mtch) - r.span()[1]) + "c"
		txt.tag_add(r.group(0), starts, ends)

def removehighlight():
	global txt
	linestart = txt.index(tk.INSERT).split('.')[0] + "." 
	lineend = txt.index(txt.index(tk.INSERT).split('.')[0] + ".end")
	cur = 0
	collect = False
	rmvs = ""
	rmve = ""
	cont = False
	isend = True
	detected = False
	while cur <= int(lineend.split('.')[1]) and rmve == "":
		linecur = linestart + str(cur)
		tags = txt.tag_names(linecur)
		ch = txt.get(linecur)
		wasend = isend
		isend = ch in " \n\t[]{}(),.;:"
		if tags and tags[0] in "[]{}()" and not ch in "[]{}()":
			txt.tag_remove(tags[0], linecur)
		elif collect and len(tag) == 0 and not detected and isend: 
			rmvs = rmve = ""
			collect = False
		elif collect and not isend and not detected:
			if not tag or not ch == tag[0]:
				detected = True
			else: 
				cmp += ch
				tag = tag[1:]		
		elif collect and rmvs != "" and isend:
			rmve = linecur
			collect = False
		elif collect:
			detected = True
		elif len(tags) > 0 and tags[0] in ["if", "while", "public", "class", "void", "static", "double", "int", "String", "for", "boolean","break","true","false"]:	
			taglt = tags[0]
			rmvs = linecur			
			cmp = ch
			tag = tags[0][1:]
			collect = True
			if not wasend:
				detected = True
		cur += 1
	if rmve != "":
		txt.tag_remove(taglt, rmvs, rmve)
		
def updatehighlight(event=None,start="1.0",end=tk.END,inputupdate=False):
	global txt
	global upar
	if inputupdate:
		removehighlight()
	re.sub("[ \n\t,.()[\\]{};]+((if)|(while)|(public)|(class)|(void)|(static)|(double)|(int)|(String)|(for)|(boolean)|(true)|(false)|(break))(?![a-zA-Z0-9])", partial(processmatches, startm=start, update=True), txt.get(start, end))
	re.sub('("[a-zA-Z0-9!@#$%^&*()-=_+[\]{}\\:;\',./?>< |]*")|(".*)|[(){}]|([][])', partial(processmatches, startm='1.0'), txt.get('1.0', tk.END))
	for l in upar:
		while len(l) > 0:
			txt.tag_add("unmp", l.pop(0))

def toggletheme(event=None):
	global lighttheme
	lighttheme = not lighttheme
	if lighttheme:
		sv_ttk.set_theme("light")
	else:
		sv_ttk.set_theme("dark")

def checkpaste(event=None):
	global pasted
	global window
	if pasted:
		updatehighlight()
		pasted = False
	window.after(2000, checkpaste)

def setpasted(event=None):
	global pasted
	pasted = True

"""
#
#
#keymap 
#
#
"""

keymap = ["f",compile,"s",save,"r",run]

"""
#
#splashscreen
#
"""

sswindow = tk.Tk()
sswindow.geometry("300x300")
ttk.Label(text="leapcode").grid(column=0,row=0,sticky="e")
ttk.Label(text="v0.0.3").grid(column=0,row=1,sticky="e")

lt = tk.StringVar()
lt.set("leap's tip of the day: if statements are like onions- they have layers")

leapstip = ttk.Label(textvariable=lt)
leapstip.grid(column=1,row=2,sticky="es")

sm = tk.StringVar()
sm.set("optimizing assemblies")
statusmessage = ttk.Label(textvariable=sm)
statusmessage.grid(column=1,row=3)

status = 0

def querying():
	global sm
	sm.set("querying neural networks for answers")

def leaposcheck():
	global sm
	global status
	sm.set("checking leapOS flag")
	status = 1

def updatew():
	global sm
	global status
	if status:
		return
	if sm.get()[-3:-1] == "..":
		sm.set(sm.get()[0:-3])
	else:
		sm.set(sm.get() + '.')
	sswindow.after(1000, updatew)

sswindow.after(0, updatew)
sswindow.after(4050, querying)
sswindow.after(7050, leaposcheck)
sswindow.after(9000, sswindow.destroy)
sswindow.mainloop()

"""
#
#
#initialization
#
#
"""

mod = False
pastebin = "" #copied text for pasting
pastebin2 = "" #highlighted text before shortcut workaround
cursorpos = "" #cursor position before shortcut workaround
#status = 0       #syntax highlighting status OBSOLETE
upar = [[],[],[]]
uterm = []
lighttheme = False
pasted = False

window = tk.Tk()
ttk.Label(text="  leapcode").grid(column=0,row=0,sticky="ws")
ttk.Label(text="    v0.0.3").grid(column=0,row=1,sticky="wn")

nb = ttk.Button(text="+",width=1)
nb.grid(column=1,row=1,sticky="w")

txt = tk.Text(window,height=50,width=100)
txt.grid(column=0,row=2,columnspan=3,rowspan=3)
txt.tag_config("if", foreground="blue")
txt.tag_config("(", foreground="bisque4")
txt.tag_config(")", foreground="bisque4")
txt.tag_config("{", foreground="dark green")
txt.tag_config("}", foreground="dark green")
txt.tag_config("[", foreground="cyan4")
txt.tag_config("]", foreground="cyan4")
txt.tag_config("unmp", foreground="red")
txt.tag_config("while",foreground="blue")
txt.tag_config("for",foreground="blue")
txt.tag_config("class",foreground="blue")
txt.tag_config("static",foreground="blue")
txt.tag_config("public",foreground="blue")
txt.tag_config("void",foreground="cyan4")
txt.tag_config("double",foreground="cyan4")
txt.tag_config("int",foreground="cyan4")
txt.tag_config("String",foreground="cyan4")
txt.tag_config("boolean",foreground="cyan4")
txt.tag_config("true",foreground="purple")
txt.tag_config("false",foreground="purple")
txt.tag_config("break",foreground="blue")
txt.tag_config("ustring", foreground="red")
txt.tag_config("string", foreground="brown")

cb = ttk.Combobox(text="select code",width=17)
cb.grid(column=1,row=1,padx=30,sticky="w")

fetchfiles()

rb = ttk.Button(text="run")
rb.grid(column=0,row=1,sticky="e")

color = ttk.Button(text="Compile!")
color.grid(column=1,row=0,sticky="w")

tb = ttk.Button(text="theme")
tb.grid(column=1,row=0,sticky="w",padx=85)

sb = ttk.Button(text="save")
sb.grid(column=1,row=0,sticky="w",padx=152)

sv_ttk.set_theme("dark")

"""
#
#
#binding handlers
#
#
"""

cb.bind("<Enter>", fetchfiles)
cb.bind("<<ComboboxSelected>>", filltext)
color.bind("<Button-1>", compile) 
tb.bind("<Button-1>", toggletheme) 
nb.bind("<Button-1>", makenew)
sb.bind("<Button-1>", save)
rb.bind("<Button-1>",run)
window.bind("<<Paste>>", setpasted)
window.after(1000, checkpaste)
#txt.bind("<BackSpace>", removehighlight)
#window.bind("<Control_L>",togglemod)
window.bind("<Key>",pressedkey)
window.mainloop()
