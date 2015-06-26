from django.shortcuts import render
from .models import *


def front_page(request):
    data = {}
    data["first_batch"] = RefreshBatch.objects.order_by("date")[0]
    data["num_batches"] = RefreshBatch.objects.count()
    data["average_server_count"] = Server.objects.count() / data["num_batches"]
    data["average_player_count"] = Player.objects.count() / data["num_batches"]
    return render(request, "stats/front_page.html", data)


def engine(request, name):
    return render(request, "stats/engine.html", {"name": name})


def about(request):
    return render(request, "stats/about.html")


def load_site_global_context(request):
    return {
        "engines": Engine.objects.all().order_by("name")
    }
