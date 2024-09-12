import tkinter as tk
import tkinter.ttk as ttk
import subprocess
from pathlib import Path
import re

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
	txt.delete('1.0', 'end')
	txt.insert('end',subprocess.run("cat " + cb.get(),shell=True,capture_output=True).stdout)
	#f.close()	          #

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
	file = cb.get()  #first we have to use stdin with a custom delimiter to catch all chars, then we use split to cleanup (add tabs and newlines, set -f fixes asterisk expansion)
	print("data=$(cat <<\\!eof!\n" + flatten_helper([line + "\*" for line in (flatten_helper([line + "\\t" for line in re.split(r"\t",flatten_helper([line + "\\n" for line in txt.get('1.0', 'end').splitlines()]))])).split(sep="*")])[0:-7] + "\n!eof!\n); echo $data > " + file)
	subprocess.run("set -f; data=$(cat <<\\!eof!\n" + flatten_helper([line + "\\t" for line in re.split(r"\t",flatten_helper([line + "\\n" for line in txt.get('1.0', 'end').splitlines()]))])[0:-4] + "\n!eof!\n); echo $data > " + file,shell=True)

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
	if mod:
		if chr(event.char.encode()[0] + 96) in keymap:
			mod = not mod
			keymap[keymap.index(chr(event.char.encode()[0] + 96))+1]()
		else:
			warnshortcut()

"""
#
#
#keymap 
#
#
"""

keymap = ["f",compile,"s",save,"r",run,"c",copy,"v",paste]

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

window = tk.Tk()
ttk.Label(text="  leapcode").grid(column=0,row=0,sticky="ws")
ttk.Label(text="    v0.0.2").grid(column=0,row=1,sticky="wn")

nb = ttk.Button(text="+",width=1)
nb.grid(column=1,row=1,sticky="w")

txt = tk.Text(window,height=50,width=100)
txt.grid(column=0,row=2,columnspan=3,rowspan=3)

cb = ttk.Combobox(text="select code",width=17)
cb.grid(column=1,row=1,padx=18,sticky="w")

fetchfiles()

rb = ttk.Button(text="run")
rb.grid(column=0,row=1,sticky="e")

sb = ttk.Button(text="save")
sb.grid(column=0,row=1)

style = ttk.Style()

style.configure('C.TButton',font='helvetica 24',background='SpringGreen4')
style.map('C.TButton',background=[('pressed', 'SpringGreen4')])

color = ttk.Button(text="Compile!",style="C.TButton")
color.grid(column=1,row=0,sticky="w")

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
nb.bind("<Button-1>", makenew)
sb.bind("<Button-1>", save)
rb.bind("<Button-1>",run)
window.bind("<Control_L>",togglemod)
window.bind("<Key>",pressedkey)
window.mainloop()
