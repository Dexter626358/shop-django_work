from .models import Product, Category_photo, Category, Guest, Product_in_cart, Photo, Mini_photo
from django.http import HttpResponse, HttpResponseNotFound
from django.views import View, generic
from django.http import HttpResponseBadRequest, HttpResponseForbidden, HttpResponseRedirect
from django.core.paginator import Paginator
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.generic.edit import FormView
from .forms import ImageFieldForm, LoginForm, RegisterForm, ProductsInCartForm
from django.core.validators import validate_image_file_extension
from django.shortcuts import render
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_http_methods


nginx = "http://127.0.0.1:80"
Page_Size = 3


def get_mini(prod):
    mini = Mini_photo.objects.filter(product=prod)
    if mini:
        pics = [m for m in mini]
        mini = nginx + str(pics[0].mini.url)
    else:
        mini = None
    return mini


def get_product_str(prod):
    mini = get_mini(prod)
    data = {"category" : prod.category.name, "name": prod.name, "id": prod.id, "price": prod.price,
                "mini": mini,"incoming_date": prod.incoming_date.strftime('%Y.%m.%d-%H:%M:%S')}
    return data


def log_out(request):
    logout(request)
    return HttpResponseRedirect(reverse("shop:index"))


def log_in(request): #  *args, **kwargs
    form = LoginForm(request.POST)
    if form.is_valid():
        user = authenticate(request, username=form.cleaned_data['username'], password=form.cleaned_data['password'])
        if user is not None:
            login(request, user)
            try:
                g = Guest.objects.get(username=user.username)
            except Guest.DoesNotExist:
                content = "You are login " + user.username + '. But to purchase goods you need to register as a guest.'
                return HttpResponse(content)
        else:
            return HttpResponseForbidden('You must register first.')
        return HttpResponseRedirect(reverse('shop:cart'))
    else:
        return LoginForm()


class LoginGuestView(FormView):
    form_class = LoginForm
    template_name = 'shop/login.html'
    success_url = reverse_lazy('shop:cart')

    def post(self, request): #  *args, **kwargs
        # form_class = self.get_form_class()
        # form = self.get_form(form_class)
        return log_in(request)


class ProductsCartView(View): # PersonalAreaView
    model = Guest

    def get(self, request):
        user = request.user
        if not user.is_authenticated:
            return HttpResponseRedirect(reverse('shop:login'))
        if user.is_staff:
            return HttpResponseRedirect(reverse('admin:index'))
        g = get_object_or_404(Guest, username=user.username)
        cart = g.products_cart.all()
        data = []
        for pc in cart:
            p = pc.product
            mini = get_mini(p)
            data.append({"id": p.id, "name": p.name, "quantity": p.quantity, "mini": mini})
        context = {"name": g.username, 'cart': data}
        return render(request, 'shop/cart.html', context)


from django.http import JsonResponse

def validate_username(request):
    username = request.GET.get('username', None)
    data = {
        'is_taken': User.objects.filter(username__iexact=username).exists()
    }
    if data['is_taken']:
        data['error_message'] = 'Пользователь с именем "' + username + '" уже существует.'
    return JsonResponse(data)


# < script src = "{% static 'js/app.js' %}" > < / script >
# < link rel = "stylesheet" type = "text/css" href = "{% static 'css/app.css' %}" >

# from django.contrib.auth.forms import UserCreationForm
# from django.views.generic.edit import CreateView
# class RegistrationGuestView(CreateView):
#     form_class = UserCreationForm



class RegistrationGuestView(FormView):
    form_class = RegisterForm
    template_name = 'shop/register.html'
    success_url = reverse_lazy('shop:cart')

    def get(self, request):
        return render(request, self.template_name, {"form": RegisterForm()})

    def post(self, request): #  *args, **kwargs
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']
            try:
                User.objects.get(username=username)
            except User.DoesNotExist:
                g = Guest.objects.create_user(username, email, password)
                login(request, g)
            else:
                content = 'User with name ' + username + ' already exist!'
                return HttpResponseForbidden(content)
            return self.form_valid(form)
        else:
            return self.form_invalid(form)


