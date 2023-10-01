import datetime
import telebot
import django


Bot = telebot.TeleBot('6663339888:AAGACkXkrUmjm3xq2rWtVUJ4lgPa2CXBo1A')
CHAT_ID = '-4046728742'


def parse_date(date_str, date_format="%Y-%m-%d"):
    if not date_str:
        return None
    return datetime.datetime.strptime(date_str, date_format).date()


def send_order_create_notify(order):
    html = """
<b>Buyurtma raqami:</b>  {{ order.id }}
<b>Holati:</b> {{ order.get_status_display }}
<b>Buyurtmachi:</b> {{ order.consumer.fio | default:"-" }}
<b>Kuryer:</b> {{ order.courier.fio | default:"-" }}
<b>Tolangan:</b> {{ order.paid_price }}
<b>Narxi:</b> {{ order.total_price }}
<b>Olingan mahsulotlar:</b>
{{ products }}
"""
    content = django.template.Template(html).render(django.template.Context({"order": order, "products": "\n".join([f"{i}. {p.product} - {p.count} x {p.price} = {p.count * p.price}" for i, p in enumerate(order.products.all(), 1)])}))
    Bot.send_message(CHAT_ID, content, parse_mode="HTML")
