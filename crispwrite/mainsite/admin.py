
from django.contrib import admin
from .models import NewsletterSubscription, ContactMessage, Meeting, ChatSession, ChatMessage

admin.site.register(NewsletterSubscription)
admin.site.register(ContactMessage)
admin.site.register(Meeting)
admin.site.register(ChatSession)
admin.site.register(ChatMessage)
