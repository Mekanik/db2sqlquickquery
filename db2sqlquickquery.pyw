#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
'db2sqlquickquery' - AS400 DB2 SQL editor with syntax highlight and autocomplete.
"""


import sys

from tkinter import *
from tkinter.ttk import *
import tkinter.font

import re

import solcolors as colorscheme
from sqlcomplete import Autocomplete
from sqleditor import SqlEditor
from sqlquery import SqlQuery
from sqlsyntaxhighlight import SqlSyntaxHighlight
from sqlhistorywnd import SqlHistoryWnd


__author__ = "Vakhrin Vladimir"
__email__ = "vakhwork@gmail.com"
__copyright__ = "2012, Vakhrin Vladimir"
__version__ = "1.0.0"
__status__ = "Production"


FONT_NAME = "Consolas"
FONT_SIZE = 10


FILE_ENCODING = "utf-8"

# AS400 settings
AS_SYSTEM = 'NEW'
AS_USER = '*'
AS_PWD = '*'


databases = ('LOG_TEST', 'REBASE', 'SPB_BASE')

def get_readable(rows):
  if not rows:
    return ""

  columns_max_length = []

  col_index = 0
  for column_desc in rows[0].cursor_description:
    if len(columns_max_length) <= col_index:
      columns_max_length.append(0)
    ln = len(column_desc[0])
    ml = columns_max_length[col_index]
    if ln > ml:
      columns_max_length[col_index] = ln
    col_index += 1

  for row in rows:
    col_index = 0
    for el in row:
      ln = len(str(el).strip())
      ml = columns_max_length[col_index]
      if ln > ml:
        columns_max_length[col_index] = ln
      col_index += 1

  out_str = ""

  col_index = 0
  header_str = ''
  for column_desc in rows[0].cursor_description:
    ln = len(column_desc[0])
    ml = columns_max_length[col_index]
    spaces_needed = ml - ln
    header_str += column_desc[0] + ' ' * spaces_needed + ' | '
    col_index += 1
  header_str += '\n'

  splitter_str = ''
  for symbols in columns_max_length:
    splitter_str += '-' * symbols + '-+-'
  splitter_str += '\n'

  out_str += header_str + splitter_str

  for row in rows:
    col_index = 0
    for el in row:
      ln = len(str(el).strip())
      ml = columns_max_length[col_index]
      spaces_needed = ml - ln
      out_str += str(el).strip() + ' ' * spaces_needed + ' | '
      col_index += 1
    out_str += '\n'

  if len(rows) > 10:
    out_str += splitter_str + header_str

  return out_str



class GuiApp(Frame):
  """ Application DB2 SQL quick query """

  def __init__(self, master=None):
    Frame.__init__(self, master)
    self.master.title("AS400 DB2 sql quick query")
    self.grid(sticky=N+S+E+W)

    self.normal_font = tkinter.font.Font(family=FONT_NAME,size=FONT_SIZE)
    self.italic_font = tkinter.font.Font(family=FONT_NAME, size=FONT_SIZE, slant="italic")
    self.bold_font = tkinter.font.Font(family=FONT_NAME, size=FONT_SIZE, weight="bold")

    self.create_widgets()

    # Database query.
    self._sql_query = SqlQuery(AS_SYSTEM, AS_USER, AS_PWD)
    # Syntax highlighting
    self._syntax = SqlSyntaxHighlight(self.t_q, self.normal_font, self.bold_font, self.italic_font)
    # Autocomplete
    self._complete = Autocomplete(self.t_q)
    self._complete.generate_completion_list(self._sql_query)
    # Indent, navigation, etc
    self._editor = SqlEditor(self.t_q)

    self._bind_events()

  def _bind_events(self):
    self.bind_all('<Control-Key-q>', sys.exit)
    self.bind_all('<Control-Key-r>', self._on_run)
    self.bind_all('<Control-Key-R>', self._on_partial_run)
    self.bind_all('<Control-Key-F>', self._on_format)
    self.bind_all('<Control-Key-U>', self._on_to_upper)
    self.bind_all('<Control-Key-h>', self._on_show_history)

    self.t_q.event_add('<<comment-block>>', '<Control-Key-k>')
    self.t_q.event_add('<<uncomment-block>>', '<Control-Key-K>')
    self.t_q.event_add('<<show-completion>>', '<Control-space>')

  def _on_history_return(self, query):
    self.t_q.insert(INSERT, query)

  def _on_show_history(self, _ = None):
    history_wnd = SqlHistoryWnd(self._on_history_return)
    print("On show history") # TODO 

  def _on_comment_block(self):
    self.t_q.event_generate('<<comment-block>>', when='tail')

  def _on_unclomment_block(self):
    self.t_q.event_generate('<<uncomment-block>>', when='tail')

  def _on_run(self, _ = None):
    """ Run query. """
    query = self.t_q.get(1.0, END)
    self.run(query)

  def _on_partial_run(self, _ = None):
    """ Run selected as query. """
    try:
      query = self.t_q.selection_get()
    except:
      return

    self.run(query)

  def _on_format(self, _ = None):
    self.t_q.event_generate("<<format>>",when="tail")

  def _on_to_upper(self, _ = None):
    self.t_q.event_generate("<<to-upper>>",when="tail")


  def _on_rb_delimiter(self):
    """ Sql delimiter type changed. """
    self._sql_query.set_sql_delimiter(self.rb_sql_var.get())

  
  def _on_browse_history(self):
    pass


  def create_widgets(self):
    """ Create widgets on main application window. """
    # Layout ####################################################################
    top = self.winfo_toplevel()
    top.columnconfigure(0, weight=1)
    top.rowconfigure(0, weight=1)

    self.columnconfigure(0, weight=1) # Column with editor text controls
    self.columnconfigure(1, weight=0) # Side bar

    self.rowconfigure(0, weight=0) # Toolbar row
    self.rowconfigure(1, weight=1) # Text editor and output row
    self.rowconfigure(2, weight=0) # Statusbar row

    # Menu ####################################################################
    self.menu = Menu(top)
    top['menu'] = self.menu

    self.file_menu = Menu(self.menu, tearoff=0)
    self.file_menu.add_command(label="Open", command=None, accelerator="Ctrl+O")
    self.file_menu.add_command(label="Save", command=None, accelerator="Ctrl+S")
    self.file_menu.add_separator()
    self.file_menu.add_command(label="Exit", command=sys.exit, accelerator="Ctrl+Q")
    self.menu.add_cascade(label="File", menu=self.file_menu)

    self.edit_menu = Menu(self.menu, tearoff=0)
    self.edit_menu.add_command(label="To upper", command=self._on_to_upper, accelerator="Ctrl+Shift+U")
    self.edit_menu.add_command(label="Reformat", command=self._on_format, accelerator="Ctrl+Shift+F")
    self.edit_menu.add_separator()
    self.edit_menu.add_command(label="Comment block", command=self._on_comment_block, accelerator="Ctrl+K")
    self.edit_menu.add_command(label="Uncomment block", command=self._on_unclomment_block, accelerator="Ctrl+Shift+K")
    self.menu.add_cascade(label="Edit", menu=self.edit_menu)

    self.query_menu = Menu(self.menu, tearoff=0)
    self.query_menu.add_command(label="Run", command=self._on_run, accelerator="Ctrl+R")
    self.query_menu.add_command(label="Run selected", command=self._on_partial_run, accelerator="Ctrl+Shift+R")
    self.menu.add_cascade(label="Query", menu=self.query_menu)

    # Top toolbar ##############################################################
    self.toolbar = PanedWindow(self, orient=HORIZONTAL)
    self.toolbar.grid(row=0, column=0, sticky=N+E+S+W)

    self.str_db = StringVar()
    self.str_db.set(databases[0])
    self.combo_db = Combobox(self.toolbar, textvariable=self.str_db,
        values=databases, width=14)

    self.cb_limit_var = IntVar()
    self.cb_limit = Checkbutton(self.toolbar, var=self.cb_limit_var,
        onvalue=1, offvalue=0, text="Limit")
    self.cb_limit_var.set(1)

    self.rb_sql_var = StringVar()
    self.rb_sql_sys = Radiobutton(self.toolbar, text="DB2 /", var=self.rb_sql_var,
        value='*SYS', width=5, style='Toolbutton', command=self._on_rb_delimiter)
    self.rb_sql_sql = Radiobutton(self.toolbar, text="SQL .", var=self.rb_sql_var,
        value='*SQL', width=5, style='Toolbutton', command=self._on_rb_delimiter)
    self.rb_sql_var.set('*SQL')

    self.s_count_var = StringVar()
    self.s_count_var.set(100)
    self.s_count = Spinbox(self.toolbar, textvariable=self.s_count_var,
        from_=1, to=500, width=5)

    # Database selector
    self.toolbar.add(self.combo_db)

    # Sql delimiter style.
    self.toolbar.add(self.rb_sql_sys)
    self.toolbar.add(self.rb_sql_sql)

    # Rows limit counter.
    self.toolbar.add(self.cb_limit)
    self.toolbar.add(Label(self.toolbar, text="Count"))
    self.toolbar.add(self.s_count)

    # Empty frame as spacer.
    self.toolbar.add(Frame(self.toolbar))

    # Query  control ##########################################################
    self.txtwnd = PanedWindow(self, orient=VERTICAL)
    self.txtwnd.grid(row=1, column=0, sticky=N+E+S+W)

    frame_q = Frame(self.txtwnd)
    frame_q.columnconfigure(0, weight=1)
    frame_q.rowconfigure(0, weight=1)
    self.txtwnd.add(frame_q, weight=10)

    self.xs_q = Scrollbar(frame_q, orient=HORIZONTAL)
    self.xs_q.grid(row=1, column=0, sticky=E+W+N)
    self.ys_q = Scrollbar(frame_q, orient=VERTICAL)
    self.ys_q.grid(row=0, column=1,sticky=N+S+W)
    self.t_q = Text(frame_q,
        font=self.normal_font,
        background=colorscheme.base3,
        foreground=colorscheme.base01,
        selectbackground=colorscheme.base03,
        xscrollcommand=self.xs_q.set,
        yscrollcommand=self.ys_q.set,
        wrap=NONE,
        undo=True)

    self.t_q.grid(row=0, column=0, sticky=N+E+S+W)
    self.xs_q['command'] = self.t_q.xview
    self.ys_q['command'] = self.t_q.yview

    # Output control ##########################################################
    frame_out = Frame(self.txtwnd)
    frame_out.columnconfigure(0, weight=1)
    frame_out.rowconfigure(0, weight=1)
    self.txtwnd.add(frame_out, weight=1)

    self.xs_out = Scrollbar(frame_out, orient=HORIZONTAL)
    self.xs_out.grid(row=1, column=0, sticky=E+W+N)
    self.ys_out = Scrollbar(frame_out, orient=VERTICAL)
    self.ys_out.grid(row=0, column=1,sticky=N+S+W)
    self.t_out = Text(frame_out, font=self.normal_font,
        xscrollcommand=self.xs_out.set,
        yscrollcommand=self.ys_out.set,
        height=12,
        wrap=NONE)

    self.t_out.grid(row=0, column=0, sticky=N+S+E+W)
    self.xs_out['command'] = self.t_out.xview
    self.ys_out['command'] = self.t_out.yview

    # History control
    self.b_history = Button(self, text="Browse history", width=15, command=self._on_browse_history)
    self.b_history.grid(row=2, columnspan=2, sticky=N+E+S+W)

    # Status bar ##########################################################
    sb_frame = Frame(self)
    sb_frame.grid(row=3, columnspan=2, sticky=E+W)

    self.l_query_status = Label(sb_frame, padding=(0,0,3,0), relief=GROOVE, anchor=E, width=30)
    self.l_query_status.pack(side=RIGHT)
    self.l_query_status.config(text="")

    self.l_last_query_db = Label(sb_frame, padding=(3,0,3,0), relief=GROOVE, anchor=W)
    self.l_last_query_db.pack(side=RIGHT)
    self.l_last_query_db.config(text="")
    # Buttons ##########################################################
    frame_side = Frame(self)
    frame_side.grid(row=0,column=1, rowspan=2, sticky=N)

    self.b_get = Button(frame_side, text="Get", width=15, command=self.run)
    self.b_get.grid(row=0, sticky=N)
    self.b_exit = Button(frame_side, text="Exit", width=15, command=self.quit)
    self.b_exit.grid(row=1, sticky=N)

    self.b_upper = Button(frame_side, text="To upper", width=15, command=None)
    self.b_upper.grid(row=3, sticky=N)
    self.b_reformat = Button(frame_side, text="Reformat", width=15, command=None)
    self.b_reformat.grid(row=4, sticky=N)

  def run(self, query):
    queries = query.strip().split(';')

    limit = self.cb_limit_var.get() == 1

    try:
      limit_to = int(self.s_count_var.get())
    except ValueError:
      limit_to = 1
      self.s_count_var.set(1)

    if limit_to <= 0:
      limit_to = 1
      self.s_count_var.set(1)

    self.t_out.delete(1.0, END)
    total_time = 0.0
    total_rows = 0
    
    alter_re = re.compile('(alter|drop|update|insert)\ ') # TODO add \n and test this, move method

    for q in queries:
      if not q:
        continue
      if limit and not alter_re.match(q):
        q += " FETCH FIRST %d ROWS ONLY" % limit_to

      try:
        result = self._sql_query.get_rows(database=self.str_db.get(), query=q)
      except Exception as ex:
        self.t_out.insert(INSERT, ex.args[0] + '\n')
        continue

      total_time += result['time']
      total_rows += result['rowcount']
      self.t_out.insert(INSERT, get_readable(result['rows']))
      self.t_out.insert(INSERT, "Rows %d\t\ttime %.4f\n\n"
          % (result['rowcount'], result['time']))

    # Total details
    self.l_query_status.config(text="Total rows %d; Time %.4fs"
        % (total_rows, total_time))
    self.l_last_query_db.config(text=self.str_db.get())

def init_tk():
  app = GuiApp()
  app.mainloop()

def main():
  init_tk()

if __name__ == '__main__':
  main()

