
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, ListView, DeleteView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404
from django.contrib import messages
from .models import *
from .forms import *
from books.models import Book
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.utils import timezone

class BorrowBookView(LoginRequiredMixin, CreateView):
    model = Borrow
    form_class = BorrowForm
    template_name = 'borrow/borrow_form.html'
    success_url = reverse_lazy('borrow:borrow_list')

    def get_initial(self):
        initial = super().get_initial()
        book_id = self.request.GET.get('book')
        if book_id:
            initial['book'] = book_id
        return initial

    def form_valid(self, form):
        # Enforce that a user may have at most 3 active borrows.
        active_borrows = Borrow.objects.filter(user=self.request.user, returned=False).count()
        if active_borrows >= 3:
            form.add_error(None, "You have already borrowed 3 books. Please return one before borrowing another.")
            return self.form_invalid(form)

        form.instance.user = self.request.user
        book = form.instance.book
        if book.available_copies < 1:
            form.add_error('book', "This book is currently not available.")
            return self.form_invalid(form)
        # Decrease available copies.
        book.available_copies -= 1
        book.save()
        messages.success(self.request, "You have borrowed the book. Please return it within 14 days!")
        return super().form_valid(form)

class BorrowListView(LoginRequiredMixin, ListView):
    model = BorrowRequest
    template_name = 'borrow/borrow_list.html'
    context_object_name = 'borrows'

    def get_queryset(self):
        return BorrowRequest.objects.filter(user=self.request.user).exclude(status='draft').order_by('-requested_on')


# Allow users to cancel (remove) an active borrow.
class BorrowCancelView(LoginRequiredMixin, DeleteView):
    model = Borrow
    template_name = 'borrow/borrow_cancel_confirm.html'
    success_url = reverse_lazy('borrow:borrow_list')

    def get_queryset(self):
        # Only allow cancellation of active (not returned) borrows for the current user.
        return Borrow.objects.filter(user=self.request.user, returned=False)

    def delete(self, request, *args, **kwargs):
        self.object = self.get_object()
        # Return the book copy.
        book = self.object.book
        book.available_copies += 1
        book.save()
        return super().delete(request, *args, **kwargs)

# For superusers to mark a borrow as returned.
class SuperuserRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser

class BorrowReturnUpdateView(SuperuserRequiredMixin, UpdateView):
    model = Borrow
    fields = ['returned']
    template_name = 'borrow/borrow_return_form.html'
    success_url = reverse_lazy('dashboard:dashboard')

class SuperuserRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser

