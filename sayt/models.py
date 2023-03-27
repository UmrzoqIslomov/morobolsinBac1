from collections import OrderedDict

from django.db import models
from django.contrib.auth.base_user import BaseUserManager
from django.contrib.auth.models import AbstractUser, AbstractBaseUser

# Create your models here.
from api.models import User
from base.format import product_format, user_format, sub_format

price_type = {
    ("$", "$"),
    ("sum", "sum"),
    ("₽", "₽")
}

class Color(models.Model):
    name = models.CharField(max_length=256)
    def __str__(self):
        return self.name

class Category(models.Model):
    content = models.CharField(max_length=256)
    slug = models.CharField(max_length=256)

    def __str__(self):
        return self.content

    def res(self):
        sub = []
        for i in SubCategory.objects.filter(ctg=self):
            sub.append(sub_format(i))
        return OrderedDict([
        ('id', self.id),
        ('content', self.content),
        ('slug', self.slug),
        ("sub", sub)
    ])

class SubCategory(models.Model):
    name = models.CharField(max_length=256)
    ctg = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return self.name


class Product(models.Model):
    color = models.ManyToManyField(Color)
    category = models.ForeignKey(Category, null=True, on_delete=models.SET_NULL)
    name = models.CharField(max_length=256)
    tag = models.CharField(max_length=256)
    pesonType = models.CharField(max_length=256)
    level = models.CharField(max_length=256)
    price = models.IntegerField(default=0)
    price_type = models.CharField(choices=price_type, max_length=5)
    def __str__(self):
        return self.name


class ProImg(models.Model):
    pro = models.ForeignKey(Product, null=True, on_delete=models.SET_NULL)
    img = models.ImageField()


class Skidka(models.Model):
    pro = models.ForeignKey(Product, on_delete=models.CASCADE)
    skid_per = models.CharField("Donasi uchun skidka", max_length=128)
    prise_skid = models.CharField("Skidka narxi", max_length=128)

    def __str__(self):
        return self.skid_per


class Razmer(models.Model):
    pro = models.ForeignKey(Product, null=True, on_delete=models.SET_NULL)
    razmer = models.CharField(max_length=256)

    def __str__(self):
        return self.razmer


class Basket(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    total = models.IntegerField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True, auto_now=False, editable=False)
    updated_at = models.DateTimeField(auto_now_add=False, auto_now=True)

    def save(self, *args, **kwargs):
        self.total = self.product.price * self.quantity
        return super(Basket, self).save(*args, **kwargs)

    def response(self):
        return {
            'id': self.id,
            'product': product_format(self.product),
            "user": user_format(self.user),
            'quantity': self.quantity,
            'total': self.total,
        }

class Saved(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)



