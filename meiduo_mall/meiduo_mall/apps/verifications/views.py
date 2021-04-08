from django.shortcuts import render
from rest_framework.views import APIView


# Create your views here.
class SMSCodeView(APIView):
    """短信验证码"""

    def get(self, request, mobile):
        pass

    