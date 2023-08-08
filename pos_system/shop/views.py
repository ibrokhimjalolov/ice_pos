from django.shortcuts import render


def index_view(request):
    cnt = {
        "aside_menus": ["statistics", "kassa", "employers", "products", "orders", "clients", "settings"]
    }
    return render(request, "index.html", cnt)
