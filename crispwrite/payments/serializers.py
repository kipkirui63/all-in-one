
from rest_framework import serializers
from django.contrib.auth import authenticate
from .models import User, Tool, Subscription

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField()

class ToolSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tool
        fields = ['id', 'name', 'description', 'price_id', 'is_active']

class SubscriptionSerializer(serializers.ModelSerializer):
    tool_name = serializers.CharField(source='tool.name', read_only=True)
    
    class Meta:
        model = Subscription
        fields = ['id', 'tool', 'tool_name', 'status', 'created_at', 'updated_at']
