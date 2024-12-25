from django.urls import path,include
from .views import Sign_up_View,Login,Logout,MainView,DeleteView,EditView,DetailView

urlpatterns = [
    path('user_creation/',Sign_up_View.as_view(), name = 'user_creation'),
    path('login/',Login.as_view(), name = 'login'),
    path('logout/',Logout.as_view(), name = 'logout'),# ログアウトのURLは、後ほど確認。テンプレートを作成しないから
    path('',MainView.as_view(), name = 'main'),
    path('delete',DeleteView.as_view(), name = 'delete'),
    path('<int:pk>/edit/',EditView.as_view(), name = 'edit'),
    path('detail',DetailView.as_view(), name = 'detail'),
    
]