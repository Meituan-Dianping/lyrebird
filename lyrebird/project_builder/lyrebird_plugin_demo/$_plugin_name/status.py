from lyrebird.plugins import ClickableStatusText, TextMenuItem, ImageMenuItem
import qrcode
import io
import binascii


class StatusbarDemoImage(ClickableStatusText):
    def get_text(self):
        return 'Lyrebird_QRCode'

    def get_menu(self):

        img = qrcode.make("https://github.com/Meituan-Dianping/lyrebird")
        img_buffer = io.BytesIO()
        img.save(img_buffer, 'png')
        img_data_bytes = img_buffer.getvalue()
        img_buffer.close()

        img_data = (b"data:image/png;base64," + binascii.b2a_base64(img_data_bytes)).decode()
        return [ImageMenuItem(src=img_data)]

class StatusbarDemoText(ClickableStatusText):
    def get_text(self):
        return 'Lyrebird_Text'

    def get_menu(self):
        return [TextMenuItem(src="Text Status Bar")]
