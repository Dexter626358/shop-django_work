from django.urls import path  # , include
from django.conf.urls import url
from django.conf import settings
from django.conf.urls.static import static
from . import views


app_name = 'shop'
#, kwargs=kwargs1  kwargs1={"page": 1, "size": 1}
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('detail/<int:product_id>/', views.DetailView.as_view(), name='detail'),  #  views.detail
    path('photos/<int:product_id>/', views.add_photos, name='photos'), # PhotosProductView.as_view()
    path('<int:category_id>/', views.CategoryView.as_view(), name='category'),
    path('<int:category_id>/page<int:page>/', views.CategoryView.as_view(), name='category'),
    path('<int:category_id>/page<int:page>/size<int:size>/', views.CategoryView.as_view(), name='category'),
    path('login/', views.LoginGuestView.as_view(), name='login'),
    path('register/', views.RegistrationGuestView.as_view(), name='register'),
    path('login/cart/', views.ProductsCartView.as_view(), name='cart'),
    path('logout/', views.log_out, name='log_out'),
    path('search/', views.SearchView.as_view(), name='search'),
    path('ajax/validate_username/', views.validate_username, name='validate_username'),
    path('ajax/login/', views.log_in, name='ajax_login'),
    path('ajax_order_check/', views.ajax_order_check, name='ajax_order_check'),
    path('order/<int:order_id>/', views.OrderView.as_view(), name='order'),
    path('orders/', views.orders, name='orders'),
] #+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)