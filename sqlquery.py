#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import pyodbc
import time

class SqlQuery:
  _delimiters = { '*SQL' : 0, '*SYS' : 1 }

  def __init__(self, sys_name, user, pwd, sql_delimiter = '*SQL'):
    self._sys_name = sys_name
    self._user = user
    self._pwd = pwd #base64.b64decode(pwd.encode('ascii')).decode('ascii')
    self.set_sql_delimiter(sql_delimiter)

  def _make_answer_dict(self, rows, time, rowcount):
    return { 'rows' : rows, 'time' : time, 'rowcount' : rowcount }
    
  def _get_connection_string(self, database):
    """ Returns AS400 DB2 ODBC connection string. """
    return ('ODBC;DNS=;DRIVER={Client Access ODBC Driver (32-bit)};'
      'SYSTEM=%s;CMT=0;DBQ=%s;NAM=%d;DFT=5;DSP=1;TFT=0;TSP=0;DEC=0;'
      'XDYNAMIC=0;UID=%s;PWD=%s;RECBLOCK=2;BLOCKSIZE=512;SCROLLABLE=0;'
      'TRANSLATE=0;LAZYCLOSE=0;LIBVIEW=0;REMARKS=0;CONNTYPE=0;SORTTYPE=2;'
      'SORTWEIGHT=1;LANGUAGEID=ENG;PREFETCH=0;DFTPKGLIB=' 
      % (self._sys_name, database, self._delimiters[self._sql_delimiter], self._user, self._pwd))

  def set_sql_delimiter(self, sql_delimiter):
    if sql_delimiter not in self._delimiters.keys():
      raise Exception('Wrong SQL delimiter type', sql_delimiter)

    self._sql_delimiter = sql_delimiter

  def get_rows(self, database, query):
    print("SQL Query: " + database + " : " + query) # TODO drop
    connection = None
    try:
      connection = pyodbc.connect(self._get_connection_string(database))
      cursor = connection.cursor()
      time_start = time.clock()
      cursor.execute(query)
    except (pyodbc.ProgrammingError,
        pyodbc.NotSupportedError,
        pyodbc.DataError,
        pyodbc.IntegrityError,
        pyodbc.DatabaseError,
        pyodbc.Error) as ex:
      if connection:
        connection.close()
      error_text = ex.args[1]
      error_text = error_text.replace('\ufffd', '_')
      msg = "Error: %s (%s)" % (ex.args[0], error_text)
      print(msg)
      raise Exception(msg)

    fetched_rows = cursor.fetchall()

    time_end = time.clock()
    answer = self._make_answer_dict(
        rows = fetched_rows,
        time = time_end - time_start,
        rowcount = cursor.rowcount if cursor.rowcount >= 0 else len(fetched_rows))

    connection.close()
    return answer
