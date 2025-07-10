import type { Express } from "express";
import { createServer, type Server } from "http";
import { storage } from "./storage";
import { insertNewsletterSubscriptionSchema, insertContactMessageSchema, insertMeetingSchema } from "@shared/schema";
import { sendContactFormEmail, sendNewsletterSubscriptionEmail, sendMeetingConfirmationEmail, sendMeetingRescheduleEmail } from "./emailService";
import { handleChatMessage, generateSessionId } from "./chatbot";
import { z } from "zod";

export async function registerRoutes(app: Express): Promise<Server> {
  // Newsletter subscription endpoint
  app.post("/api/newsletter/subscribe", async (req, res) => {
    try {
      const validatedData = insertNewsletterSubscriptionSchema.parse(req.body);
      
      // Check if email already exists
      const existingSubscription = await storage.getNewsletterSubscriptionByEmail(validatedData.email);
      if (existingSubscription) {
        return res.status(409).json({ 
          message: "This email is already subscribed to our newsletter." 
        });
      }

      const subscription = await storage.createNewsletterSubscription(validatedData);
      
      // Send email notification
      try {
        await sendNewsletterSubscriptionEmail(validatedData);
      } catch (emailError) {
        console.error("Failed to send newsletter subscription email:", emailError);
        // Continue with success response even if email fails
      }
      
      res.status(201).json({ 
        message: "Successfully subscribed to newsletter!",
        subscription: {
          id: subscription.id,
          email: subscription.email,
          firstName: subscription.firstName,
          lastName: subscription.lastName
        }
      });
    } catch (error) {
      if (error instanceof z.ZodError) {
        return res.status(400).json({ 
          message: "Invalid input data",
          errors: error.errors 
        });
      }
      
      console.error("Newsletter subscription error:", error);
      res.status(500).json({ 
        message: "An error occurred while processing your subscription." 
      });
    }
  });

  // Contact form submission endpoint
  app.post("/api/contact/submit", async (req, res) => {
    try {
      const validatedData = insertContactMessageSchema.parse(req.body);
      
      const contactMessage = await storage.createContactMessage(validatedData);
      
      // Send email notification
      try {
        await sendContactFormEmail(validatedData);
      } catch (emailError) {
        console.error("Failed to send contact form email:", emailError);
        // Continue with success response even if email fails
      }
      
      res.status(201).json({ 
        message: "Thank you for your message! We'll get back to you soon.",
        contactMessage: {
          id: contactMessage.id,
          name: contactMessage.name,
          email: contactMessage.email
        }
      });
    } catch (error) {
      if (error instanceof z.ZodError) {
        return res.status(400).json({ 
          message: "Invalid input data",
          errors: error.errors 
        });
      }
      
      console.error("Contact form submission error:", error);
      res.status(500).json({ 
        message: "An error occurred while processing your message." 
      });
    }
  });

  // Meeting endpoints
  app.post("/api/meetings/book", async (req, res) => {
    try {
      // Transform the preferredDate string to Date object before validation
      const requestData = {
        ...req.body,
        preferredDate: req.body.preferredDate ? new Date(req.body.preferredDate) : undefined
      };
      
      const meetingData = insertMeetingSchema.parse(requestData);
      const meeting = await storage.createMeeting(meetingData);
      
      // Send meeting confirmation email
      try {
        await sendMeetingConfirmationEmail(meeting);
      } catch (emailError) {
        console.error("Failed to send meeting confirmation email:", emailError);
        // Continue even if email fails
      }
      
      res.json({ 
        message: "Meeting booked successfully",
        meeting: {
          id: meeting.id,
          meetingType: meeting.meetingType,
          preferredDate: meeting.preferredDate,
          duration: meeting.duration,
          status: meeting.status
        }
      });
    } catch (error) {
      console.error("Meeting booking error:", error);
      res.status(400).json({ 
        message: error instanceof Error ? error.message : "Failed to book meeting" 
      });
    }
  });

  app.get("/api/meetings", async (req, res) => {
    try {
      const meetings = await storage.getAllMeetings();
      res.json(meetings);
    } catch (error) {
      console.error("Failed to fetch meetings:", error);
      res.status(500).json({ message: "Failed to fetch meetings" });
    }
  });

  app.get("/api/meetings/:id", async (req, res) => {
    try {
      const id = parseInt(req.params.id);
      const meeting = await storage.getMeeting(id);
      if (!meeting) {
        return res.status(404).json({ message: "Meeting not found" });
      }
      res.json(meeting);
    } catch (error) {
      console.error("Failed to fetch meeting:", error);
      res.status(500).json({ message: "Failed to fetch meeting" });
    }
  });

  app.put("/api/meetings/:id", async (req, res) => {
    try {
      const id = parseInt(req.params.id);
      // Transform preferredDate string to Date object if present
      const updates = {
        ...req.body,
        ...(req.body.preferredDate && { preferredDate: new Date(req.body.preferredDate) })
      };
      const updatedMeeting = await storage.updateMeeting(id, updates);
      
      if (!updatedMeeting) {
        return res.status(404).json({ message: "Meeting not found" });
      }

      // Send reschedule notification if date changed
      if (updates.preferredDate) {
        try {
          await sendMeetingRescheduleEmail(updatedMeeting);
        } catch (emailError) {
          console.error("Failed to send reschedule email:", emailError);
        }
      }
      
      res.json({ 
        message: "Meeting updated successfully", 
        meeting: updatedMeeting 
      });
    } catch (error) {
      console.error("Failed to update meeting:", error);
      res.status(500).json({ message: "Failed to update meeting" });
    }
  });

  app.delete("/api/meetings/:id", async (req, res) => {
    try {
      const id = parseInt(req.params.id);
      const success = await storage.deleteMeeting(id);
      
      if (!success) {
        return res.status(404).json({ message: "Meeting not found" });
      }
      
      res.json({ message: "Meeting cancelled successfully" });
    } catch (error) {
      console.error("Failed to cancel meeting:", error);
      res.status(500).json({ message: "Failed to cancel meeting" });
    }
  });

  // Chatbot endpoints
  app.post("/api/chat", async (req, res) => {
    try {
      const { message, sessionId } = req.body;
      
      if (!message || typeof message !== 'string') {
        return res.status(400).json({ error: "Message is required" });
      }

      const finalSessionId = sessionId || generateSessionId();
      const result = await handleChatMessage(finalSessionId, message);
      
      res.json(result);
    } catch (error) {
      console.error("Chat API error:", error);
      res.status(500).json({ 
        error: "Sorry, I'm experiencing technical difficulties. Please contact our team directly." 
      });
    }
  });

  app.post("/api/chat/session", (req, res) => {
    const sessionId = generateSessionId();
    res.json({ sessionId });
  });

  // Server status endpoint
  app.get("/api/health", (req, res) => {
    res.json({ status: "ok", timestamp: new Date().toISOString() });
  });

  const httpServer = createServer(app);
  return httpServer;
}
