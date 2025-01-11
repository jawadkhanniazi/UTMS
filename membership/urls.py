from django.urls import path

from membership import views
urlpatterns = [
    path('membership/add/', views.add_membership, name='add_membership'),
    path('membership/list/', views.list_membership, name='list_membership'),
    path('membership/list/<int:id>/', views.list_single_membership, name='list_membership'),
    path('membership/edit/<int:id>/', views.edit_membership, name='edit_membership'),
    path('membership/add-attechment/<int:id>/', views.add_attechment, name='add_attechment'),
    path('membership/add-remarks/<int:id>/', views.add_remarks, name='add_remarks'),
    path('membership/search/', views.search_membership, name='search_membership'), 
]
