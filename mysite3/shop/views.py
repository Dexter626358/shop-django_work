from .models import *
from .forms import *
from django.http import HttpResponse, HttpResponseNotFound
from django.views import View, generic
from django.http import HttpResponseBadRequest, HttpResponseForbidden, HttpResponseRedirect
from django.core.paginator import Paginator
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.views.generic.edit import FormView
from django.core.validators import validate_image_file_extension
from django.shortcuts import render
from django.urls import reverse
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.contrib.admin.views.decorators import staff_member_required
from django.views.decorators.http import require_http_methods
from django.http import JsonResponse
from django.forms import modelformset_factory


nginx = "http://127.0.0.1:80"
Page_Size = 3


def get_mini(prod):
    mini = Mini_photo.objects.filter(product=prod)
    if mini:
        mini = nginx + str(mini.first().mini.url)
    else:
        mini = None
    return mini


def get_product_str(prod):
    mini = get_mini(prod)
    data = {"category" : prod.category.name, "name": prod.name, "id": prod.id, "price": prod.price,
                "mini": mini,"production_date": prod.production_date.strftime('%Y.%m.%d')} # .strftime('%Y.%m.%d') -%H:%M:%S
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

    def post(self, request):
        return log_in(request)


class SearchView(FormView):
    form_class = SearchForm()
    template_name = 'shop/search.html'
    success_url = reverse_lazy('shop:search')

    def get(self, request):
        form = SearchForm()
        return render(request, self.template_name, {"form": form, "find": False})

    def post(self, request):
        form = SearchForm(request.POST)
        if not form.is_valid():
            return render(request, self.template_name, {"form": form, "find": False})
        categories = form.cleaned_data['categories']
        search = form.cleaned_data['search']
        where = form.cleaned_data['where']
        order = form.cleaned_data['order']
        if "all" in categories:
            res = False
            if where == "name":
                res = Product.objects.filter(name__contains=search)
            elif where == "manufacturer":
                res = Product.objects.filter(manufacturer__name__contains=search)
            elif where == "description":
                res = Product.objects.filter(description__contains=search)
            if res:
                if order == 'alph':
                    res = res.order_by('name')
                elif order == 'alph_back':
                    res = res.order_by('-name')
                elif order == 'price_up':
                    res = res.order_by('price')
                elif order == 'price_down':
                    res = res.order_by('-price')
            elif order == 'alph':
                res = Product.objects.order_by('name')
            elif order == 'alph_back':
                res = Product.objects.order_by('-name')
            elif order == 'price_up':
                res = Product.objects.order_by('price')
            elif order == 'price_down':
                res = Product.objects.order_by('-price')
        else:
            res = Product.objects.none()
            for cat in categories:
                data = None
                c = get_object_or_404(Category, name=cat)
                if where == "name":
                    data = Product.objects.filter(category=c).filter(name__contains=search)
                elif where == "manufacturer":
                    data = Product.objects.filter(category=c).filter(manufacturer__name__contains=search)
                elif where == "description":
                    data = Product.objects.filter(category=c).filter(description__contains=search)
                if data:
                    if order == 'alph':
                        data = data.order_by('name')
                    elif order == 'alph_back':
                        data = data.order_by('-name')
                    elif order == 'price_up':
                        data = data.order_by('price')
                    elif order == 'price_down':
                        data = data.order_by('-price')
                elif order == 'alph':
                    data = Product.objects.filter(category=c).order_by('name')
                elif order == 'alph_back':
                    data = Product.objects.filter(category=c).order_by('-name')
                elif order == 'price_up':
                    data = Product.objects.filter(category=c).order_by('price')
                elif order == 'price_down':
                    data = Product.objects.filter(category=c).order_by('-price')
                res |= data

        form = SearchForm()
        return render(request, self.template_name, {"form": form, "find": res, "where": where})


