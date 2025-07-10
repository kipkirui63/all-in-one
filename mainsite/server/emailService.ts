import nodemailer from 'nodemailer';
import type { InsertContactMessage, InsertNewsletterSubscription, Meeting } from '@shared/schema';
import dotenv from 'dotenv'
dotenv.config();

// Email configuration
const createTransporter = () => {
  console.log('Creating email transporter with user:', process.env.EMAIL_USER);
  console.log('EMAIL_PASSWORD configured:', !!process.env.EMAIL_PASSWORD);
  
  return nodemailer.createTransport({
    service: 'gmail',
    auth: {
      user: process.env.EMAIL_USER || 'your-email@gmail.com',
      pass: process.env.EMAIL_PASSWORD || 'your-app-password'
    },
    debug: true,
    logger: true
  });
};

export const sendContactFormEmail = async (contactData: InsertContactMessage) => {
  const transporter = createTransporter();
  
  const mailOptions = {
    from: process.env.EMAIL_USER || 'your-email@gmail.com',
    to: 'crispailtd@gmail.com',
    subject: 'New Contact Form Submission - CrispAI Website',
    html: `
      <h2>New Contact Form Submission</h2>
      <div style="font-family: Arial, sans-serif; line-height: 1.6;">
        <p><strong>Name:</strong> ${contactData.name}</p>
        <p><strong>Email:</strong> ${contactData.email}</p>
        <p><strong>Phone:</strong> ${contactData.phone || 'Not provided'}</p>
        <p><strong>Message:</strong></p>
        <div style="background-color: #f5f5f5; padding: 15px; border-left: 4px solid #007bff; margin: 10px 0;">
          ${contactData.message.replace(/\n/g, '<br>')}
        </div>
        <hr>
        <p style="color: #666; font-size: 12px;">
          This email was sent from the CrispAI website contact form.
        </p>
      </div>
    `
  };

  try {
    await transporter.sendMail(mailOptions);
    console.log('Contact form email sent successfully');
  } catch (error) {
    console.error('Error sending contact form email:', error);
    throw error;
  }
};

export const sendNewsletterSubscriptionEmail = async (subscriptionData: InsertNewsletterSubscription) => {
  const transporter = createTransporter();
  
  const mailOptions = {
    from: process.env.EMAIL_USER || 'your-email@gmail.com',
    to: 'crispailtd@gmail.com',
    subject: 'New Newsletter Subscription - CrispAI Website',
    html: `
      <h2>New Newsletter Subscription</h2>
      <div style="font-family: Arial, sans-serif; line-height: 1.6;">
        <p><strong>Email:</strong> ${subscriptionData.email}</p>
        <p><strong>First Name:</strong> ${subscriptionData.firstName || 'Not provided'}</p>
        <p><strong>Last Name:</strong> ${subscriptionData.lastName || 'Not provided'}</p>
        <p><strong>Subscription Date:</strong> ${new Date().toLocaleString()}</p>
        <hr>
        <p style="color: #666; font-size: 12px;">
          This email was sent from the CrispAI website newsletter subscription form.
        </p>
      </div>
    `
  };

  try {
    await transporter.sendMail(mailOptions);
    console.log('Newsletter subscription email sent successfully');
  } catch (error) {
    console.error('Error sending newsletter subscription email:', error);
    throw error;
  }
};

