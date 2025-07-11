import openai
import json
from datetime import datetime, timedelta
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from rest_framework import status
from .models import NewsletterSubscription, ContactMessage, Meeting, ChatSession, ChatMessage
from .serializers import NewsletterSubscriptionSerializer, ContactMessageSerializer, MeetingSerializer
import uuid
import time
from django.shortcuts import render

openai.api_key = settings.OPENAI_API_KEY

CRISPAI_CONTEXT = """
You are CrispAI's customer support assistant. CrispAI is an AI solutions company that empowers businesses with AI-driven automation and insights.

IMPORTANT CONVERSATION RULES:
- Keep responses short and precise (1-2 sentences maximum)
- At the start of a NEW conversation, ask: "Hi! I'm here to help with CrispAI. Could I get your name and email for personalized assistance?"
- When someone asks to book a session/meeting/demo or shows interest in scheduling, IMMEDIATELY respond: "Please visit our contact page to schedule your meeting: https://crispai.ca/contact"
- Do NOT ask for dates, times, preferences, or contact details when booking - just provide the link
- Be brief and direct - avoid lengthy explanations or multiple questions

ABOUT CRISPAI:
- Mission: Empowering businesses through AI-driven automation and insights
- Vision: To be the leading provider of accessible AI solutions that transform how businesses operate
- Location: Ottawa, Canada
- Contact: info@crispai.ca, +1 (343) 580-1393

OUR SERVICES:
1. AI for Sales - Transform your sales process with intelligent lead scoring, automated follow-ups, and predictive analytics
2. AI for Marketing - Revolutionize your marketing campaigns with personalized content, customer segmentation, and campaign optimization
3. AI for Customer Support - Enhance customer satisfaction with intelligent chatbots, automated ticket routing, and sentiment analysis
4. AI for Operations - Streamline business operations with process automation, predictive maintenance, and supply chain optimization
5. AI for HR - Modernize human resources with automated recruiting, employee engagement analysis, and performance predictions
6. AI for IT - Optimize IT infrastructure with automated monitoring, predictive issue resolution, and intelligent resource allocation
7. AI for Nonprofits - Empower nonprofits with donor insights, volunteer management, and impact measurement tools
8. AI for Manufacturing - Enhance production with quality control automation, predictive maintenance, and supply chain optimization
9. AI for Healthcare - Improve patient care with diagnostic assistance, treatment optimization, and administrative automation
10. AI for Retail - Boost sales with inventory optimization, customer behavior analysis, and personalized recommendations
11. AI for Education - Transform learning with personalized education, automated grading, and student performance analytics
12. AI for Government - Improve public services with citizen service automation, policy analysis, and resource optimization

MARKETPLACE:
CrispAI Marketplace offers specialized AI applications to enhance business operations:

1. Business Intelligence Agent ($19.99/month)
   - Advanced AI-powered analytics platform
   - Real-time dashboards and predictive modeling
   - Transforms data into actionable insights
   - 7-day free trial available
   - URL: https://businessagent.crispai.ca/

2. AI Recruitment Assistant ($19.99/month)
   - Streamlines hiring process with AI-powered candidate screening
   - Interview scheduling and talent matching algorithms
   - Automated candidate evaluation
   - 7-day free trial available
   - URL: https://workflow.getmindpal.com/67751ba8f77a6fddb63cd44e

3. CrispWrite ($89.99/month)
   - Professional writing assistant for compelling content
   - AI-powered grammar and style suggestions
   - Handles emails, reports, and various content types
   - 7-day free trial available
   - URL: https://crispwrite.crispai.ca/

4. SOP Assistant ($19.99/month)
   - Create, manage, and optimize Standard Operating Procedures
   - Intelligent templates and collaborative editing
   - Process documentation and optimization
   - 7-day free trial available
   - URL: https://workflow.getmindpal.com/sop-agent-workflow-avlkgrhad7x0xazm

5. Resume Analyzer ($19.99/month)
   - Advanced resume screening tool
   - Evaluates candidates against job requirements
   - Detailed scoring and recommendations
   - 7-day free trial available
   - URL: https://workflow.getmindpal.com/67751e695156e8aaefc0c8de

MEETING TYPES:
- AI Consultation (30 min) - Discuss your AI needs and explore opportunities
- Product Demo (45 min) - See our AI solutions in action
- Strategy Session (60 min) - Deep dive into AI strategy for your business
- Technical Support (30 min) - Get help with existing implementations

CONTACT INFORMATION:
- Main Email: info@crispai.ca
- Support Email: support@crispai.ca
- Phone: +1 (343) 580-1393
- Website: https://crispai.ca
- Marketplace: https://marketplace.crispai.ca

GUIDELINES:
- Give extremely brief answers (1-2 sentences maximum)
- For ANY booking/meeting/demo request, immediately provide link: https://crispai.ca/contact
- Do NOT ask follow-up questions about booking details - just give the link
- Avoid lengthy explanations or multiple questions
- For detailed information, direct to contact page or support@crispai.ca
- If you don't have a specific answer, direct users to support@crispai.ca
- Be efficient - get to the point immediately
"""

