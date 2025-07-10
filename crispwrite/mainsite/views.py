
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
        email = request.data.get('email')
        first_name = request.data.get('firstName')
        last_name = request.data.get('lastName')

        if not email:
            return Response({'message': 'Email is required'}, status=status.HTTP_400_BAD_REQUEST)

        # Check if email already exists
        if NewsletterSubscription.objects.filter(email=email).exists():
            return Response({
                'message': 'This email is already subscribed to our newsletter.'
            }, status=status.HTTP_409_CONFLICT)

        subscription = NewsletterSubscription.objects.create(
            email=email,
            first_name=first_name,
            last_name=last_name
        )

        # Send email notification
        try:
            send_newsletter_subscription_email({
                'email': email,
                'firstName': first_name,
                'lastName': last_name
            })
        except Exception as e:
            print(f"Failed to send newsletter subscription email: {e}")

        return Response({
            'message': 'Successfully subscribed to newsletter!',
            'subscription': {
                'id': subscription.id,
                'email': subscription.email,
                'firstName': subscription.first_name,
                'lastName': subscription.last_name
            }
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({
            'message': 'An error occurred while processing your subscription.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def contact_submit(request):
    try:
        name = request.data.get('name')
        email = request.data.get('email')
        phone = request.data.get('phone')
        message = request.data.get('message')

        if not all([name, email, message]):
            return Response({
                'message': 'Name, email, and message are required'
            }, status=status.HTTP_400_BAD_REQUEST)

        contact_message = ContactMessage.objects.create(
            name=name,
            email=email,
            phone=phone,
            message=message
        )

        # Send email notification
        try:
            send_contact_form_email({
                'name': name,
                'email': email,
                'phone': phone,
                'message': message
            })
        except Exception as e:
            print(f"Failed to send contact form email: {e}")

        return Response({
            'message': "Thank you for your message! We'll get back to you soon.",
            'contactMessage': {
                'id': contact_message.id,
                'name': contact_message.name,
                'email': contact_message.email
            }
        }, status=status.HTTP_201_CREATED)

    except Exception as e:
        return Response({
            'message': 'An error occurred while processing your message.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def book_meeting(request):
    try:
        data = request.data.copy()
        
        # Convert preferredDate string to datetime
        if 'preferredDate' in data:
            data['preferredDate'] = datetime.fromisoformat(data['preferredDate'].replace('Z', '+00:00'))

        serializer = MeetingSerializer(data=data)
        if serializer.is_valid():
            meeting = serializer.save()
            
            # Send meeting confirmation email
            try:
                send_meeting_confirmation_email(meeting)
            except Exception as e:
                print(f"Failed to send meeting confirmation email: {e}")

            return Response({
                'message': 'Meeting booked successfully',
                'meeting': {
                    'id': meeting.id,
                    'meetingType': meeting.meeting_type,
                    'preferredDate': meeting.preferred_date,
                    'duration': meeting.duration,
                    'status': meeting.status
                }
            }, status=status.HTTP_201_CREATED)
        else:
            return Response({
                'message': 'Invalid input data',
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

    except Exception as e:
        return Response({
            'message': 'Failed to book meeting'
        }, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_meetings(request):
    try:
        meetings = Meeting.objects.all()
        serializer = MeetingSerializer(meetings, many=True)
        return Response(serializer.data)
    except Exception as e:
        return Response({
            'message': 'Failed to fetch meetings'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['GET'])
@permission_classes([AllowAny])
def get_meeting(request, meeting_id):
    try:
        meeting = Meeting.objects.get(id=meeting_id)
        serializer = MeetingSerializer(meeting)
        return Response(serializer.data)
    except Meeting.DoesNotExist:
        return Response({
            'message': 'Meeting not found'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['PUT'])
@permission_classes([AllowAny])
def update_meeting(request, meeting_id):
    try:
        meeting = Meeting.objects.get(id=meeting_id)
        data = request.data.copy()
        
        # Convert preferredDate string to datetime if present
        if 'preferredDate' in data:
            data['preferredDate'] = datetime.fromisoformat(data['preferredDate'].replace('Z', '+00:00'))

        serializer = MeetingSerializer(meeting, data=data, partial=True)
        if serializer.is_valid():
            updated_meeting = serializer.save()
            
            # Send reschedule notification if date changed
            if 'preferredDate' in data:
                try:
                    send_meeting_reschedule_email(updated_meeting)
                except Exception as e:
                    print(f"Failed to send reschedule email: {e}")

            return Response({
                'message': 'Meeting updated successfully',
                'meeting': MeetingSerializer(updated_meeting).data
            })
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    except Meeting.DoesNotExist:
        return Response({
            'message': 'Meeting not found'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['DELETE'])
@permission_classes([AllowAny])
def delete_meeting(request, meeting_id):
    try:
        meeting = Meeting.objects.get(id=meeting_id)
        meeting.delete()
        return Response({
            'message': 'Meeting cancelled successfully'
        })
    except Meeting.DoesNotExist:
        return Response({
            'message': 'Meeting not found'
        }, status=status.HTTP_404_NOT_FOUND)

@api_view(['POST'])
@permission_classes([AllowAny])
def chat(request):
    try:
        message = request.data.get('message')
        session_id = request.data.get('sessionId')

        if not message:
            return Response({'error': 'Message is required'}, status=status.HTTP_400_BAD_REQUEST)

        if not session_id:
            session_id = generate_session_id()

        result = handle_chat_message(session_id, message)
        return Response(result)

    except Exception as e:
        print(f"Chat API error: {e}")
        return Response({
            'error': 'Sorry, I\'m experiencing technical difficulties. Please contact our team directly.'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

@api_view(['POST'])
@permission_classes([AllowAny])
def chat_session(request):
    session_id = generate_session_id()
    return Response({'sessionId': session_id})

@api_view(['GET'])
@permission_classes([AllowAny])
def health(request):
    return Response({
        'status': 'ok',
        'timestamp': datetime.now().isoformat()
    })

# Helper functions
def generate_session_id():
    return f"chat_{int(time.time())}_{uuid.uuid4().hex[:9]}"

def handle_chat_message(session_id, user_message):
    try:
        # Get or create chat session
        session, created = ChatSession.objects.get_or_create(session_id=session_id)
        
        # Check if this is the first message
        is_first_message = session.messages.count() == 0
        
        # Add user message
        ChatMessage.objects.create(
            session=session,
            role='user',
            content=user_message
        )

        if is_first_message:
            welcome_response = "Hi! I'm here to help with CrispAI. Could I get your name and email for personalized assistance?"
            
            ChatMessage.objects.create(
                session=session,
                role='assistant',
                content=welcome_response
            )

            return {
                'response': welcome_response,
                'sessionId': session_id
            }

        # Get recent messages for context
        recent_messages = session.messages.order_by('timestamp')[-10:]
        
        messages = [{'role': 'system', 'content': CRISPAI_CONTEXT}]
        for msg in recent_messages:
            messages.append({
                'role': msg.role,
                'content': msg.content
            })

        # Get response from OpenAI
        response = openai.ChatCompletion.create(
            model='gpt-4',
            messages=messages,
            max_tokens=100,
            temperature=0.7
        )

        assistant_response = response.choices[0].message.content

        # Save assistant response
        ChatMessage.objects.create(
            session=session,
            role='assistant',
            content=assistant_response
        )

        return {
            'response': assistant_response,
            'sessionId': session_id
        }

    except Exception as e:
        print(f"Chat error: {e}")
        return {
            'response': "I'm experiencing technical difficulties right now. Please contact our team directly at info@crispai.ca or +1 (343) 580-1393 for immediate assistance.",
            'sessionId': session_id
        }

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
