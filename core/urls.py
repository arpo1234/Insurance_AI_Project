from django.contrib import admin
from django.urls import path
from recommender import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.home, name='home'),
    path('login/', views.login_page, name='login_page'),
    path('register/', views.register_page, name='register_page'),
    path('logout/', views.logout_user, name='logout_user'),
    path('delete-history/<int:id>/', views.delete_history, name='delete_history'),
    # হিস্ট্রি দেখার নতুন ইউআরএল
    path('view-history/<int:id>/', views.view_history, name='view_history'),
]