import uuid
from lyrebird.utils import JSONFormat


PLACEMENT_BOTTOM_LEFT = 'bottom_left'
PLACEMENT_BOTTOM_RIGHT = 'bottom_right'
PLACEMENT_TOP_RIGHT = 'top_right'


class PlainText:
    """
    Status plain text component

    On main UI rendering , Lyrebird will call getText function and display its return on footbar or appbar.

    Attributes:
        - prepend_icon use Material Design icon
        - placement: accept PLACEMENT_BOTTOM_LEFT, PLACEMENT_BOTTOM_RIGHT and PLACEMENT_TOP_RIGHT
        - rank: The larger the data, the closer to the target placement
        - icon: Display in QRCode
    """
    rank = 0
    prepend_icon = None
    placement = PLACEMENT_BOTTOM_LEFT

    def __init__(self):
        self.display = True
        self.id = str(uuid.uuid4())
        if not hasattr(self, 'name'):
            self.name = self.id

    @property
    def type(self):
        return self.__class__.__base__.__name__

    def get_text(self):
        """
        return a string
        """
        pass


class ClickableStatusText:
    """
    Plugin status text-tooltip component

    On main UI rendering , Lyrebird will call getText function and display its return on footbar or appbar.
    If user click that text， Lyrebird will call getMenu function for loading menu items.

    Attributes:
        - prepend_icon use Material Design icon
        - placement: accept PLACEMENT_BOTTOM_LEFT, PLACEMENT_BOTTOM_RIGHT and PLACEMENT_TOP_RIGHT
        - rank: The larger the data, the closer to the target placement
        - icon: Display in QRCode
    """

    rank = 0
    prepend_icon = None
    placement = PLACEMENT_BOTTOM_LEFT

    def __init__(self):
        self.id = str(uuid.uuid4())
        if not hasattr(self, 'name'):
            self.name = self.id

    @property
    def type(self):
        return self.__class__.__base__.__name__

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

    def get_detail(self):
        return [menu_item.json() for menu_item in self.get_menu()]

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


class Selector:
    """
    Plugin status select component

    On main UI rendering , Lyrebird will call getMenu function and display its return on footbar or appbar.

    Attributes:
        - type: 
        - prepend_icon: use Material Design icon
        - placement: accept PLACEMENT_BOTTOM_LEFT, PLACEMENT_BOTTOM_RIGHT and PLACEMENT_TOP_RIGHT
        - rank: The larger the data, the closer to the target placement
    """

    rank = 0
    prepend_icon = None
    placement = PLACEMENT_BOTTOM_LEFT

    def __init__(self):
        self.id = str(uuid.uuid4())
        if not hasattr(self, 'name'):
            self.name = self.id

    @property
    def type(self):
        return self.__class__.__base__.__name__

    def get_menu(self):
        """
        return a dict
        {
            'selectedIndex': selected_index,
            'selected': selected_api,
            'allItem': [{
                'text': 'Display text',
                'api': ''
            }]
        }
        """
        pass

    def get_detail(self):
        return self.get_menu()

    def json(self):
        info = JSONFormat.json(self)
        info.update({
            'src': self.get_menu()
        })
        return info
