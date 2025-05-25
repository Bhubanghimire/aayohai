import uuid
import datetime
import jwt
# from rest_framework_simplejwt.tokens import RefreshToken
from events.models import Event
# from events.api.serializers import EventlikeSerializer
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings
from PIL import Image, ImageDraw, ImageFont
import os
import qrcode
from urllib.request import urlopen
import io
import urllib

from events.serializers import EventSerializers


def createUnique():
    a = str(uuid.uuid4().fields[-1])[:4]
    b = str(datetime.datetime.now().date())
    c = b.replace('-', '')

    d = str(datetime.datetime.now().time())
    e = d.replace(':', '')
    final = a + '-' + c + '-' + e
    final2 = final.replace('.', '')

    return final2



def send_mail_with_ticket(ticket):
    base_url = settings.HOST_URL
    attach = ticket.ticket_img.url
    url = base_url + attach
    print(attach, url)
    fd = urlopen(url)

    img_url = ticket.ticket_img.url
    html_content = render_to_string("ticket_email.html", {'title': 'Otp',
                                                                'ticket_created_at': str(
                                                                    datetime.datetime.now().date()),
                                                                'ticket_number': ticket.ticket_number,
                                                                'no_of_ticket': ticket.no_of_ticket,
                                                                'user_full_name': ticket.user.first_name,
                                                                'user_email': ticket.user.email,
                                                                'base_url': base_url,
                                                                "ticket_image": img_url,
                                                                # 'user_phone': ticket.user.mobile,
                                                                'event_rate': (
                                                                            ticket.event_price.price * ticket.no_of_ticket),
                                                                "event_title": ticket.event.title,
                                                                "event_start_time": ticket.event.start_date,
                                                                "event_end_date": ticket.event.event_date
                                                                })
    test_contend = strip_tags(html_content)
    email = EmailMultiAlternatives('Send Ticket detail', test_contend, settings.DEFAULT_FROM_EMAIL, [ticket.user.email])

    email.attach_alternative(html_content, 'text/html')
    email.send()
    return 'Done'


def CreateTicketFunction(request, ticket_number, name):
    uniqueid = uuid.uuid1()
    event = Event.objects.filter(ticket__ticket_number=ticket_number).first()
    event = EventSerializers(event).data
    # url = event["cover_image"]
    base_url = settings.HOST_URL
    attach = event["cover_image"]
    url = base_url + attach

    fd = urlopen(url)
    file = io.BytesIO(fd.read())
    try:
        image = Image.open(file)
        font_path = os.path.join(os.path.dirname(__file__), "ARIAL.TTF")
        font = ImageFont.truetype(font_path, 14)
    except Exception as e:
        return e

    draw = ImageDraw.Draw(image)
    qr = qrcode.make(ticket_number)
    qr = qr.resize((180, 200),Image.Resampling.LANCZOS)

    image.paste(qr, (40, 85))
    draw.text((45, 300), name, font=font, fill='#000000')
    path = f'media/ticket/'
    os.makedirs(path, exist_ok=True)  # Creates the directory if it doesn't exist
    image.save(f'media/ticket/{uniqueid}.png')

    image.show()

    return f'/ticket/{uniqueid}.png'