from pynput.keyboard import Controller, Key
keyboard = Controller()

# Type user_id
keyboard.type("kjhkjjnh")
keyboard.press(Key.enter)
keyboard.release(Key.enter)