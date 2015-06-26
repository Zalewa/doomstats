from django.shortcuts import render
from .models import *


def front_page(request):
    return render(request, "stats/front_page.html")


def engine(request, name):
    return render(request, "stats/engine.html", {"name": name})


def load_site_global_context(request):
    return {
        "engines": Engine.objects.all().order_by("name")
    }
