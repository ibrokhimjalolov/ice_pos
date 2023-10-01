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
<b>Buyurtma sanasi:</b> {{ order.created_at | date:"Y-m-d H:i:s" }}
"""
    content = django.template.Template(html).render(django.template.Context({"order": order}))
    Bot.send_message(CHAT_ID, content, parse_mode="HTML")
