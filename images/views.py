from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .forms import ImageCreateForm
from django.shortcuts import get_object_or_404
from .models import Image
from django.http import JsonResponse, HttpResponse
from django.views.decorators.http import require_POST
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger


@login_required
def image_create(request):
    if request.method == "POST":
        # форма отправлена
        form = ImageCreateForm(data=request.POST)
        if form.is_valid():
            # данные в форме валидны
            cd = form.cleaned_data
            new_image = form.save(commit=False)
            # назначить текущего пользователя элементу
            new_image.user = request.user
            new_image.save()
            messages.success(request, "Image added successfully")
            # перенаправить к представлению детальной
            # информации о только что созданном элементе
            return redirect(new_image.get_absolute_url())
    else:
        # скомпоновать форму с данными(url и title)
        # предоставленными букмарклетом методом GET
        form = ImageCreateForm(data=request.GET)
    return render(request,
                  "images/image/create.html",
                  {"section": "images",
                   "form": form}) 


def image_detail(request, id, slug):
    image = get_object_or_404(Image, id=id, slug=slug)
    return render(request, "images/image/detail.html", {"section": "images",
                                                        "image": image})


@login_required
@require_POST
def image_like(requset):
    image_id = requset.POST.get("id")
    action = requset.POST.get("action")
    if image_id and action:
        try:
            image = Image.objects.get(id=image_id)
            if action == "like":
                image.users_like.add(requset.user)
            else:
                image.users_like.remove(requset.user)
            return JsonResponse({"status": "ok"})
        
        except Image.DoesNotExist:
            pass
        return JsonResponse({"status": "error"})
    
@login_required
def image_list(request):
    images = Image.objects.all()
    paginator = Paginator(images, 8)
    page = request.GET.get("page")
    images_only = request.GET.get("images_only")
    try:
        images = paginator.page(page)
    except PageNotAnInteger:
        #Если страница не является целым числом,
        # то отобразим первую страницу
        images = paginator.page(1)
    except EmptyPage: # вызывается, если запрошенная страница находиться вне диапазона 
        if images_only:
            # Если AJAX-запрос и страница вне диапозона,
            # то вернуть пустую страницу
            return HttpResponse("")
        # Если старница вне диапозона, 
        # то вернуть последнюю страницу
        images = paginator.page(paginator.num_pages)

    if images_only:
        return render(request, 
                      "images/image/list_images.html",
                      {"section": images,
                       "images": images})
    
    return render(request, 
                  "images/image/list.html",
                  {"section": "images",
                   "images": images})