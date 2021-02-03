import io
import qrcode
import binascii
from jinja2 import Template
from lyrebird.application import config

def _format_parameters(link):
    params = {
        'ip': config.get('ip'),
        'port': config.get('mock.port')
    }
    link_template = Template(link)
    formated_link = link_template.render(params)
    return formated_link

def get_qrcode_img(link):
    formated_link = _format_parameters(link)

    img = qrcode.make(formated_link, border=1)
    img_buffer = io.BytesIO()
    img.save(img_buffer, 'png')
    img_data_bytes = img_buffer.getvalue()
    img_buffer.close()

    img_data = (b"data:image/png;base64," + binascii.b2a_base64(img_data_bytes)).decode()
    return img_data
