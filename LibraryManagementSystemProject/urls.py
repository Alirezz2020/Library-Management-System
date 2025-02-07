from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('accounts.urls')),  # From your previous proj.
    path('books/', include('books.urls', namespace='books')),
    path('borrow/', include('borrow.urls', namespace='borrow')),
    path('dashboard/', include('dashboard.urls', namespace='dashboard')),
    path('', include('books.urls', namespace='books')),  # Optionally, set a default.
]
