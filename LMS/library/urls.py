from django.urls import path, include
from .views import *

urlpatterns = [
    path('', book_list, name='book_list'),
    path('books/add/', create_book, name='create_book'),
    path('books/update/<int:pk>/', update_book, name='update_book'),
    path('books/delete/<int:pk>/', delete_book, name='delete_book'),

    path('books/issue/<int:book_id>/',issue_book, name='issue_book'),
    path('books/return/<int:transaction_id>/',return_book, name='return_book'),
    path('books/search/', search_books, name='search_books'),
    
    path('members/', member_list, name='member_list'),
    path('members/add/', create_member, name='create_member'),
    path('members/<int:member_id>/delete/', delete_member, name='delete_member'),

]
