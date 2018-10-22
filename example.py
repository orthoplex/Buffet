from curses import *
import buffet

if __name__ == "__main__":
    stdscr = initscr()
    stdscr.keypad(True)

    noecho()
    cbreak()
    curs_set(0)

    win = newwin(7, 30, 2, 10)
    win.keypad(True)

    my_menu = buffet.Menu(win)
    player1 = buffet.TextBox("Player 1", 10, "Lukas", r".{3}")
    player2 = buffet.TextBox("Player 2", 10, "Robin", r".{3}")
    player3 = buffet.TextBox("Player 3", 10, "", r"^(.{3,})?$")
    player4 = buffet.TextBox("Player 4", 10, "", r"^(.{3,})?$")
    seed = buffet.TextBox("Seed", 10, "", r"^(([1-9][0-9]*)|0)?$")
    width = buffet.NumberRange("Width", 7, 3, 10)
    height = buffet.NumberRange("Height", 6, 3, 10)
    pin = buffet.PasswordBox("PIN", 4, r"^3141$")
    saveButton = buffet.Button("Save", my_menu.save)
    cancelButton = buffet.Button("Cancel", my_menu.cancel)

    my_menu.addItem(player1)
    my_menu.addItem(player2)
    my_menu.addItem(player3)
    my_menu.addItem(player4)
    my_menu.addItem(seed)
    my_menu.addItem(width)
    my_menu.addItem(height)
    my_menu.addItem(pin)
    my_menu.addItem(saveButton)
    my_menu.addItem(cancelButton)

    print(my_menu.run())
