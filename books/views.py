from django.urls import reverse_lazy
from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.contrib.auth.mixins import UserPassesTestMixin
from django.core.exceptions import PermissionDenied
from .models import Book
from django.core.paginator import Paginator
from django.db.models import Q


class BookListView(ListView):
    model = Book
    template_name = 'books/book_list.html'
    context_object_name = 'books'
    paginate_by = 20  # 20 books per page
    # for search box ( you can use it anywhere)
    def get_queryset(self):
        qs = super().get_queryset().order_by('title')  # explicit ordering
        q = self.request.GET.get('q')
        if q:
            qs = qs.filter(Q(title__icontains=q) | Q(author__icontains=q))
        return qs
    # for pagination you can use it anywhere
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        products = self.get_queryset()
        page_number = self.request.GET.get('page', 1)  # Get current page, default to 1
        paginator = Paginator(products, self.paginate_by)
        current_page = paginator.get_page(page_number)

        context['current_page'] = current_page.number
        context['total_pages'] = paginator.num_pages

        return context


class BookDetailView(DetailView):
    model = Book
    template_name = 'books/book_detail.html'
# Create a mixin that allows only superusers to pass.
class SuperuserRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        raise PermissionDenied(self.get_permission_denied_message())
class BookCreateView(SuperuserRequiredMixin, CreateView):
    model = Book
    fields = ['title', 'author', 'isbn', 'total_copies', 'available_copies']
    template_name = 'books/book_form.html'
    success_url = reverse_lazy('books:book_list')
class BookUpdateView(SuperuserRequiredMixin, UpdateView):
    model = Book
    fields = ['title', 'author', 'isbn', 'total_copies', 'available_copies']
    template_name = 'books/book_form.html'
    success_url = reverse_lazy('books:book_list')
class BookDeleteView(SuperuserRequiredMixin, DeleteView):
    model = Book
    template_name = 'books/book_confirm_delete.html'
    success_url = reverse_lazy('books:book_list')