export const sendMeetingConfirmationEmail = async (meeting: Meeting) => {
  const transporter = createTransporter();
  const meetingDate = new Date(meeting.preferredDate);
  const formattedDate = meetingDate.toLocaleDateString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
  const formattedTime = meetingDate.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    timeZoneName: 'short',
  });

  // Create calendar event data
  const startDate = new Date(meeting.preferredDate);
  const endDate = new Date(startDate.getTime() + meeting.duration * 60000);
  
  const calendarEvent = generateCalendarInvite({
    title: `${meeting.meetingType} - ${meeting.name}`,
    description: meeting.description || `Meeting with ${meeting.name} regarding ${meeting.meetingType}`,
    startDate,
    endDate,
    location: 'Google Meet (link will be provided)',
    attendees: [meeting.email, 'crispailtd@gmail.com']
  });

  // Send to customer
  const customerMailOptions = {
    from: process.env.EMAIL_USER || 'your-email@gmail.com',
    to: meeting.email,
    cc: 'crispailtd@gmail.com',
    subject: `Meeting Confirmed - ${meeting.meetingType}`,
    html: `
      <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #2563eb;">Meeting Confirmation</h2>
        <p>Dear ${meeting.name},</p>
        <p>Thank you for booking a meeting with CrispAI. Your ${meeting.meetingType.toLowerCase()} has been confirmed.</p>
        
        <div style="background-color: #f3f4f6; padding: 20px; border-radius: 8px; margin: 20px 0;">
          <h3 style="margin-top: 0;">Meeting Details</h3>
          <p><strong>Type:</strong> ${meeting.meetingType}</p>
          <p><strong>Date:</strong> ${formattedDate}</p>
          <p><strong>Time:</strong> ${formattedTime}</p>
          <p><strong>Duration:</strong> ${meeting.duration} minutes</p>
          <p><strong>Timezone:</strong> ${meeting.timezone}</p>
          ${meeting.company ? `<p><strong>Company:</strong> ${meeting.company}</p>` : ''}
          ${meeting.description ? `<p><strong>Description:</strong> ${meeting.description}</p>` : ''}
        </div>

        <p>A Google Meet link will be sent to you 15 minutes before the meeting.</p>
        <p>If you need to reschedule or cancel, please contact us at least 24 hours in advance.</p>
        
        <p>Best regards,<br>The CrispAI Team</p>
        <p>Email: info@crispai.ca<br>Phone: +1 (343) 580-1393</p>
      </div>
    `,
    attachments: [
      {
        filename: 'meeting.ics',
        content: calendarEvent,
        contentType: 'text/calendar'
      }
    ]
  };

  // Send to admin
  const adminMailOptions = {
    from: process.env.EMAIL_USER || 'your-email@gmail.com',
    to: 'crispailtd@gmail.com',
    subject: `New Meeting Booked - ${meeting.meetingType}`,
    html: `
      <h2>New Meeting Booking</h2>
      <div style="font-family: Arial, sans-serif; line-height: 1.6;">
        <p><strong>Customer:</strong> ${meeting.name}</p>
        <p><strong>Email:</strong> ${meeting.email}</p>
        <p><strong>Phone:</strong> ${meeting.phone || 'Not provided'}</p>
        <p><strong>Company:</strong> ${meeting.company || 'Not provided'}</p>
        <p><strong>Meeting Type:</strong> ${meeting.meetingType}</p>
        <p><strong>Date & Time:</strong> ${formattedDate} at ${formattedTime}</p>
        <p><strong>Duration:</strong> ${meeting.duration} minutes</p>
        <p><strong>Timezone:</strong> ${meeting.timezone}</p>
        <p><strong>Description:</strong> ${meeting.description || 'Not provided'}</p>
        <p><strong>Meeting ID:</strong> ${meeting.id}</p>
      </div>
    `
  };

  try {
    await Promise.all([
      transporter.sendMail(customerMailOptions),
      transporter.sendMail(adminMailOptions)
    ]);
    console.log('Meeting confirmation emails sent successfully');
  } catch (error) {
    console.error('Error sending meeting confirmation emails:', error);
    throw error;
  }
};

export const sendMeetingRescheduleEmail = async (meeting: Meeting) => {
  const transporter = createTransporter();
  const meetingDate = new Date(meeting.preferredDate);
  const formattedDate = meetingDate.toLocaleDateString('en-US', {
    weekday: 'long',
    year: 'numeric',
    month: 'long',
    day: 'numeric',
  });
  const formattedTime = meetingDate.toLocaleTimeString('en-US', {
    hour: '2-digit',
    minute: '2-digit',
    timeZoneName: 'short',
  });

  const mailOptions = {
    from: process.env.EMAIL_USER || 'your-email@gmail.com',
    to: meeting.email,
    cc: 'crispailtd@gmail.com',
    subject: `Meeting Rescheduled - ${meeting.meetingType}`,
    html: `
      <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
        <h2 style="color: #2563eb;">Meeting Rescheduled</h2>
        <p>Dear ${meeting.name},</p>
        <p>Your ${meeting.meetingType.toLowerCase()} has been rescheduled to a new time.</p>
        
        <div style="background-color: #f3f4f6; padding: 20px; border-radius: 8px; margin: 20px 0;">
          <h3 style="margin-top: 0;">Updated Meeting Details</h3>
          <p><strong>Type:</strong> ${meeting.meetingType}</p>
          <p><strong>New Date:</strong> ${formattedDate}</p>
          <p><strong>New Time:</strong> ${formattedTime}</p>
          <p><strong>Duration:</strong> ${meeting.duration} minutes</p>
          <p><strong>Timezone:</strong> ${meeting.timezone}</p>
        </div>

        <p>Please update your calendar accordingly. A new Google Meet link will be sent to you.</p>
        
        <p>Best regards,<br>The CrispAI Team</p>
      </div>
    `
  };

  try {
    await transporter.sendMail(mailOptions);
    console.log('Meeting reschedule email sent successfully');
  } catch (error) {
    console.error('Error sending meeting reschedule email:', error);
    throw error;
  }
};

function generateCalendarInvite(event: {
  title: string;
  description: string;
  startDate: Date;
  endDate: Date;
  location: string;
  attendees: string[];
}) {
  const formatDate = (date: Date) => {
    return date.toISOString().replace(/[-:]/g, '').split('.')[0] + 'Z';
  };

  const icsContent = `BEGIN:VCALENDAR
VERSION:2.0
PRODID:-//CrispAI//Meeting Scheduler//EN
BEGIN:VEVENT
UID:${Date.now()}@crispai.ca
DTSTAMP:${formatDate(new Date())}
DTSTART:${formatDate(event.startDate)}
DTEND:${formatDate(event.endDate)}
SUMMARY:${event.title}
DESCRIPTION:${event.description}
LOCATION:${event.location}
ATTENDEE:MAILTO:${event.attendees.join(',MAILTO:')}
STATUS:CONFIRMED
SEQUENCE:0
END:VEVENT
END:VCALENDAR`;

  return icsContent;
}