# 

import sys

from tkinter import *
from tkinter.ttk import *
import tkinter.font


class SqlHistoryWnd(Frame):
    def __init__(self, callback):
        self._callback = callback
    
        Frame.__init__(self, master)
        self.master.title("History")
        self.grid(sticky=N+S+E+W)

        top = self.winfo_toplevel()
        top.columnconfigure(0, weight=1)
        top.rowconfigure(0, weight=1)

        self.columnconfigure(0, weight=1) # Column with editor text controls
        self.rowconfigure(0, weight=1) # Toolbar row

        self.b_history = Button(self, text="Browse history", width=15, command=self._on_browse_history)
        self.b_history.grid(row=1, columnspan=1, sticky=N+E+S+W)
