import json
import random
import uuid
import datetime

import requests
from rest_framework import status
from rest_framework.authtoken.models import Token
from rest_framework.generics import GenericAPIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from api.v1.auth.serializer import Userserializer
from api.models import User, OTP
from api.v1.auth.servise import sms_sender, BearerAuth
from base.helper import generate_key, code_decoder
from sayt.models import Product, Basket


class AuthView(GenericAPIView):
    serializer_class = Userserializer

    def post(self, request, *args, **kwargs):
        data = request.data
        method = data.get('method')
        params = data.get('params')

        if not method:
            return Response({
                "Error": "method kiritilmagan"
            })

        if params is None:
            return Response({
                "Error": "params kiritilmagan"
            })

        if method == "regis":
            mobile = params.get("mobile")
            name = params.get("name")
            user = User.objects.filter(mobile=mobile).first()
            if user:
                return Response({
                    "Error": "Bu tel nomer allaqachon bor"
                })

            serializer = self.get_serializer(data=params)
            serializer.is_valid(raise_exception=True)
            user = serializer.create(serializer.data)
            user.set_password(params["password"])
            user.save()

            token = Token()
            token.user = user
            token.save()

        elif method == "login":
            nott = 'mobile' if "mobile" not in params else "password" if "password" not in params else None
            if nott:
                return Response({
                    "Error": f"{nott} polyasi to'ldirilmagan"

                })

            mobile = params.get("mobile")
            user = User.objects.filter(mobile=mobile).first()

            if not user:
                return Response({
                    "Error": "Bunday User topilmadi"
                })
            if not user.check_password(params['password']):
                return Response({
                    "Error": "parol  xato"
                })
            try:
                token = Token.objects.get(user=user)
            except:
                token = Token()
                token.user = user
                token.save()

        elif method == "step.one":
            params = data['params']
            nott = params['mobile']
            print(nott)
            if not nott:
                return Response({
                    "Error": f"paramsda mobile polyasi to'ldirilmagan"
                })

            users = User.objects.filter(mobile=params["mobile"]).first() or User.objects.filter(
                mobile="+" + params["mobile"]
            ).first()
            if users:
                return Response(
                    {
                        'Error': "Bunday mobile allaqachon ro'yxatdan  o'tgan"
                    }, status=status.HTTP_400_BAD_REQUEST
                )

            code = random.randint(10000, 99999)
            key = generate_key(50) + "$" + str(code) + "$" + uuid.uuid1().__str__()
            otp = code_decoder(key)
            # sms = sms_sender(params['mobile'], code)

            # if sms.get('status') != "waiting":
            #     return Response({
            #         "error": "sms xizmatida qandaydir muommo",
            #         "data": sms
            #     })
            root = OTP()
            root.mobile = params['mobile']
            root.key = otp
            root.save()

            return Response({
                "otp": code,
                "token": root.key
            })



        elif method == "step.two":
            nott = 'otp' if "otp" not in params else "token" if "token" not in params else None
            if nott:
                return Response({
                    "Error": f"params.{nott} polyasi to'ldirilmagan"

                })

            otp = OTP.objects.filter(key=params['token']).first()
            if not otp:
                return Response({
                    "Error": f"Xato Token"
                })

            otp.state = "step_two"
            otp.save()
            now = datetime.datetime.now(datetime.timezone.utc)
            cr = otp.created_at
            if (now - cr).total_seconds() > 120:
                otp.is_expired = True
                otp.save()
                return Response({
                    "Error": f"Kod eskirgan"
                })

            if otp.is_expired:
                return Response({
                    "Error": f"Kod eskirgan"
                })

            otp_key = code_decoder(otp.key, decode=True)
            key = otp_key.split("$")[1]
            if str(key) != str(params['otp']):
                otp.tries += 1
                if otp.tries >= 3:
                    otp.is_expired = True

                otp.save()
                return Response({
                    "Error": "Xato OTP"
                })
            user = User.objects.filter(mobile=otp.mobile).first() or User.objects.filter(
                mobile="+" + otp.mobile).first()

            otp.state = "confirmed"
            otp.save()
            if user:
                return Response({
                    "is_registered": True
                })
            else:
                return Response({
                    "is_registered": False
                })

        else:
            return Response({
                "Error": "Bunday method yoq"
            })

        return Response({
            "result": {
                "token": token.key,
                "mobile": user.mobile,
                "name": user.name,
            }
        })


class ActionViews(GenericAPIView):
    authentication_classes = (BearerAuth,)
    permission_classes = (IsAuthenticated,)

    def post(self, request, *args, **kwargs):
        data = request.data
        method = data.get('method')
        params = data.get('params')
        if not method:
            return Response({
                "Error": "method polyasi to'ldirilmagan"
            })
        if params is None:
            return Response({
                "Error": "params polyasi to'ldirilmagan"
            })

        if method == "add.basket":
            if 'product_id' not in params:
                return Response({
                    "Error": "parmas.product_id bo'lishi kerak"
                })

            pro = Product.objects.filter(pk=params['product_id']).first()
            if not pro:
                return Response({
                    "Error": "bunaqa pr0 topilmadi"
                })

            prev = Basket.objects.filter(user=request.user, product=pro).first()
            if prev:
                bas = prev
            else:
                bas = Basket()
            bas.user = request.user
            bas.product = pro
            bas.quantity = params.get('quantity', 1)
            bas.save()

            return Response({
                "res": "basketga qowildi",
                "data": bas.response()
            })
        elif method == "del.Basket":
            if 'basket_id' not in params:
                return Response({
                    "Error": "parmas.basket_id bo'lishi kerak"
                })
            pro = Basket.objects.filter(pk=params['basket_id']).first()
            if not pro:
                return Response({
                    "Error": " bunaqa pro topilmadi"
                })
            else:
                pro.delete()

            return Response({
                "res": f"basketdan {params['basket_id']}-id lik product  ochirildi"
            })
        elif method == "seeAll":
            return Response({
                "res": "hammasini koriw",
                "data":  [x.response() for x in Basket.objects.filter(user=request.user)]
            })

        else:
            return Response({
                "Error": "bunaqa method yo"
            })