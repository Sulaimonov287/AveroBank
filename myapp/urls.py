from django.urls import path
from .views import RegisterView, Login, Logout, AccountCreateView, AccountDetailView, AccountUpdateView ,CardListView, CardDetailView, CardCreateView, CardUpdateView, CardDeleteView
from .views import TransferView, TransactionHistoryView, CardTransactionHistoryView, CheckPhoneView, CheckCardView


urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', Login.as_view(), name='login'),
    path('logout/', Logout.as_view(), name='logout'),
    path('account/create/', AccountCreateView.as_view(), name='account_create'),
    path('account/', AccountDetailView.as_view(), name='account'),
    path('account/update/', AccountUpdateView.as_view(), name='account_update'),
    path('cards/', CardListView.as_view(), name='card_list'),
    path('cards/create/', CardCreateView.as_view(), name='card_create'),
    path('cards/<int:pk>/', CardDetailView.as_view(), name='card_detail'),
    path('cards/<int:pk>/update/', CardUpdateView.as_view(), name='card_update'),
    path('cards/<int:pk>/delete/', CardDeleteView.as_view(), name='card_delete'),
    path('transfer/', TransferView.as_view(), name='transfer'),
    path('transactions/', TransactionHistoryView.as_view(), name='transaction_history'),
    path('cards/<int:pk>/transactions/', CardTransactionHistoryView.as_view(), name='card_transaction_history'),
    path('check/phone/', CheckPhoneView.as_view(), name='check_phone'),
    path('check/card/', CheckCardView.as_view(), name='check_card'),
]