class IndexView(View):
    model = Category

    def get(self, request):
        list_c = Category.objects.order_by('name') # 'pk'
        done = []
        for cat in list_c:
            image = Category_photo.objects.filter(category=cat)
            if image:
                pics = [m for m in image]
                image = nginx + str(pics[0].photo.url)
            else:
                image = None
            done.append({"name": cat.name, "image": image, "id": cat.id})
        user = request.user
        # user = authenticate(request, username=user.username, password=user.password)
        context = {"data": done, "form": LoginForm(), "user": user if user.is_authenticated else False}
        # "username": user.username, "login": True if user.is_authenticated else False}
        return render(request, 'shop/index.html', context)

    def post(self, request): #  *args, **kwargs
        return log_in(request)


class DetailView(View):
    model = Product

    def get(self, request, product_id):
        prod = get_object_or_404(Product, pk=product_id)
        data = get_product_str(prod)
        data["description"] = prod.description
        photos = Photo.objects.filter(product=prod)
        urls = [nginx + str(file.photo.url) for file in photos]
        data["images"] = urls
        form = ProductsInCartForm()
        data["cart_form"] = form
        id = 0
        if request.user.is_staff:
            id = product_id
        data["id"] = id
        return render(request, 'shop/detail.html', data)

    def post(self, request, product_id): # Add Product_in_cart # *args, **kwargs
        prod = get_object_or_404(Product, pk=product_id)
        user = request.user
        if not user.is_authenticated:
            return HttpResponseRedirect(reverse('shop:login'))
        try:
            guest = Guest.objects.get(username=user.username)
        except Guest.DoesNotExist:
            return HttpResponseRedirect(reverse('shop:login'))
        form = ProductsInCartForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            pic = Product_in_cart.objects.create(product=prod, quantity=quantity)
            guest.products_cart.add(pic)
        else:
            return form.form_invalid()
        return HttpResponseRedirect(reverse('shop:cart'))


class CategoryView(View):
    model = Product

    def get(self, request, category_id, page=1, size=Page_Size):
        cat = get_object_or_404(Category, pk=category_id)
        all = Product.objects.filter(category = cat).order_by('id')
        p = Paginator(all, size)
        data = p.page(page)
        done = [get_product_str(p) for p in data]
        context = {"category": cat.name, "data": done}
        context["category_id"] = category_id # '/page'
        context["pages"] = [pnum for pnum in p.page_range]
        context["current_page"] = page
        # context["size"] = size  arg3=size
        return render(request, 'shop/category.html', context)


@require_http_methods(["POST"])   # POST GET
def log_in(request):
    form = LoginForm(request.POST)
    if form.is_valid():
        user = authenticate(request, username=form.cleaned_data['username'], password=form.cleaned_data['password'])
        if user is not None:
            login(request, user)
            try:
                g = Guest.objects.get(username=user.username)
            except Guest.DoesNotExist:
                content = "Вы вошли " + user.username + '. Но чтобы заказывать зарегистрируйтесь как клиент.'
                return JsonResponse({"error":content})
        else:
            return JsonResponse({"error":'Неверный логи или пароль.'})
        return JsonResponse({"error": False, "hello": "Здравствуйте, " + user.username}) # , "url": reverse('shop:cart')
    else:
        return JsonResponse({"error":'Ошибка. Введите логин и пароль.'})# LoginForm()


@staff_member_required(login_url='admin:login') # , redirect_field_name='shop:index'
def add_photos(request, product_id):  # , *args, **kwargs
    if request.method == 'POST':
        prod = get_object_or_404(Product, pk=product_id)
        form = ImageFieldForm(request.POST)
        if form.is_valid():
            pictures = request.FILES.getlist('images')
            for f in pictures:
                # if validate_image_file_extension(f):
                image = Photo(photo=f, product=prod)
                image.save()
                prod.photo_set.add(image)
            pictures = request.FILES.getlist('mini')
            for f in pictures:
                image = Mini_photo(mini=f, product=prod)
                image.save()
                prod.mini_photo_set.add(image)
            return HttpResponseRedirect(reverse('shop:detail', args=(product_id,)))
        else:
            return ImageFieldForm.form_invalid(form)
    else:
        prod = get_object_or_404(Product, pk=product_id)
        photos = Photo.objects.filter(product=prod)
        mini_photos = Mini_photo.objects.filter(product=prod)
        images_urls = [nginx + str(file.photo.url) for file in photos]
        mini_urls = [nginx + str(file.mini.url) for file in mini_photos]
        form = ImageFieldForm()
        context = {"images": images_urls, "minis": mini_urls, "form": form}
        return render(request, 'shop/photos.html', context)









