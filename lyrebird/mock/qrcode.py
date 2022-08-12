import io
import qrcode
import binascii
from lyrebird import utils

def get_qrcode_img(link):
    formated_link = utils.render(link)

    img = qrcode.make(formated_link, border=1)
    img_buffer = io.BytesIO()
    img.save(img_buffer, 'png')
    img_data_bytes = img_buffer.getvalue()
    img_buffer.close()

    img_data = (b"data:image/png;base64," + binascii.b2a_base64(img_data_bytes)).decode()
    return img_data
