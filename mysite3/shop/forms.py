from django import forms
from .models import *


class ImageFieldForm(forms.Form):
    images = forms.ImageField(required=False, widget=forms.ClearableFileInput(attrs={'multiple': True}))
    mini = forms.ImageField(label='Mini images', required=False, widget=forms.ClearableFileInput(attrs={'multiple': True}))


class LoginForm(forms.Form):
    username = forms.CharField(label='Имя:', max_length=30)
    password = forms.CharField(label='Пароль:', max_length=30)


class RegisterForm(forms.Form):
    first_name = forms.CharField(label='Имя: ', max_length=20)
    username = forms.CharField(label='Имя: ', max_length=30)
    password = forms.CharField(label='Пароль: ', max_length=30)
    email = forms.EmailField(required=True)


class SearchForm(forms.Form):
    c_list = [('all', 'Все категории')]
    c_list.extend([(cat.name, cat.name) for cat in Category.objects.all()])
    CATEGORY_CHOICES = (c_list)
    SEARCH_CHOICES = (('name','Модель',),('manufacturer', 'Марка',),
                      ('description','Описание',),)
    ORDER_CHOICES = (('price_down','По убыванию цены',),('price_up', 'По возрастанию цены',),
                      ('alph','По алфавиту',),('alph_back','Алфавит наоборот',))
    order = forms.ChoiceField(required=False, label='Сортировать:', widget=forms.RadioSelect,
                              choices=ORDER_CHOICES)
    where = forms.ChoiceField(required=False, label='В каком поле искать:', widget=forms.RadioSelect, choices=SEARCH_CHOICES)
    categories = forms.MultipleChoiceField(initial = ('all', 'Все категории'), label='Категория поиска:',
        required=True,
        widget=forms.CheckboxSelectMultiple,
        choices=CATEGORY_CHOICES,
    )
    search = forms.CharField(required=False, label='Что искать:', max_length=30)



class ProductInCartForm(forms.Form):
    quantity = forms.IntegerField(label='Заказать:', min_value = 0, initial = 0)


class AddCommentStaffForm(forms.Form):
    name = forms.CharField(label='Имя: ', max_length=30, required=True)
    content = forms.CharField(widget=forms.Textarea, max_length=4000, required=True, label='')


class AddCommentForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea, max_length=4000, required=True, label='')

# class CartForm(forms.ModelForm):
#
#     class Meta:
#         model = Product_in_cart
#         fields = ['product', 'quantity', 'guest'] # , 'guest'






