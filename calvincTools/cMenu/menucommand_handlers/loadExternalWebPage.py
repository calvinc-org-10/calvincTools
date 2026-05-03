from PySide6.QtWidgets import QWidget


import webbrowser


class loadExternalWebPage():
    def __init__(self, url:str|None, parent:QWidget|None = None):
        if url:
            self.reloadPage(url)
    # __init__

    def reloadPage(self, url:str):
        webbrowser.open_new_tab(url)
    # reloadPage

    def end_of_class(self):
        """ place this after the all methods and comments in the class, to avoid accidentally leaving out a method or comment when copying/pasting or refactoring code"""
        pass