
from django.urls import path
from . import views

urlpatterns = [
    path('newsletter/subscribe', views.newsletter_subscribe, name='newsletter-subscribe'),
    path('contact/submit', views.contact_submit, name='contact-submit'),
    path('meetings/book', views.book_meeting, name='book-meeting'),
    path('meetings', views.get_meetings, name='get-meetings'),
    path('meetings/<int:meeting_id>', views.get_meeting, name='get-meeting'),
    path('meetings/<int:meeting_id>', views.update_meeting, name='update-meeting'),
    path('meetings/<int:meeting_id>', views.delete_meeting, name='delete-meeting'),
    path('chat', views.chat, name='chat'),
    path('chat/session', views.chat_session, name='chat-session'),
    path('health', views.health, name='health'),
]
