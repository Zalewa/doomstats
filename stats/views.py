from django.shortcuts import render


def front_page(request):
    return render(request, "stats/front_page.html")
