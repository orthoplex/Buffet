from curses import *
import re

class Menu:
    def __init__(self, scr):
        self.scr = scr
        self.items = []
        self.commit = False
        self.finished = False
        self.height, self.width = self.scr.getmaxyx()

        self.toprow = 0
        self.bottomrow = 0

    def save(self):
        if self.allValid():
            self.commit = True
            self.finished = True

    def cancel(self):
        self.commit = False
        self.finished = True

    def allValid(self):
        for item in self.items:
            if not item.isValid():
                return False
        return True

    def run(self):
        self.commit = False
        self.finished = False
        cursor = 0
        while not self.finished:
            self.show(cursor)
            key = self.scr.getch()
            if not self.getCurrentItem(cursor).active:
                if key == KEY_DOWN:
                    cursor = min(cursor + 1, self.getSize() - 1)
                elif key == KEY_UP:
                    cursor = max(cursor - 1, 0)
                elif key == 27:
                    self.cancel()
                else:
                    self.getCurrentItem(cursor).handleKey(key)
            else:
                self.getCurrentItem(cursor).handleKey(key)

            if cursor > self.bottomrow - 1:
                self.scrollDown()
            elif cursor < self.toprow:
                self.scrollUp()

        values = [item.getValue() for item in self.items]

        return {"commit": self.commit, "values": values}

    def getSize(self):
        return len(self.items)

    def getCurrentItem(self, cursor):
        return self.items[cursor]

    def show(self, cursor = None):
        self.scr.clear()
        for row, item in enumerate(self.items):
            if row in range(self.toprow, self.bottomrow):
                item.show(self.scr, [row - self.toprow, 0], (row == cursor))

    def addItem(self, item):
        self.items.append(item)
        self.bottomrow = min(self.getSize(), self.height)

    def scrollDown(self):
        if self.bottomrow < self.getSize():
            self.bottomrow += 1
            self.toprow += 1

    def scrollUp(self):
        if self.toprow > 0:
            self.bottomrow -= 1
            self.toprow -= 1

class MenuItem:
    def __init__(self, name, value = None):
        self.name = name
        self.active = False

    def handleKey(self, key):
        pass

    def getText(self):
        return self.name

    def show(self, scr, pos, highlight):
        y, x = pos
        mode = {
            True: A_REVERSE,
            False: A_NORMAL
        }[highlight]

        scr.addstr(y, x, self.getText(), mode)

    def isValid(self):
        return True

class InputItem(MenuItem):
    def __init__(self, name, value = None):
        MenuItem.__init__(self, name)
        self.value = value

    def show(self, scr, pos, selected):
        y, x = pos
        highlight = {
            True: A_REVERSE,
            False: A_NORMAL
        }[selected]

        valid = {
            True: A_NORMAL,
            False: A_REVERSE
        }[self.isValid()]

        scr.addstr(y, x, self.name, highlight)
        scr.addstr(y, x + 10, self.getText(), valid)

    def getValue(self):
        return self.value

    def getText(self):
        return str(self.value)

class ToggleButton(InputItem):
    def __init__(self, name, value = False):
        InputItem.__init__(self, name, value)

    def getText(self):
        text = {
            True: "On",
            False: "Off"
        }[self.value]
        return text

    def handleKey(self, key):
        if key == KEY_LEFT:
            self.toggle()
        elif key == KEY_RIGHT:
            self.toggle()

    def toggle(self):
        self.value = not self.value

class TextBox(InputItem):
    def __init__(self, name, length = 10, value = "", regex = ""):
        InputItem.__init__(self, name, value)
        self.name = name
        self.length = length
        self.changed = False
        self.regex = regex

    def handleKey(self, key):
        if not self.changed:
            self.value = ""
            self.changed = True
        if len(self.getText()) < self.length:
            if re.match(r"[a-zA-Z0-9]", chr(key)):
                self.value += chr(key)
        if key == 8:
            self.value = self.value[:-1]
        elif key == KEY_DC:
            self.value = ""

    def isValid(self):
        if re.match(self.regex, self.value):
            return True
        return False

class PasswordBox(TextBox):
    def __init__(self, name, length = 10, regex = ""):
        TextBox.__init__(self, name, length, "", regex)

    def getText(self):
        return "*" * len(self.value)

class Selection(InputItem):
    def __init__(self, name, options, value = 0):
        InputItem.__init__(self, name, value)
        self.options = options

    def getText(self):
        return self.options[self.value]

    def handleKey(self, key):
        if key == KEY_LEFT:
            self.value -= 1
            self.value %= self.getSize()
        elif key == KEY_RIGHT:
            self.value += 1
            self.value %= self.getSize()

    def getSize(self):
        return len(self.options)

class Button(MenuItem):
    def __init__(self, name, callback):
        MenuItem.__init__(self, name)
        self.name = name
        self.callback = callback

    def getValue(self):
        return None

    def getText(self):
        return "[%s]" % self.name

    def handleKey(self, key):
        if key == 10:
            self.callback()

class NumberRange(InputItem):
    def __init__(self, name, value = 5, minimum = 0, maximum = 10):
        InputItem.__init__(self, name, value)
        self.minimum = minimum
        self.maximum = maximum

    def handleKey(self, key):
        if key == KEY_LEFT:
            self.value = max(self.value - 1, self.minimum)
        elif key == KEY_RIGHT:
            self.value = min(self.value + 1, self.maximum)