class ProductsCartView(FormView):
    form_class = modelformset_factory(Product_in_cart, fields=('quantity',), extra=0, can_delete=True)
    template_name = 'shop/cart.html'
    success_url = reverse_lazy('shop:cart')

    def get(self, request):
        user = request.user
        if not user.is_authenticated:
            return HttpResponseRedirect(reverse('shop:login'))
        if user.is_staff:
            return HttpResponseRedirect(reverse('admin:index'))
        g = get_object_or_404(Guest, username=user.username)
        CartFormSet = self.get_form_class() # , can_order=True
        cart = Product_in_cart.objects.filter(guest=g).order_by('id')
        formset = CartFormSet(queryset = cart) # .filter(quantity__gt=0)
        context = {"formset": formset, "name": g.username, "nginx": nginx + '/media/', "cart_full": True if cart else False} # , 'cart': data
        return render(request, self.template_name, context)


    def post(self, request):
        user = request.user
        if not user.is_authenticated:
            return HttpResponseRedirect(reverse('shop:login'))
        if user.is_staff:
            return HttpResponseRedirect(reverse('admin:index'))
        guest = get_object_or_404(Guest, username=user.username)
        CartFormSet = self.get_form_class()
        initial = CartFormSet(queryset=Product_in_cart.objects.filter(guest=guest).order_by('id'))
        formset = CartFormSet(request.POST, initial=initial) # form = CartForm(request.POST, instance=prod)
        if formset.is_valid():
            formset.save()
            good = guest.product_in_cart_set.filter(quantity__gt=0)
            if not good:
                return HttpResponseRedirect(reverse('shop:cart'))
            ord = Order.objects.create(guest=guest)
            for g in good:
                prod = get_object_or_404(Product, id=g.product.id)
                Ordered_product.objects.create(order = ord, product=prod, quantity=g.quantity)
                prod.reserved += g.quantity
                prod.save()
                g.delete()
            return HttpResponseRedirect(reverse('shop:order', args=(ord.pk,))) # cart'))
        else:
            return HttpResponseRedirect(reverse('shop:cart'))


@require_http_methods(["POST"])
def ajax_order_check(request):
    user = request.user
    g = get_object_or_404(Guest, username=user.username)
    CartFormSet = modelformset_factory(Product_in_cart, fields=('quantity',), extra=0, can_delete=True)
    initial = CartFormSet(queryset=Product_in_cart.objects.filter(guest=g).order_by('id'))
    formset = CartFormSet(request.POST, initial=initial)
    error = False
    # if formset.is_valid():
    for form in formset:
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            id = form.instance.product.id
            prod_old = get_object_or_404(Product, id=id)
            free = prod_old.quantity - prod_old.reserved
            if free < quantity:
                error = "В наличии " + prod_old.__str__()
                if free == 0:
                    error += " нет."
                else:
                    error += "  есть только " + str(free) + " шт."
    return JsonResponse({"error": error})


@require_http_methods(["GET"])   # POST
def orders(request):
    user = request.user
    if not user.is_authenticated:
        return HttpResponseRedirect(reverse('shop:login'))
    if user.is_staff:
        return HttpResponseRedirect(reverse('admin:index'))
    guest = get_object_or_404(Guest, username=user.username)
    orders = guest.order_set.all()
    return render(request, 'shop/orders.html', {"orders": orders, "nginx": nginx + '/media/'})


class OrderView(View):
    template_name = 'shop/order.html'

    def get(self, request, order_id):
        user = request.user
        if not user.is_authenticated:
            return HttpResponseRedirect(reverse('shop:login'))
        if user.is_staff:
            return HttpResponseRedirect(reverse('admin:index'))
        order = Order.objects.get(pk=order_id)
        return render(request, self.template_name, {"order": order, "nginx": nginx + '/media/'})
# if request.method == "POST":  - оплата Картой


def validate_username(request):
    username = request.GET.get('username', None)
    data = {
        'is_taken': User.objects.filter(username__iexact=username).exists()
    }
    if data['is_taken']:
        data['error_message'] = 'Пользователь с именем "' + username + '" уже существует.'
    return JsonResponse(data)


