import uuid
from lyrebird.db.database_server import JSONFormat


PLACEMENT_BOTTOM_LEFT = 'bottom_left'
PLACEMENT_BOTTOM_RIGHT = 'bottom_right'
PLACEMENT_TOP_RIGHT = 'top_right'

class ClickableStatusText:
    """
    Plugin status text component

    On main UI rendering , Lyrebird will call getText function and display its return on footbar.
    If user click that text， Lyrebird will call getMenu function for loading menu items.

    Attributes:
        - prepend_icon use Material Design icon
        - placement: accept PLACEMENT_BOTTOM_LEFT, PLACEMENT_BOTTOM_RIGHT and PLACEMENT_TOP_RIGHT
        - rank: The larger the data, the closer to the target placement
        - icon: Display in QRCode
    """

    def __init__(self):
        self.id = str(uuid.uuid4())
        if not hasattr(self, 'name'):
            self.name = self.id
        if not hasattr(self, 'rank'):
            self.rank = 0
        if not hasattr(self, 'icon'):
            self.icon = ''
        if not hasattr(self, 'prepend_icon'):
            self.prepend_icon = None
        if not hasattr(self, 'placement'):
            self.placement = PLACEMENT_BOTTOM_LEFT

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

    def json(self):
        info = JSONFormat.json(self)
        info.update({
            'text': self.get_text()
        })
        return info


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
    src: link
    """
    pass


class SelectItem(MenuItem):
    """
    src: selector
    [{
        'selectedIndex': 0,
        # Has no selectedIndex, set -1
        'allItem': [{
            'text': '', 
            'api': ''
        }]
    }]
    """
    pass
