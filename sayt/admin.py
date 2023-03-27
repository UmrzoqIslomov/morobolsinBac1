from django.contrib import admin

# Register your models here.
from sayt.models import *

class RazmerInline(admin.StackedInline):
    model = Razmer
    extra = 1
class ImgInline(admin.StackedInline):
    model = ProImg
    extra = 1


class ProAdmin(admin.ModelAdmin):
    model = Product
    inlines = [ImgInline, RazmerInline]

admin.site.register(Category)
admin.site.register(Skidka)
admin.site.register(SubCategory)
admin.site.register(Product, ProAdmin)
admin.site.register(Color)