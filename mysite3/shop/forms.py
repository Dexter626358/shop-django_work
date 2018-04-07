from django import forms

class ImageFieldForm(forms.Form):
    images = forms.ImageField(required=False, widget=forms.ClearableFileInput(attrs={'multiple': True}))
    mini = forms.ImageField(label='Mini images', required=False, widget=forms.ClearableFileInput(attrs={'multiple': True}))

#FileField
# method POST and
# the <form> that posted the request has the attribute enctype="multipart/form-data".

class LoginForm(forms.Form):
    username = forms.CharField(label='Имя:', max_length=30)
    password = forms.CharField(label='Пароль:', max_length=30)


class RegisterForm(forms.Form):
    username = forms.CharField(label='Имя: ', max_length=30)
    password = forms.CharField(label='Пароль: ', max_length=30)
    email = forms.EmailField(required=True)


class ProductsInCartForm(forms.Form):
    quantity = forms.IntegerField(label='Заказать, сколько: ', localize=False, initial=1, min_value=0)


    # forms.DecimalField(max_digits=4, decimal_places=2, localize=True)
# < input type = "number"... >