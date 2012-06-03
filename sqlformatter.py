
import re

 
new_line_keywords = ['select', 'from', 'where', 'update', 'insert', 'having', 'group', 'order', 'union']

def printsql(sql):
  re_newliners = re.compile('(' + '|'.join(new_line_keywords) + ')$', re.IGNORECASE)
  splited = sql.split()
  out = ''
  for word in splited:
    if re_newliners.match(word):
      out += '\n'
    out += word + ' '
  return out

