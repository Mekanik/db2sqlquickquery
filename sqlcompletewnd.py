#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from tkinter import *
from tkinter.ttk import *

class CompleteWindow:

  def __init__(self, text):
    self._text = text
    self._wnd = None

  def show_window(self, data, tables):
    if self.is_active():
      self.hide_window()

    self._wnd = Toplevel(self._text)
    self._wnd.wm_geometry("+10000+10000")
    self._wnd.wm_overrideredirect(1)
    self.scrollbar = scrollbar = Scrollbar(self._wnd, orient=VERTICAL)
    self.listbox = listbox = Listbox(self._wnd, yscrollcommand=scrollbar.set,
        exportselection=False, bg="white")


    self.origselforeground = listbox.cget("selectforeground")
    self.origselbackground = listbox.cget("selectbackground")
    scrollbar.config(command=listbox.yview)
    scrollbar.pack(side=RIGHT, fill=Y)
    listbox.pack(side=LEFT, fill=BOTH, expand=True)

    acw = self._wnd
    text = self._text
    listbox = self.listbox
    for item in tables['LOG_TEST'].keys():
      listbox.insert(END, item)

    self.startindex = self._text.index("insert-1c") 
    text.see(self.startindex)
    x, y, cx, cy = text.bbox(self.startindex)

    acw_width, acw_height = acw.winfo_width(), acw.winfo_height()
    text_width, text_height = text.winfo_width(), text.winfo_height()
    new_x = text.winfo_rootx() + min(x, max(0, text_width - acw_width))
    new_y = text.winfo_rooty() + y
    if (text_height - (y + cy) >= acw_height # enough height below
        or y < acw_height): # not enough height above
      # place acw below current line
        new_y += cy
    else:
      # place acw above current line
        new_y -= acw_height
    acw.wm_geometry("+%d+%d" % (new_x, new_y))

    # bind events
    self._wnd.bind(KEYPRESS_VIRTUAL_EVENT_NAME, self.keypress_event)


  def is_active(self):
    return self._wnd is not None

  def hide_window(self):
    if not self.is_active():
      return

    # unbind events
    self._wnd.event_delete(KEYRELEASE_VIRTUAL_EVENT_NAME, KEYRELEASE_SEQUENCE)

    self.scrollbar.destroy()
    self.scrollbar = None
    self.listbox.destroy()
    self.listbox = None
    self._wnd.destroy()
    self._wnd = None

  def keypress_event(self, event):
    if not self.is_active():
      return

    keysym = event.keysym
    if keysym == "Return":
      self.hide_window()
      return

    if any(s in keysym for s in ("Shift", "Control", "Alt",
                                   "Meta", "Command", "Option")):
            # A modifier key, so ignore
      return

    if len(keysym) == 1:
      # add to widget to saved position (call position) this symbol
      # search in list
      print(keysym)

    self.hide_window()
    return
