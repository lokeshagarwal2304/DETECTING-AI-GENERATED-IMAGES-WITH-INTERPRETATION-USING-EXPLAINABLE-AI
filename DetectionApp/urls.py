from django.urls import path

from . import views

urlpatterns = [path("index.html", views.index, name="index"),
		     path("UserLogin.html", views.UserLogin, name="UserLogin"),
		     path("UserLoginAction", views.UserLoginAction, name="UserLoginAction"),
		     path("SingleImage.html", views.SingleImage, name="SingleImage"),
		     path("SingleImageAction", views.SingleImageAction, name="SingleImageAction"),		     
		     
		    ]