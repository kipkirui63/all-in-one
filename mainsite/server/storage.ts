import { users, newsletterSubscriptions, contactMessages, meetings, type User, type InsertUser, type NewsletterSubscription, type InsertNewsletterSubscription, type ContactMessage, type InsertContactMessage, type Meeting, type InsertMeeting } from "@shared/schema";

export interface IStorage {
  getUser(id: number): Promise<User | undefined>;
  getUserByUsername(username: string): Promise<User | undefined>;
  createUser(user: InsertUser): Promise<User>;
  createNewsletterSubscription(subscription: InsertNewsletterSubscription): Promise<NewsletterSubscription>;
  getNewsletterSubscriptionByEmail(email: string): Promise<NewsletterSubscription | undefined>;
  createContactMessage(message: InsertContactMessage): Promise<ContactMessage>;
  createMeeting(meeting: InsertMeeting): Promise<Meeting>;
  getMeeting(id: number): Promise<Meeting | undefined>;
  getAllMeetings(): Promise<Meeting[]>;
  updateMeeting(id: number, updates: Partial<Meeting>): Promise<Meeting | undefined>;
  deleteMeeting(id: number): Promise<boolean>;
}

export class MemStorage implements IStorage {
  private users: Map<number, User>;
  private newsletterSubscriptions: Map<number, NewsletterSubscription>;
  private contactMessages: Map<number, ContactMessage>;
  private meetings: Map<number, Meeting>;
  private currentUserId: number;
  private currentSubscriptionId: number;
  private currentMessageId: number;
  private currentMeetingId: number;

  constructor() {
    this.users = new Map();
    this.newsletterSubscriptions = new Map();
    this.contactMessages = new Map();
    this.meetings = new Map();
    this.currentUserId = 1;
    this.currentSubscriptionId = 1;
    this.currentMessageId = 1;
    this.currentMeetingId = 1;
  }

  async getUser(id: number): Promise<User | undefined> {
    return this.users.get(id);
  }

  async getUserByUsername(username: string): Promise<User | undefined> {
    return Array.from(this.users.values()).find(
      (user) => user.username === username,
    );
  }

  async createUser(insertUser: InsertUser): Promise<User> {
    const id = this.currentUserId++;
    const user: User = { ...insertUser, id };
    this.users.set(id, user);
    return user;
  }

  async createNewsletterSubscription(insertSubscription: InsertNewsletterSubscription): Promise<NewsletterSubscription> {
    const id = this.currentSubscriptionId++;
    const subscription: NewsletterSubscription = { 
      id,
      email: insertSubscription.email,
      firstName: insertSubscription.firstName ?? null,
      lastName: insertSubscription.lastName ?? null,
      subscribedAt: new Date()
    };
    this.newsletterSubscriptions.set(id, subscription);
    return subscription;
  }

  async getNewsletterSubscriptionByEmail(email: string): Promise<NewsletterSubscription | undefined> {
    return Array.from(this.newsletterSubscriptions.values()).find(
      (sub) => sub.email === email,
    );
  }

  async createContactMessage(insertMessage: InsertContactMessage): Promise<ContactMessage> {
    const id = this.currentMessageId++;
    const message: ContactMessage = {
      id,
      name: insertMessage.name,
      email: insertMessage.email,
      phone: insertMessage.phone ?? null,
      message: insertMessage.message,
      createdAt: new Date()
    };
    this.contactMessages.set(id, message);
    return message;
  }

  async createMeeting(insertMeeting: InsertMeeting): Promise<Meeting> {
    const id = this.currentMeetingId++;
    const now = new Date();
    const meeting: Meeting = {
      id,
      name: insertMeeting.name,
      email: insertMeeting.email,
      phone: insertMeeting.phone ?? null,
      company: insertMeeting.company ?? null,
      meetingType: insertMeeting.meetingType,
      preferredDate: insertMeeting.preferredDate,
      duration: insertMeeting.duration ?? 30,
      timezone: insertMeeting.timezone,
      description: insertMeeting.description ?? null,
      status: insertMeeting.status ?? "pending",
      googleMeetLink: insertMeeting.googleMeetLink ?? null,
      calendarEventId: insertMeeting.calendarEventId ?? null,
      createdAt: now,
      updatedAt: now
    };
    this.meetings.set(id, meeting);
    return meeting;
  }

  async getMeeting(id: number): Promise<Meeting | undefined> {
    return this.meetings.get(id);
  }

  async getAllMeetings(): Promise<Meeting[]> {
    return Array.from(this.meetings.values());
  }

  async updateMeeting(id: number, updates: Partial<Meeting>): Promise<Meeting | undefined> {
    const existing = this.meetings.get(id);
    if (!existing) return undefined;
    
    const updated: Meeting = {
      ...existing,
      ...updates,
      id, // Keep original id
      createdAt: existing.createdAt, // Keep original creation time
      updatedAt: new Date() // Update modification time
    };
    this.meetings.set(id, updated);
    return updated;
  }

  async deleteMeeting(id: number): Promise<boolean> {
    return this.meetings.delete(id);
  }
}

export const storage = new MemStorage();