@api_view(['POST'])
@permission_classes([AllowAny])
def newsletter_subscribe(request):
    try:
        data = json.loads(request.body)
        email = data.get('email')
        subscription, created = NewsletterSubscription.objects.get_or_create(email=email)
        if created:
            return Response({'message': 'Subscribed successfully'}, status=status.HTTP_201_CREATED)
        return Response({'message': 'Already subscribed'}, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def contact_submit(request):
    try:
        data = json.loads(request.body)
        contact = ContactMessage.objects.create(
            name=data.get('name'),
            email=data.get('email'),
            message=data.get('message')
        )
        return Response({'message': 'Message sent successfully'}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def book_meeting(request):
    try:
        data = json.loads(request.body)
        meeting = Meeting.objects.create(
            name=data.get('name', 'Test User'),
            email=data.get('email', 'test@example.com'),
            meeting_type=data.get('meeting_type', 'AI Consultation'),
            preferred_date=data.get('preferred_date', data.get('scheduled_time')),
            timezone=data.get('timezone', 'UTC'),
            description=data.get('description', ''),
            phone=data.get('phone', ''),
            company=data.get('company', '')
        )
        return Response({'message': 'Meeting booked successfully', 'id': meeting.id}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_meetings(request):
    meetings = Meeting.objects.all()
    return Response([{
        'id': m.id,
        'name': m.name,
        'email': m.email,
        'meeting_type': m.meeting_type,
        'preferred_date': m.preferred_date,
        'description': m.description,
        'status': m.status,
        'created_at': m.created_at
    } for m in meetings])

@api_view(['GET'])
@permission_classes([AllowAny])
def get_meeting(request, meeting_id):
    try:
        meeting = Meeting.objects.get(id=meeting_id)
        return Response({
            'id': meeting.id,
            'name': meeting.name,
            'email': meeting.email,
            'meeting_type': meeting.meeting_type,
            'preferred_date': meeting.preferred_date,
            'description': meeting.description,
            'status': meeting.status,
            'created_at': meeting.created_at
        })
    except Meeting.DoesNotExist:
        return Response({'error': 'Meeting not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['PUT'])
@permission_classes([AllowAny])
def update_meeting(request, meeting_id):
    try:
        meeting = Meeting.objects.get(id=meeting_id)
        data = json.loads(request.body)
        meeting.name = data.get('name', meeting.name)
        meeting.email = data.get('email', meeting.email)
        meeting.meeting_type = data.get('meeting_type', meeting.meeting_type)
        meeting.preferred_date = data.get('preferred_date', meeting.preferred_date)
        meeting.description = data.get('description', meeting.description)
        meeting.status = data.get('status', meeting.status)
        meeting.save()
        return Response({'message': 'Meeting updated successfully'})
    except Meeting.DoesNotExist:
        return Response({'error': 'Meeting not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_meeting(request, meeting_id):
    try:
        meeting = Meeting.objects.get(id=meeting_id)
        meeting.delete()
        return Response({'message': 'Meeting deleted successfully'})
    except Meeting.DoesNotExist:
        return Response({'error': 'Meeting not found'}, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([AllowAny])
def chat(request):
    try:
        data = json.loads(request.body)
        message = data.get('message')
        # Basic chat response
        return Response({'response': f'Echo: {message}'})
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def chat_session(request):
    sessions = ChatSession.objects.all()
    return Response([{
        'id': s.id,
        'created_at': s.created_at
    } for s in sessions])

@api_view(['GET'])
@permission_classes([AllowAny])
def health(request):
    return Response({'status': 'healthy'})

def send_contact_form_email(contact_data):
    subject = 'New Contact Form Submission - CrispAI Website'
    html_content = f"""
    <h2>New Contact Form Submission</h2>
    <div style="font-family: Arial, sans-serif; line-height: 1.6;">
        <p><strong>Name:</strong> {contact_data['name']}</p>
        <p><strong>Email:</strong> {contact_data['email']}</p>
        <p><strong>Phone:</strong> {contact_data.get('phone', 'Not provided')}</p>
        <p><strong>Message:</strong></p>
        <div style="background-color: #f5f5f5; padding: 15px; border-left: 4px solid #007bff; margin: 10px 0;">
            {contact_data['message'].replace(chr(10), '<br>')}
        </div>
        <hr>
        <p style="color: #666; font-size: 12px;">
            This email was sent from the CrispAI website contact form.
        </p>
    </div>
    """
    
    msg = EmailMultiAlternatives(
        subject,
        contact_data['message'],
        settings.DEFAULT_FROM_EMAIL,
        ['crispailtd@gmail.com']
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send()

def send_newsletter_subscription_email(subscription_data):
    subject = 'New Newsletter Subscription - CrispAI Website'
    html_content = f"""
    <h2>New Newsletter Subscription</h2>
    <div style="font-family: Arial, sans-serif; line-height: 1.6;">
        <p><strong>Email:</strong> {subscription_data['email']}</p>
        <p><strong>First Name:</strong> {subscription_data.get('firstName', 'Not provided')}</p>
        <p><strong>Last Name:</strong> {subscription_data.get('lastName', 'Not provided')}</p>
        <p><strong>Subscription Date:</strong> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <hr>
        <p style="color: #666; font-size: 12px;">
            This email was sent from the CrispAI website newsletter subscription form.
        </p>
    </div>
    """
    
    msg = EmailMultiAlternatives(
        subject,
        f"New newsletter subscription from {subscription_data['email']}",
        settings.DEFAULT_FROM_EMAIL,
        ['crispailtd@gmail.com']
    )
    msg.attach_alternative(html_content, "text/html")
    msg.send()

def send_meeting_confirmation_email(meeting):
    # Implementation for meeting confirmation email
    # Similar to the original Node.js implementation
    pass

def send_meeting_reschedule_email(meeting):
    # Implementation for meeting reschedule email
    # Similar to the original Node.js implementation
    pass