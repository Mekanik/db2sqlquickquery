#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from tkinter import *
from _tkinter import TclError
import sqlformatter

SPACES_IN_TAB = 4
BEGIN_COMMENT = '--'

def _get_col(index):
  return int(index.split('.')[1])

def _get_row(index):
  return int(index.split('.')[0])

def _get_insert(text):
  insert_index = text.index('insert').split('.')
  return (int(insert_index[0]), int(insert_index[1]))

class SqlEditor:
  def __init__(self, text_widget):
    self._text = text_widget
    self._text.bind("<Key-Tab>", self._on_key_tab)
    self._text.bind("<Control-Key-Tab>", self._on_key_control_tab)
    self._text.bind("<Shift-Key-Tab>", self._on_key_control_tab)
    self._text.bind("<Key-Return>", self._on_key_return)
    self._text.bind("<Key-KP_Enter>", self._on_key_return)
    self._text.bind("<Key-BackSpace>", self._on_key_backspace)

    self._text.bind("<<comment-block>>", self._comment_block)
    self._text.bind("<<uncomment-block>>", self._uncomment_block)
    self._text.bind("<<to-upper>>", self._to_upper)
    self._text.bind("<<format>>", self._format)

# Key-KP_Enter
# Key-BackSpace

  def _to_upper(self, _):
    content = self._text.get(1.0, END).upper()
    self._text.delete(1.0, END)
    self._text.insert(INSERT, content)
    return "break"

  def _format(self, _):
    content = self._text.get(1.0, END)
    #parsed = sqlparse.parse(content)
    #parsed = sqlparse.format(content, reindent=True, keyword_case='upper')
    parsed = sqlformatter.printsql(content)
    self._text.delete(1.0, END)
    self._text.insert(INSERT, parsed)
    return "break"


  def _comment_block(self, _):
    text = self._text

    if text.tag_ranges("sel"):
      first, last = self._get_selection_indices()
      line_first = _get_row(first)
      line_last = _get_row(last)
    else:
      line_first = line_last =  _get_row(text.index('insert'))

    for i in range(line_first, line_last + 1):
      text.insert("%d.0" % i, BEGIN_COMMENT)
    
    return "break"


  def _uncomment_block(self, _):
    text = self._text

    if text.tag_ranges("sel"):
      first, last = self._get_selection_indices()
      line_first = _get_row(first)
      line_last = _get_row(last)
    else:
      line_first = line_last =  _get_row(text.index('insert'))

    for i in range(line_first, line_last + 1):
      line_prefix = text.get("%s.0" % i, "%d.%d" % (i, len(BEGIN_COMMENT)))
      if line_prefix == BEGIN_COMMENT:
        text.delete("%d.0" % i, "%d.%d" % (i, len(BEGIN_COMMENT)))
    
    return "break"

  def _get_selection_indices(self):
    try:
      first = self._text.index("sel.first")
      last = self._text.index("sel.last")
      return first, last
    except TclError:
      return None, None
  
  def _on_key_backspace(self, _):
    text = self._text

    if text.tag_ranges("sel"):
      return

    insert_index = _get_insert(text)
    
    line_before_i = text.get("%d.0" % insert_index[0],
        "%d.%d" % (insert_index[0], insert_index[1]))
    # If we have some meaning symbols before cursor do 1 backspace.
    if len(line_before_i.strip()) != 0:
      return

    symbols_to_del = insert_index[1] % SPACES_IN_TAB
    if symbols_to_del == 0:
      symbols_to_del = SPACES_IN_TAB

    text.delete("%d.%d" % (insert_index[0], insert_index[1] - symbols_to_del),
        "%d.%d" % (insert_index[0], insert_index[1]))
    return "break"

  def _on_key_tab(self, _):
    text = self._text

    # If text selected, indent block.
    if text.tag_ranges("sel"):
      first, last = self._get_selection_indices()
      line_first = _get_row(first)
      line_last = _get_row(last)

      for i in range(line_first, line_last + 1):
        text.insert("%d.0" % i, ' ' * SPACES_IN_TAB)
      return "break"

    col_i = _get_col(text.index('insert'))

    pad = ' ' * (SPACES_IN_TAB - col_i % SPACES_IN_TAB)
    text.insert("insert", pad)
    text.see("insert")
    return "break"

  def _on_key_control_tab(self, _):
    text = self._text
    if text.tag_ranges("sel"):
      first, last = self._get_selection_indices()
      line_first = _get_row(first)
      line_last = _get_row(last)
    else:
      line_first = line_last =  _get_row(text.index('insert'))

    for i in range(line_first, line_last + 1):
      line = text.get("%d.0" % i, "%d.end" % i)
      stripped_len = len(line.lstrip())
      if len(line) - stripped_len >= SPACES_IN_TAB:
        text.delete("%d.0" % i, "%d.%d" % (i, SPACES_IN_TAB))

    return "break"

  def _on_key_return(self, _):
    text = self._text

    # If some text selected, pass.
    if text.tag_ranges("sel"):
      return

    # Insert tabs, like in prec line. If line was empty, start with 0.
    line_i = _get_row(text.index('insert'))
    line = text.get("%s.0" % line_i, "%s.end" % line_i)
    stripped_len = len(line.lstrip())
    offset = len(line) - stripped_len if stripped_len > 0 else 0
    text.insert("insert", '\n' + ' ' * offset)
    text.see("insert")
    return "break"