class RegistrationGuestView(FormView):
    form_class = RegisterForm
    template_name = 'shop/register.html'
    success_url = reverse_lazy('shop:cart')

    def get(self, request):
        return render(request, self.template_name, {"form": RegisterForm()})

    def post(self, request):
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            email = form.cleaned_data['email']
            first_name = form.cleaned_data['first_name']
            try:
                User.objects.get(username=username)
            except User.DoesNotExist:
                g = Guest.objects.create_user(username, email, password)
                g.first_name = first_name
                g.save()
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
                image = nginx + str(image.first().photo.url)
            else:
                image = None
            done.append({"name": cat.name, "image": image, "id": cat.id})
        user = request.user
        # user = authenticate(request, username=user.username, password=user.password)
        context = {"data": done, "form": LoginForm(), "user": user if user.is_authenticated else False}
        return render(request, 'shop/index.html', context)


    def post(self, request):
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
        comments = Comment.objects.filter(product=prod)
        data['add_com_form'] = id = False
        user = request.user
        if user.is_authenticated:
            if user.is_staff:
                id = product_id
                data['add_com_form'] = AddCommentStaffForm()
            else:
                for com in comments:
                    if com.user.username == user.username:
                        break
                else:
                    data['add_com_form'] = AddCommentForm()
        data["comments"] = comments
        data["id"] = id
        data["cart_form"] = ProductInCartForm()
        return render(request, 'shop/detail.html', data)


    def post(self, request, product_id): # Add Product_in_cart
        prod = get_object_or_404(Product, pk=product_id)
        user = request.user
        if not user.is_authenticated:
            return HttpResponseRedirect(reverse('shop:login'))
        try:
            guest = Guest.objects.get(username=user.username)
        except Guest.DoesNotExist:
            add_com_form = AddCommentStaffForm(request.POST)
            if add_com_form.is_valid():#isinstance(add_com_form, AddCommentStaffForm):
                Comment.objects.create(user=user, product=prod,
                                       name=add_com_form.cleaned_data['name'],
                                       content=add_com_form.cleaned_data['content'])
            return HttpResponseRedirect(reverse('shop:detail', args=(product_id,)))
        form = ProductInCartForm(request.POST)
        add_com_form = AddCommentForm(request.POST)
        if form.is_valid():
            quantity = form.cleaned_data['quantity']
            free = prod.quantity - prod.reserved
            if free < quantity:
                quantity = free
            try:
                pic = guest.product_in_cart_set.get(product=prod)
            except Product_in_cart.DoesNotExist:
                Product_in_cart.objects.create(product=prod, quantity=quantity, guest=guest)
            else:
                pic.quantity += quantity
                pic.save()       # guest.product_in_cart_set.add(pic)
        elif add_com_form.is_valid():
            Comment.objects.create(user = user, product = prod,
                name = user.username,
                content = add_com_form.cleaned_data['content'])
            return HttpResponseRedirect(reverse('shop:detail', args=(product_id,)))
        return HttpResponseRedirect(reverse('shop:cart'))


class CategoryView(View):
    model = Product

    def get(self, request, category_id, page=1, size=Page_Size):
        cat = get_object_or_404(Category, pk=category_id)
        all = Product.objects.filter(category = cat).order_by('name') # id
        p = Paginator(all, size)
        data = p.page(page)
        done = [get_product_str(p) for p in data]
        context = {"category": cat.name, "data": done}
        context["category_id"] = category_id # '/page'
        context["pages"] = [pnum for pnum in p.page_range]
        context["current_page"] = page
        # context["size"] = size
        return render(request, 'shop/category.html', context)


@require_http_methods(["POST"])
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
        return JsonResponse({"error": False, "hello": "Здравствуйте, " + user.username})
    else:
        return JsonResponse({"error":'Ошибка. Введите логин и пароль.'})


@staff_member_required(login_url='admin:login') # , redirect_field_name='shop:index'
def add_photos(request, product_id):
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





