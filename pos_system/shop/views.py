from typing import Any, Dict
from django.shortcuts import render
from django.views.generic import TemplateView, View
from . import models


aside_menus = ["statistics", "kassa", "employers", "products", "orders", "clients", "settings"]



def index_view(request):
    cnt = {
        "aside_menus": ["statistics", "kassa", "employers", "products", "orders", "clients", "settings"]
    }
    return render(request, "index.html", cnt)


class ProductList(TemplateView):
    template_name = "products.html"
    
    def get_context_data(self, **kwargs):
        cnt = super().get_context_data(**kwargs)
        qs = models.Product.objects.all().order_by("title")
        search = self.request.GET.get("search")
        if search:
            qs = qs.filter(title__icontains=search)
        cnt["aside_menus"] = aside_menus
        cnt["object_list"] = qs
        return cnt



class ProductDetail(View):
    
    def get_object(self):
        return models.Product.objects.get(pk=self.kwargs["pk"])
    
    def get(self, request, pk):
        product = self.get_object()
        cnt = {
            "aside_menus": aside_menus,
            "object": product,
        }
        return render(request, "product_detail.html", cnt)
    
    def post(self, request, pk):
        product = self.get_object()
        errors = []
        data = request.POST
        try:
            title = str(data["title"])
            price = str(data["price"])
            count_in_box = int(data["count_in_box"])
        except (KeyError, ValueError) as e:
            errors.append("Xatolik")
        if models.Product.objects.filter(title=title).exclude(pk=product.pk).exists():
            errors.append("Bu nomli mahsulot mavjud")
        if errors:
            cnt = {
                "aside_menus": aside_menus,
                "object": product,
                "message_list": errors,
            }
            return render(request, "product_detail.html", cnt)
        product.title = title
        product.price = price
        product.count_in_box = count_in_box
        product.save()
        return render(request, "product_detail.html", {"aside_menus": aside_menus, "object": product, "success": True})


class ProductCreate(View):
    
    def get(self, request):
        cnt = {
            "aside_menus": aside_menus,
        }
        return render(request, "product_create.html", cnt)
    
    
    def post(self, request):
        errors = []
        data = request.POST
        try:
            title = str(data["title"])
            price = str(data["price"])
            count_in_box = int(data["count_in_box"])
        except (KeyError, ValueError) as e:
            errors.append("Xatolik")
        if models.Product.objects.filter(title=title).exists():
            errors.append("Bu nomli mahsulot mavjud")
        if errors:
            cnt = {
                "aside_menus": aside_menus,
                "message_list": errors,
            }
            return render(request, "product_create.html", cnt)
        product = models.Product.objects.create(title=title, price=price, count_in_box=count_in_box)
        return render(request, "product_detail.html", {"aside_menus": aside_menus, "object": product, "success": True})
