from django.urls import path
from .views import *

app_name = 'borrow'

urlpatterns = [
    path('request/add/<int:pk>/', AddToBorrowCartView.as_view(), name='add_to_cart'),
    path('request/create/', RequestBorrowView.as_view(), name='borrow_request'),
    path('request/list/', BorrowRequestListView.as_view(), name='request_list'),
    path('request/add/', AddBorrowRequestView.as_view(), name='request_add'),
    path('request/cart/', BorrowRequestCartView.as_view(), name='request_cart'),
    path('request/submit/', SubmitBorrowRequestView.as_view(), name='request_submit'),
    path('request/cancel/<int:pk>/', CancelBorrowRequestView.as_view(), name='request_cancel'),
    path('request/approve/<int:pk>/', ApproveBorrowRequestView.as_view(), name='approve_request'),
    path('request/reject/<int:pk>/', RejectBorrowRequestView.as_view(), name='reject_request'),
    path('create/', BorrowBookView.as_view(), name='borrow_book'),
    path('list/', BorrowListView.as_view(), name='borrow_list'),
    path('cancel/<int:pk>/', BorrowCancelView.as_view(), name='borrow_cancel'),
    path('return/<int:pk>/', BorrowReturnUpdateView.as_view(), name='borrow_return'),
    path('mark-returned/<int:pk>/', BorrowMarkReturnedView.as_view(), name='mark_returned'),
]
