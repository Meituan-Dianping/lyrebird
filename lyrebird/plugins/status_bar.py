import uuid


class ClickableStatusText:
    """
    Plugin status text component

    On main UI rendering , Lyrebird will call getText function and display its return on footbar.
    If user click that text， Lyrebird will call getMenu function for loading menu items.
    """

    def __init__(self):
        self.id = str(uuid.uuid4())
        if not hasattr(self, 'name'):
            self.name = self.id
        if not hasattr(self, 'rank'):
            self.rank = 0

    def get_text(self):
        """
        return a string
        """
        pass

    def get_menu(self):
        """
        return a list of MenuItem

        e.g.
        return [TextMenuItem('Hello'), TextMenuItem('World')]
        """
        pass


class MenuItem:

    def __init__(self, src):
        self.id = str(uuid.uuid4())
        self.type = self.__class__.__name__
        self.src = src

    def json(self):
        return {'id': self.id, 'type': self.type, 'src': self.src}


class ImageMenuItem(MenuItem):
    """
    The src argument support URL and base64 data string
    """
    pass


class TextMenuItem(MenuItem):
    """
    src: text
    """
    pass


class LinkMenuItem(MenuItem):
    """
    src: selector
    """
    pass
