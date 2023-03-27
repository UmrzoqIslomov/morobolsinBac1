from rest_framework.generics import ListCreateAPIView
from rest_framework.response import Response

from base.format import category_format, product_format
from sayt.models import Category, Product
from .serializer import CategorySerializer


class CategoryView(ListCreateAPIView):
    serializer_class = CategorySerializer

    def get(self, requests, pk=None, *args, **kwargs):
        if pk:
            # result = product_format(Product.objects.filter(category_id=pk))
            try:
                product = [product_format(i) for i in Product.objects.filter(category_id=pk)]
            except:
                product = "Bu categoryda product mavjud emas"

            try:
                result = category_format(Category.objects.filter(pk=pk).first())
            except:
                result = "bu id da category yo'q"
                product = None

        if not pk:
            result = [category_format(i) for i in Category.objects.all()]
            product = None

        return Response({"category": result,
                         'product': product})

    def put(self, requests, pk, *args, **kwargs):

        data = requests.data
        new = Category.objects.filter(pk=pk).first()
        if not new:
            return Response({'error': 'bu pkda category topilmadi'})
        serializer = self.get_serializer(data=data, instance=new, partial=True)
        serializer.is_valid(raise_exception=True)
        root = serializer.save()
        return Response(category_format(root))

    def delete(self, requeste, pk, *args, **kwargs):
        try:
            category = Category.objects.get(pk=pk).delete()
            result = {"resultat": f"categoriya {pk} id o'chirildi"}
        except:
            result = {"resultat": f"{pk}da categoriya topilmadi"}
        return Response(result)
