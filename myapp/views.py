from django.urls import reverse_lazy
from django.contrib.auth.views import LoginView, LogoutView
from django.contrib.auth.mixins import LoginRequiredMixin

from django.views.generic import CreateView, DetailView, ListView, UpdateView, DeleteView
from .models import User, Account, Card
from .forms import RegisterForm, AccountForm, CardForm
from django.contrib.auth import login

from django.views.generic import FormView, ListView
from django.db import transaction

from .models import User, Account, Card, Transaction
from .forms import TransferForm, CheckPhoneForm, CheckCardForm

class RegisterView(CreateView):
    model = User
    form_class = RegisterForm
    template_name = 'register.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        login(self.request, self.object)
        return response

    def get_success_url(self):
        return reverse_lazy('account_create')

class Login(LoginView):
    template_name = 'login.html'
    next_page = 'account'

class Logout(LoginView):
    next_page = 'login'



class AccountCreateView(LoginRequiredMixin, CreateView):
    model = Account
    form_class = AccountForm
    template_name = 'account_form.html'
    success_url = reverse_lazy('account')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    
class AccountDetailView(LoginRequiredMixin, DetailView):
    model = Account
    template_name = 'account_detail.html'
    context_object_name = 'account'

    def get_object(self, queryset = None):
        return Account.objects.get(user = self.request.user)

class AccountUpdateView(LoginRequiredMixin, UpdateView):
    model = Account
    form_class = AccountForm
    template_name = 'account_form.html'
    success_url = reverse_lazy('account')

    def get_object(self, queryset = None):
        return Account.objects.get(user = self.request.user)

class CardListView(LoginRequiredMixin, ListView):
    model = Card
    template_name = 'card_list.html'
    context_object_name = 'cards'

    def get_queryset(self):
        return Card.objects.filter(account__user = self.request.user)

class CardDetailView(LoginRequiredMixin, DetailView):
    model = Card
    template_name = 'card_detail.html'
    context_object_name = 'card'

    def get_queryset(self):
        return Card.objects.filter(account__user = self.request.user)

class CardCreateView(LoginRequiredMixin, CreateView):
    model = Card
    form_class = CardForm
    template_name = 'card_form.html'
    success_url = reverse_lazy('card_list')

    def form_valid(self, form):
        form.instance.account = self.request.user.account
        return super().form_valid(form)


class CardUpdateView(LoginRequiredMixin, UpdateView):
    model = Card
    form_class = CardForm
    template_name = 'card_form.html'
    success_url = reverse_lazy('card_list')

    def get_queryset(self):
        return Card.objects.filter(account__user = self.request.user)


class CardDeleteView(DeleteView):
    model = Card
    template_name = 'card_confirm_delete.html'
    success_url = reverse_lazy('card_list')

    def get_queryset(self):
        return Card.objects.filter(account__user = self.request.user)

    
class TransferView(LoginRequiredMixin, FormView):
    template_name = 'transfer.html'
    form_class = TransferForm
    success_url = reverse_lazy('transaction_history')

    def get_form(self, form_class=None):
        form = super().get_form(form_class)

        form.fields['source_card'].queryset = Card.objects.filter(
            account__user=self.request.user
        )

        return form

    def form_valid(self, form):
        source_type = form.cleaned_data['source_type']
        source_card = form.cleaned_data['source_card']

        send_by = form.cleaned_data['send_by']
        receiver = form.cleaned_data['receiver']
        amount = form.cleaned_data['amount']

        if amount <= 0:
            form.add_error('amount', 'Amount must be greater than 0')
            return self.form_invalid(form)

    
        if source_type == 'account':
            source = self.request.user.account

        else:
            if source_card is None:
                form.add_error('source_card', 'Choose a card')
                return self.form_invalid(form)

            if source_card.account.user != self.request.user:
                form.add_error('source_card', 'This is not your card')
                return self.form_invalid(form)

            source = source_card

        if send_by == 'phone':

            try:
                receiver_user = User.objects.get(
                    phone_number=receiver
                )

                destination = receiver_user.account

            except (User.DoesNotExist, Account.DoesNotExist):
                form.add_error('receiver', 'User not found')
                return self.form_invalid(form)

            receiver_card = None

        else:

            try:
                receiver_card = Card.objects.get(
                    card_number=receiver
                )

                destination = receiver_card
                receiver_user = receiver_card.account.user

            except Card.DoesNotExist:
                form.add_error('receiver', 'Card not found')
                return self.form_invalid(form)

        if source.balance < amount:
            form.add_error('amount', 'Not enough money')
            return self.form_invalid(form)

        with transaction.atomic():

            source.balance -= amount
            destination.balance += amount

            source.save()
            destination.save()

            Transaction.objects.create(
                sender=self.request.user,
                receiver=receiver_user,

                source_card=source_card
                if source_type == 'card'
                else None,

                receiver_card=receiver_card,

                amount=amount
            )

        return super().form_valid(form)


class TransactionHistoryView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = 'transaction_history.html'
    context_object_name = 'transactions'

    def get_queryset(self):
        filter_type = self.request.GET.get('filter', 'all')

        if filter_type == 'sent':
            return Transaction.objects.filter(
                sender=self.request.user
            ).order_by('-created_at')

        elif filter_type == 'received':
            return Transaction.objects.filter(
                receiver=self.request.user
            ).order_by('-created_at')

        return (
    Transaction.objects.filter(sender=self.request.user)
    | Transaction.objects.filter(receiver=self.request.user)
).order_by('-created_at')



class CardTransactionHistoryView(LoginRequiredMixin, ListView):
    model = Transaction
    template_name = 'card_transaction_history.html'
    context_object_name = 'transactions'

    def get_queryset(self):
        card = Card.objects.get(
            pk=self.kwargs['pk'],
            account__user=self.request.user
        )

        filter_type = self.request.GET.get('filter', 'all')

        if filter_type == 'sent':
            return Transaction.objects.filter(
                source_card=card
            ).order_by('-created_at')

        elif filter_type == 'received':
            return Transaction.objects.filter(
                receiver_card=card
            ).order_by('-created_at')

        return (
            Transaction.objects.filter(source_card=card)
            | Transaction.objects.filter(receiver_card=card)
        ).order_by('-created_at')



class CheckPhoneView(LoginRequiredMixin, FormView):
    template_name = 'check_phone.html'
    form_class = CheckPhoneForm

    def form_valid(self, form):
        phone_number = form.cleaned_data['phone_number']

        try:
            user = User.objects.get(
                phone_number=phone_number
            )

            account = user.account

            self.extra_context = {
                'form': form,
                'found': True,
                'account': account
            }

        except (User.DoesNotExist, Account.DoesNotExist):

            self.extra_context = {
                'form': form,
                'found': False
            }

        return self.render_to_response(
            self.get_context_data()
        )



class CheckCardView(LoginRequiredMixin, FormView):
    template_name = 'check_card.html'
    form_class = CheckCardForm

    def form_valid(self, form):
        card_number = form.cleaned_data['card_number']

        try:
            card = Card.objects.get(
                card_number=card_number
            )

            self.extra_context = {
                'form': form,
                'found': True,
                'account': card.account
            }

        except Card.DoesNotExist:

            self.extra_context = {
                'form': form,
                'found': False
            }

        return self.render_to_response(
            self.get_context_data()
        )