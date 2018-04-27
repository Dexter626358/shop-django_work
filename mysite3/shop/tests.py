from .models import Product, Category_photo, Category, Guest, Product_in_cart, Photo, Mini_photo
from .forms import LoginForm
from django.test import TestCase, SimpleTestCase
from django.urls import reverse
from django.utils import timezone
from django.contrib.auth.models import User
from django.contrib.auth import authenticate
from django.contrib.auth.models import AnonymousUser, User


nginx = "http://127.0.0.1:80"


class indexViewTests(TestCase):


    def test_no_categories(self):
        """
        If no categories exist, an appropriate message is displayed.
        """
        password = 'top_secret'
        user = User.objects.create_user(
            username='jacob', email='jacob@mail.ru', password=password)
        bool_log = self.client.login(username=user.username, password=password)
        self.assertTrue(bool_log)
        response = self.client.get(reverse('shop:index'))
        self.assertEqual(response.status_code, 200)
        # l = LoginForm()
        # l.fields['username'] = user.username
        # l.fields['password'] = password
        # l.full_clean()
        cont = {"data": [], "user": user}  # "form": l,
        for key , val in cont.items():
            self.assertEqual(response.context[key], val)
        self.client.logout()
        response = self.client.get(reverse('shop:index'))
        self.assertEqual(response.status_code, 200)
        cont = {"data": [], "user": False}
        for key , val in cont.items():
            self.assertEqual(response.context[key], val)
        # self.assertContains(response, c)



    def test_5_categories(self):
        Category.objects.create(name="category_1")
        Category.objects.create(name="category_2")
        Category.objects.create(name="category_3")
        Category.objects.create(name="category_A")
        Category.objects.create(name="category_B")
        response = self.client.get(reverse('shop:index'))
        self.assertEqual(response.status_code, 200)
        list_c = Category.objects.order_by('name')
        done = []
        for cat in list_c:
            image = Category_photo.objects.filter(category=cat)
            if image:
                pics = [m for m in image]
                image = nginx + str(pics[0].photo.url)
            else:
                image = None
            done.append(str({"name": cat.name, "image": image, "id": cat.id}))
        self.assertQuerysetEqual(
            response.context["data"], done)
        self.assertEqual(response.context["user"], False)
        password = 'top_secret'
        user = User.objects.create_user(
            username='jacob', email='jacob@mail.ru', password=password)
        self.client.login(username=user.username, password=password)
        response = self.client.get(reverse('shop:index'))
        self.assertEqual(response.status_code, 200)
        self.assertQuerysetEqual(
            response.context["data"], done)
        self.assertEqual(response.context["user"], user)

#

