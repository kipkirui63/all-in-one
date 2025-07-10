
from django.urls import path
from . import views

urlpatterns = [
    path("register/", views.register, name="register"),
    path("login/", views.login, name="login"),
    path("activate/<uidb64>/<token>/", views.activate, name="activate"),
    path("stripe/create-checkout/", views.create_checkout, name="create-checkout"),
    path("stripe/webhook/", views.stripe_webhook, name="stripe-webhook"),
    path("auth/check-subscription/", views.check_subscription, name="check-subscription"),
    path("agent/gateway/", views.agent_gateway, name="agent-gateway"),
    path("tools/", views.list_tools, name="list-tools"),
    path('cancel-subscription/', views.cancel_subscription, name='cancel-subscription'),
    path('my-subscriptions/', views.my_subscriptions, name='my-subscriptions'),
]
