#!/usr/bin/env python3
# -*- coding: utf-8 -*-


import re

from WidgetRedirector import * 
import solcolors as colorscheme

sql_keywords = ['as', 'by', 'create', 'cross', 'delete', 'drop',
    'fetch', 'for', 'from', 'group', 'inner', 'insert', 'into',
    'join', 'order',
    'outer', 'row', 'rows', 'select', 'set', 'update', 'union', 'valueswhere', 
    'where']
 
sql_types = ['bigint', 'binary', 'bit', 'char', 'date', 'datetime',
    'decimal', 'decimalsmallmoney', 'double', 'float', 'image',
    'int', 'integer', 'long', 'money', 'numeric', 'real', 'smalldate',
    'smallint', 'text', 'time', 'timestamp', 'tinyint', 'uniqueidentifier',
    'unsigned', 'varbinary', 'varchar', 'xml']

sql_operators = ['abs', 'absval', 'acos', 'all',
    'and', 'any', 'ascii', 'asin', 'atan2', 'avg', 'between', 'case',
    'ceil', 'ceiling', 'chr', 'coalesce', 'concat', 'corr', 'correlation',
    'cos', 'cot', 'count', 'count_big', 'covar', 'covariance', 'ctan',
    'day', 'dayname', 'dayofweek', 'dayofweek', 'dayofyear', 'days',
    'decrypt_bin', 'decrypt_char', 'degrees', 'deref', 'desc', 'difference',
    'digits', 'distinct', 'encrypt', 'escape', 'exists', 'exp', 'first', 'floor',
    'gethint', 'hex', 'hour', 'if', 'ifnull', 'in', 'intersect', 'is', 
    'julian_day', 'lcase', 'left', 'length', 'like', 'ln', 'locate', 'log',
    'log10', 'lower', 'ltrim', 'max', 'microsecond', 'midnight_seconds',
    'min', 'minus', 'minute', 'mod', 'month', 'monthname', 'multiply_alt',
    'nodenumber', 'not', 'nullif', 'or', 'partition', 'posstr', 'power',
    'prior', 'quarter', 'radians', 'raise_error', 'rand', 'replace',
    'right', 'round', 'rtrim', 'second', 'sign', 'sin', 'some', 'soundex',
    'space', 'sqrt', 'substr', 'sum', 'switch', 'tan', 'then', 'translate',
    'trunc', 'truncate', 'ucase', 'upper', 'week', 'week_iso',
    'year', '\|\|']


class SqlSyntaxHighlight:
  def __init__(self, text_widget, normal_font, bold_font, italic_font):
    self.normal_font = normal_font
    self.italic_font = italic_font
    self.bold_font = bold_font
    
    self._text = text_widget
    self.redir = WidgetRedirector(self._text)

    self.insert = self.redir.register("insert", self.on_insert)
    self.delete = self.redir.register("delete", self.on_delete)
    self._apply_tags()
 
    self._re_keyword = re.compile('(' + '|'.join(sql_keywords) + ')$')
    self._re_type = re.compile('(' + '|'.join(sql_types) + ')$')
    self._re_operator = re.compile('(' + '|'.join(sql_operators) + ')$')

  def on_insert(self, index, chars, tags=None):
#    print("on_insert (index=%s, chars=%s, tags=%s)" % (str(index), str(chars), str(tags)) )
    self.insert(index, chars, tags)
    self.syntax_highlight()

  def on_delete(self, index1, index2=None):
#    print("on_delete (index1=%s, index2=%s)" % (str(index1), str(index2)))
    self.delete(index1, index2)

  def syntax_highlight(self):
    index = self._text.search(r'\s', "insert", backwards=True, regexp=True)
    if index == "":
      index ="1.0"
    else:
      index = self._text.index("%s+1c" % index)

    word = self._text.get(index, "insert").lower()
    word_len = len(word)
    if word_len <= 0:
      return

    txt_pattern = "%s+%dc" % (index, word_len)

    # Variables
    if word[0] == ':' or word == 'null':
      self._text.tag_add("variable", index, txt_pattern)
    else:
      self._text.tag_remove("variable", index, txt_pattern)

    # Digits
    if word.isdigit():
      self._text.tag_add("digit", index, txt_pattern)
    else:
      self._text.tag_remove("digit", index, txt_pattern)
    
    # Keywords
    if self._re_keyword.match(word):
      self._text.tag_add("keyword", index, txt_pattern)
    else:
      self._text.tag_remove("keyword", index, txt_pattern)
    
    # Types
    if self._re_type.match(word):
      self._text.tag_add("type", index, txt_pattern)
    else:
      self._text.tag_remove("type", index, txt_pattern)

    # Operators
    if self._re_operator.match(word):
      self._text.tag_add("operator", index, txt_pattern)
    else:
      self._text.tag_remove("operator", index, txt_pattern)


  def _apply_tags(self):
    self._text.tag_config("keyword", foreground=colorscheme.blue, font=self.bold_font)
    self._text.tag_config("operator", foreground=colorscheme.cyan)
    self._text.tag_config("variable", foreground=colorscheme.red)
    self._text.tag_config("type", foreground=colorscheme.cyan)
    self._text.tag_config("string", foreground=colorscheme.orange)
    self._text.tag_config("digit", foreground=colorscheme.orange)
    self._text.tag_config("comment", foreground=colorscheme.base1, font=self.italic_font)