# def login_user_staff(self):
#     password = 'johnpassword'
#     user = User.objects.create_user('john', 'lennon@thebeatles.com', password)
#     user.is_staff = True
#     user.save()
#     self.assertTrue(user.is_staff)
#     bool_log = self.client.login(username=user.username, password=password)
#     self.assertTrue(bool_log)
#
#
# prod_id = 0
#
# def add_products_check_detail_description(self, n, cat, product_name):
#     global prod_id
#     prov = Provider.objects.create(name="provider_1", phone="123456", email='lena@thebeatles.com')
#     expected_data, in_list = [], []
#     for i in range(n):
#         in_list.append(i)
#         price = 267 + i
#         prod_id += 1
#         description = "description" + str(i)
#         name = product_name + str(i)  # "username": user.username, "password": password,
#         data = json.dumps({'name': name, 'price': price, 'provider': prov.name, "description": description})
#         response = self.client.post(reverse('shop:category', args=(cat.id,)), data, content_type="application/json")
#         time = timezone.now()
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.json()['category'], cat.name)
#         data = {"name": name, "id": prod_id, "price": price, "provider": prov.name,
#                 "production_date": time.strftime('%Y.%m.%d-%H:%M:%S')}
#         # self.assertEqual(response.json()['data'], [data])
#         SimpleTestCase.assertJSONEqual(self, json.dumps(response.json()['data']), json.dumps([data]),
#                                        msg="Time can be different in 1 second!")
#         del data["provider"]
#         data["description"] = description
#         response = self.client.get(reverse('shop:detail', args=(prod_id,)))
#         self.assertEqual(response.json()['data'], [data])
#         del data["description"]
#         expected_data.append(data)
#     return expected_data
#
#
# class categoryViewTests(TestCase):
#     def test_no_category(self):
#         data = [{"detail": "Object With Identifier = 1000 Does Not Exist.", "status": "404", "source": {"pointer": "/data/<class 'shop.models.Category'>/obj_id"}}] # {"errors": }
#         response = self.client.get(reverse('shop:category', args=(1000,)))
#         self.assertEqual(response.status_code, 404)
#         self.assertEqual(response.json()['errors'], data)
#
#
#     def test_new_category(self):
#         """
#         If new category add, an appropriate message is displayed.
#         """
#         name = "category_1"
#         cat = Category.objects.create(name = name)
#         response = self.client.get(reverse('shop:category', args=(cat.id,)))
#         data = {"data": []}
#         self.assertContains(response, json.dumps(data))
#
#
#     def test_not_json(self):
#         cat = Category.objects.create(name="category_1")
#         response = self.client.post(reverse('shop:category', args=(cat.id,)), {'username': 'john', 'password': 'smith'})
#         error1 = {"status": "400"}
#         error1["source"] = {"pointer": "/post/content_type/application_json"}
#         error1["title"] = 'Wrong POST attempt.'
#         error1["detail"] = "Content-Type: application/json."
#         data = [error1]
#         self.assertEqual(response.status_code, 400)
#         self.assertEqual(response.json()['errors'], data)
#
#
#     def test_products_detail_description_pagination(self):
#         n = 10   # - products
#         cat = Category.objects.create(name="category_1")
#         login_user_staff(self)
#         expected_data = add_products_check_detail_description(self, n, cat, 'product_name')
#         self.client.logout()
#
#         response = self.client.get(reverse('shop:category', args=(cat.id, 1, 5)))
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.json()['category'], cat.name)
#         in_data = response.json()['data']
#         in_list = [j for j in range(n)]
#         for data in in_data:
#             in_list[data['id'] - 1] = data
#         self.assertEqual(in_list[:5], expected_data[:5])
#
#         response = self.client.get(reverse('shop:category', args=(cat.id, 2, 5)))
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.json()['category'], cat.name)
#         in_data = response.json()['data']
#         in_list = [j for j in range(n)]
#         for data in in_data:
#             in_list[data['id'] - 1] = data
#         self.assertEqual(in_list[5:], expected_data[5:])
#
#         response = self.client.get(reverse('shop:category', args=(cat.id, 2, 3)))
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.json()['category'], cat.name)
#         in_data = response.json()['data']
#         in_list = [j for j in range(n)]
#         for data in in_data:
#             in_list[data['id'] - 1] = data
#         self.assertEqual(in_list[3:6], expected_data[3:6])
#
#         response = self.client.get(reverse('shop:category', args=(cat.id, 4, 3)))
#         self.assertEqual(response.status_code, 200)
#         self.assertEqual(response.json()['category'], cat.name)
#         in_data = response.json()['data']
#         self.assertEqual(in_data, [expected_data[9]])
#
#
# def login_guest(self, username):
#     password = 'johnpassword'
#     data = {'username': username, 'password': password, 'email': 'lennon@thebeatles.com'}
#     response = self.client.post(reverse('shop:login_guest'),
#         json.dumps(data), content_type="application/json")
#     guest = authenticate(None, username=username, password=password)
#     data["date_joined"] = guest.date_joined.strftime('%Y.%m.%d-%H:%M:%S')
#     data["guest"] = "created"
#     self.assertEqual(response.json()["data"], [data])
#     bool_log = self.client.login(username=username, password=password)
#     self.assertTrue(bool_log)
#     return guest
#
#
# class detailViewTests(TestCase):
#     def test_create_guest_add_products_in_cart(self):
#         product_name = 'product_name'
#         n = 5   # - products
#         cat = Category.objects.create(name="category_1")
#         login_user_staff(self)  # request =
#         expected_data = add_products_check_detail_description(self, n, cat, product_name)
#         self.client.logout()  # logout(request)
#         username = 'guest'
#         user = login_guest(self, username)
#         self.assertTrue(user.username == username)
#         for i in range(n):
#             quantity = i + 1
#             data = json.dumps({"quantity": quantity})
#             id = int(expected_data[i]["id"])
#             response = self.client.post(reverse('shop:detail', args=(id,)), data, content_type="application/json")
#             expected_data[i]["quantity"] = quantity
#             expected_data[i]["in_cart"] = 'Ok'
#             self.assertEqual(response.status_code, 200)
#             self.assertEqual(response.json()['username'], username) # user.username
#             self.assertEqual(response.json()['data'], [expected_data[i]])
#         self.client.logout()
#
#
# class photosViewTests(TestCase):
#     def photoPost(self):
#         # try:
#         #     prod = Product.objects.get(pk=1)
#         # except Product.DoesNotExist:
#         #     prod = Product.objects.create(name=product_name, category=cat, price=price)
#         product_name = 'product_name'
#         n = 5  # - products
#         cat = Category.objects.create(name="category_1")
#         login_user_staff(self)  # request =
#         expected_data = add_products_check_detail_description(self, n, cat, product_name)
#         for i in range(n):
#             name = product_name + str(i)
#             prod = Product.objects.get(name=name)
#             self.assertEqual(prod.set_photo, None)
#             data = Файлы
#             response = self.client.post(reverse('shop:photos', args=(prod.id,)), data)
#
#         self.client.logout()



# class loginGuestTests(TestCase):
#     def test_wrong_password(self):
#         pass
#
#
#     def test_login_existed_guest(self):
#         pass