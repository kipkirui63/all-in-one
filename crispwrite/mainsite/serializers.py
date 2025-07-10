
from rest_framework import serializers
from .models import NewsletterSubscription, ContactMessage, Meeting

class NewsletterSubscriptionSerializer(serializers.ModelSerializer):
    class Meta:
        model = NewsletterSubscription
        fields = ['id', 'email', 'first_name', 'last_name', 'subscribed_at']

class ContactMessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContactMessage
        fields = ['id', 'name', 'email', 'phone', 'message', 'created_at']

class MeetingSerializer(serializers.ModelSerializer):
    class Meta:
        model = Meeting
        fields = [
            'id', 'name', 'email', 'phone', 'company', 'meeting_type',
            'preferred_date', 'duration', 'timezone', 'description', 'status',
            'google_meet_link', 'calendar_event_id', 'created_at', 'updated_at'
        ]
