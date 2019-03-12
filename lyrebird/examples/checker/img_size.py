"""
checker example

steps:
- ignore unexepcted object
- prepare useful info
- check data

Info used in channel flow
├── name
└─┬ flow
  ├── size
  ├─┬ request
  │ └── url
  └─┬ response
    └─┬ headers
      └── Content-Type

"""


from lyrebird import CustomEventReceiver
from decimal import Decimal


# init event receiver instance
event = CustomEventReceiver()

# THRESHOLD_IMG_SIZE: image size limitation
THRESHOLD_IMG_SIZE = 500

@event('flow')
def img_size(msg):

    # 1.ignore unexepcted object
    if ignore_check(msg):
        return

    # 2.prepare useful info
    img_size = int(msg['flow']['size'])
    img_size = Decimal(img_size / 1024).quantize(Decimal('0.0'))

    # 3.check data
    if img_size > THRESHOLD_IMG_SIZE:
        img_url = msg['flow']['request']['url']
        img_url = img_url[img_url.rfind('//') + 2:]

        description = 'Image size exceeded!\n'
        description += f'Expecte: {THRESHOLD_IMG_SIZE}KB\n'
        description += f'Actual: {img_size}KB\n'
        event.issue(f'Image size exceeded',
                    {
                        "summary": "[checker][img_size]",
                        "description": description
                    })

def ignore_check(msg):
    if msg['name'] != 'server.response':
        return True
    if 'image' not in msg['flow']['response']['headers']['Content-Type']:
        return True
    return False
