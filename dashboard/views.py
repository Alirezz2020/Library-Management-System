from django.views.generic import TemplateView
from django.core.paginator import Paginator
from django.db.models import Q
from borrow.models import BorrowRequest
from books.models import Book

class DashboardView(TemplateView):
    template_name = 'dashboard/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.user.is_superuser:
            # Pending requests
            pending_requests = BorrowRequest.objects.filter(status='pending').order_by('-requested_on')
            pending_paginator = Paginator(pending_requests, 20)
            page_requests = self.request.GET.get('page_requests')
            context['requests_page'] = pending_paginator.get_page(page_requests)

            # Active borrows: approved and not returned
            active_borrows = BorrowRequest.objects.filter(status='approved', returned=False).order_by('-requested_on')
            active_search_query = self.request.GET.get('active_search', '')
            if active_search_query:
                active_borrows = active_borrows.filter(
                    Q(user__username__icontains=active_search_query) |
                    Q(book__title__icontains=active_search_query)
                )
            active_paginator = Paginator(active_borrows, 20)
            page_active = self.request.GET.get('page_active')
            context['active_borrows_page'] = active_paginator.get_page(page_active)
            context['active_search_query'] = active_search_query

            # Returned borrows: approved and returned
            returned_borrows = BorrowRequest.objects.filter(status='approved', returned=True).order_by('-requested_on')
            returned_search_query = self.request.GET.get('returned_search', '')
            if returned_search_query:
                returned_borrows = returned_borrows.filter(
                    Q(user__username__icontains=returned_search_query) |
                    Q(book__title__icontains=returned_search_query)
                )
            returned_paginator = Paginator(returned_borrows, 20)
            page_returned = self.request.GET.get('page_returned')
            context['returned_borrows_page'] = returned_paginator.get_page(page_returned)
            context['returned_search_query'] = returned_search_query

            # Books overview pagination (optional)
            books = Book.objects.all().order_by('title')
            books_paginator = Paginator(books, 20)
            page_books = self.request.GET.get('page_books')
            context['books_page'] = books_paginator.get_page(page_books)
        else:
            borrows = BorrowRequest.objects.filter(user=self.request.user).exclude(status='draft').order_by('-requested_on')
            borrow_paginator = Paginator(borrows, 20)
            page = self.request.GET.get('page')
            context['borrow_page'] = borrow_paginator.get_page(page)
            context['profile'] = self.request.user
        return context