class BorrowMarkReturnedView(SuperuserRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        # Use BorrowRequest model instead of Borrow.
        req = get_object_or_404(BorrowRequest, pk=kwargs.get('pk'), status='approved', returned=False)
        # Mark the request as returned.
        req.returned = True
        req.save()
        # Increment the book's available copies.
        book = req.book
        book.available_copies += 1
        book.save()
        messages.success(request, f"Borrow request for '{req.book.title}' has been marked as returned.")
        return HttpResponseRedirect(reverse('dashboard:dashboard'))





# --- User View to Request a Borrow ---
class RequestBorrowView(LoginRequiredMixin, CreateView):
    model = BorrowRequest
    form_class = BorrowRequestForm
    template_name = 'borrow/borrow_request_form.html'
    success_url = reverse_lazy('borrow:request_list')

    def form_valid(self, form):
        # Enforce that a user cannot have more than 3 pending requests.
        pending_count = BorrowRequest.objects.filter(user=self.request.user, status='pending').count()
        if pending_count >= 3:
            form.add_error(None, "You already have 3 pending borrow requests. Please wait for them to be processed.")
            return self.form_invalid(form)
        form.instance.user = self.request.user
        messages.success(self.request, "Your borrow request has been submitted.")
        return super().form_valid(form)

class BorrowRequestListView(LoginRequiredMixin, ListView):
    model = BorrowRequest
    template_name = 'borrow/borrow_request_list.html'
    context_object_name = 'requests'

    def get_queryset(self):
        return BorrowRequest.objects.filter(user=self.request.user).order_by('-requested_on')

# --- Superuser Views for Processing Requests ---


class SuperuserRequiredMixin(UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_superuser

class ApproveBorrowRequestView(SuperuserRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        req = get_object_or_404(BorrowRequest, pk=kwargs.get('pk'), status='pending')
        book = req.book
        if book.available_copies < 1:
            messages.error(request, "Not enough copies available to approve this request.")
            req.status = 'rejected'
            req.save()
            return HttpResponseRedirect(reverse('dashboard:dashboard'))
        # Decrease available copies.
        book.available_copies -= 1
        book.save()
        # Approve the request.
        req.status = 'approved'
        req.requested_on = timezone.now()
        req.return_date = timezone.now().date() + timedelta(days=14)
        req.save()
        messages.success(request, f"Borrow request for '{req.book.title}' has been approved.")
        return HttpResponseRedirect(reverse('dashboard:dashboard'))

class RejectBorrowRequestView(SuperuserRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        req = get_object_or_404(BorrowRequest, pk=kwargs.get('pk'), status='pending')
        req.status = 'rejected'
        req.save()
        messages.info(request, f"Borrow request for '{req.book.title}' has been rejected.")
        return HttpResponseRedirect(reverse('dashboard:dashboard'))




class AddBorrowRequestView(LoginRequiredMixin, CreateView):
    model = BorrowRequest
    form_class = BorrowRequestForm
    template_name = 'borrow/borrow_request_add.html'
    success_url = reverse_lazy('borrow:request_cart')

    def form_valid(self, form):
        form.instance.user = self.request.user
        # Enforce maximum 3 draft items.
        draft_count = BorrowRequest.objects.filter(user=self.request.user, status='draft').count()
        if draft_count >= 3:
            form.add_error(None, "You cannot add more than 3 books to your borrow cart.")
            return self.form_invalid(form)
        # (Optionally) prevent duplicates in draft.
        if BorrowRequest.objects.filter(user=self.request.user, book=form.instance.book, status='draft').exists():
            form.add_error('book', "This book is already in your borrow cart.")
            return self.form_invalid(form)
        return super().form_valid(form)

class BorrowRequestCartView(LoginRequiredMixin, ListView):
    model = BorrowRequest
    template_name = 'borrow/borrow_request_cart.html'
    context_object_name = 'requests'

    def get_queryset(self):
        # Show only draft items (in cart)
        return BorrowRequest.objects.filter(user=self.request.user, status='draft').order_by('-id')

class SubmitBorrowRequestView(LoginRequiredMixin, View):
    def post(self, request, *args, **kwargs):
        drafts = BorrowRequest.objects.filter(user=request.user, status='draft')
        if not drafts.exists():
            messages.error(request, "Your borrow cart is empty.")
            return HttpResponseRedirect(reverse('borrow:request_cart'))
        # Update all drafts to pending and set the requested_on timestamp.
        drafts.update(status='pending', requested_on=timezone.now())
        messages.success(request, "Your borrow request has been sent for approval.")
        return HttpResponseRedirect(reverse('borrow:request_cart'))

class CancelBorrowRequestView(LoginRequiredMixin, DeleteView):
    model = BorrowRequest
    template_name = 'borrow/borrow_request_cancel_confirm.html'
    success_url = reverse_lazy('borrow:request_cart')

    def get_queryset(self):
        # Only allow deletion of draft items.
        return BorrowRequest.objects.filter(user=self.request.user, status='draft')

class AddToBorrowCartView(LoginRequiredMixin, View):
    def get(self, request, pk, *args, **kwargs):
        book = get_object_or_404(Book, pk=pk)
        # Count active approved requests (not returned)
        active_count = BorrowRequest.objects.filter(user=request.user, status='approved', returned=False).count()
        # Count draft (cart) items
        draft_count = BorrowRequest.objects.filter(user=request.user, status='draft').count()
        if (active_count + draft_count) >= 3:
            messages.error(request, "You cannot have more than 3 books (active + in cart) at once.")
            return HttpResponseRedirect(reverse('borrow:request_cart'))
        if BorrowRequest.objects.filter(user=request.user, book=book, status='draft').exists():
            messages.info(request, "This book is already in your borrow cart.")
            return HttpResponseRedirect(reverse('borrow:request_cart'))
        BorrowRequest.objects.create(user=request.user, book=book, status='draft')
        messages.success(request, f"'{book.title}' has been added to your borrow cart.")
        return HttpResponseRedirect(reverse('borrow:request_cart'))