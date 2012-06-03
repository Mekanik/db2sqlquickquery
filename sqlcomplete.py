#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from tkinter import *
from tkinter.ttk import *

import pickle

import sqlcompletewnd

COMPLETE_CACHE_FILE = 'complete.pck'

def _deserialize(file_name):
  with open(file_name, 'rb') as f:
    data = pickle.load(f)
  return data

def _serialize(obj, file_name):
  with open(file_name, 'wb') as f:
    pickle.dump(obj, f, pickle.HIGHEST_PROTOCOL)

class Autocomplete:
  def __init__(self, text_widget):
    self._text = text_widget
    #self._text.bind("<Control-space>", self._show_completion)
    self._text.bind("<<show-completion>>", self._do_complete)

    self._wnd = sqlcompletewnd.CompleteWindow(self._text)

  def _do_complete(self, _):
    lastchar = self._text.get("insert-1c")
    
    print("[" + lastchar + "]")

    cursor = self._text.index("insert")
    curline = self._text.get("insert linestart", "insert")
    query = self._text.get(1.0, END)

    self._wnd.show_window(lastchar, self._tables)

  def generate_completion_list(self, sqlquery):
    self.load_completion_list(COMPLETE_CACHE_FILE)
    return

    tbl_dic = {}
    db = 'LOG_TEST'
    query = (" SELECT DBILFL AS COLUMN_NAME, DBILFI AS TABLE_NAME, DBITYP AS DATA_TYPE,"
      " DBIFLN AS LENGTH, DBINUL AS IS_NULLABLE FROM QADBIFLD WHERE DBIREL = 'Y' AND DBIATR <> 'IX'"
      " AND DBILIB = '%s' ORDER BY TABLE_NAME") % db

    rows = sqlquery.get_rows('QSYS', query)

    for row in rows:
      if db not in tbl_dic:
        tbl_dic[db] = {}
      table_name = row.TABLE_NAME.strip()
      if table_name not in tbl_dic[db]:
        tbl_dic[db][table_name] = []
      tbl_dic[db][table_name].append(
          (row.COLUMN_NAME.strip(), row.DATA_TYPE.strip(), row.LENGTH, True if row.IS_NULLABLE.strip() == 'Y' else False) )

    self._tables = tbl_dic
    _serialize(self._tables, COMPLETE_CACHE_FILE)
    
  def load_completion_list(self, file_name):
    self._tables = _deserialize(file_name)

