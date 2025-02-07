
from django.db import models
from django.contrib.auth import get_user_model
from books.models import Book
from django.utils import timezone
from datetime import timedelta

User = get_user_model()

class Borrow(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey(Book, on_delete=models.CASCADE)
    borrowed_on = models.DateTimeField(auto_now_add=True)
    # Automatically set to 14 days after borrow date.
    return_date = models.DateField(blank=True, null=True)
    # Only a superuser can later mark this as returned.
    returned = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        # On first creation, auto-set the return date if not provided.
        if not self.pk and not self.return_date:
            self.return_date = (timezone.now().date() + timedelta(days=14))
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user.username} borrowed {self.book.title}"


class BorrowRequest(models.Model):
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    book = models.ForeignKey('books.Book', on_delete=models.CASCADE)
    requested_on = models.DateTimeField(null=True, blank=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='draft')
    returned = models.BooleanField(default=False)
    return_date = models.DateField(null=True, blank=True)  # New field

    def __str__(self):
        return f"{self.user.username} - {self.book.title} ({self.get_status_display()})"