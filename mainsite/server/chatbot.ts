import OpenAI from 'openai';
import dotenv from 'dotenv'
dotenv.config();

// the newest OpenAI model is "gpt-4o" which was released May 13, 2024. do not change this unless explicitly requested by the user
const openai = new OpenAI({
  apiKey: process.env.OPENAI_API_KEY,
});

// CrispAI context and knowledge base
const CRISPAI_CONTEXT = `
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

TEAM:
- Sarah Johnson (CEO) - 15+ years in AI and business strategy
- Dr. Michael Chen (CTO) - PhD in Machine Learning, former Google AI researcher
- Emily Rodriguez (Head of Product) - 10+ years in product management and UX design
- David Kim (Lead AI Engineer) - MS in Computer Science, specialized in deep learning
- Lisa Thompson (Head of Operations) - MBA, expert in scaling tech companies
- James Wilson (Senior Data Scientist) - PhD in Statistics, expert in predictive modeling

CORE VALUES:
- Innovation First: Constantly pushing the boundaries of what's possible with AI
- Human-Centered: Technology should enhance human capabilities, not replace them
- Ethical AI: Committed to responsible AI development and deployment
- Accessibility: Making advanced AI solutions available to businesses of all sizes
- Continuous Learning: Staying at the forefront of AI advancements and best practices

ASSESSMENT TOOL:
We offer a comprehensive AI Readiness Assessment covering:
- Strategy & Vision
- Execution & Implementation
- Innovation & Technology
- Enabling Capabilities

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

Marketplace Categories:
- Analytics: Business Intelligence Agent
- Writing: CrispWrite  
- Recruitment: AI Recruitment Assistant, Resume Analyzer
- Business: SOP Assistant

All marketplace applications include:
- Free 7-day trial
- Professional support
- Regular updates and improvements
- Integration capabilities  
- Innovation & Adaptability
- Enabling Capabilities & Infrastructure

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
`;

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

interface ChatSession {
  id: string;
  messages: ChatMessage[];
  createdAt: Date;
  lastActivity: Date;
}

// In-memory storage for chat sessions (in production, use a database)
const chatSessions = new Map<string, ChatSession>();

export async function handleChatMessage(
  sessionId: string,
  userMessage: string
): Promise<{ response: string; sessionId: string }> {
  try {
    // Get or create chat session
    let session = chatSessions.get(sessionId);
    if (!session) {
      session = {
        id: sessionId,
        messages: [],
        createdAt: new Date(),
        lastActivity: new Date()
      };
      chatSessions.set(sessionId, session);
    }

    // Check if this is the first message (new conversation)
    const isFirstMessage = session.messages.length === 0;
    
    console.log(`Session ${sessionId}: isFirstMessage = ${isFirstMessage}, messages count = ${session.messages.length}`);

    // Add user message to session
    session.messages.push({
      role: 'user',
      content: userMessage,
      timestamp: new Date()
    });
    session.lastActivity = new Date();

    // If it's the first message, immediately ask for name and email
    if (isFirstMessage) {
      const welcomeResponse = "Hi! I'm here to help with CrispAI. Could I get your name and email for personalized assistance?";
      
      console.log(`Sending welcome response for new session: ${sessionId}`);
      
      // Add assistant response to session
      session.messages.push({
        role: 'assistant',
        content: welcomeResponse,
        timestamp: new Date()
      });

      return {
        response: welcomeResponse,
        sessionId: sessionId
      };
    }

    // Prepare messages for OpenAI (last 10 messages to maintain context)
    const recentMessages = session.messages.slice(-10);
    const openaiMessages: OpenAI.Chat.Completions.ChatCompletionMessageParam[] = [
      {
        role: 'system',
        content: CRISPAI_CONTEXT
      },
      ...recentMessages.map(msg => ({
        role: msg.role,
        content: msg.content
      }))
    ];

    // Get response from OpenAI
    const completion = await openai.chat.completions.create({
      model: 'gpt-4o',
      messages: openaiMessages,
      max_tokens: 100, // Very brief responses
      temperature: 0.7,
      presence_penalty: 0.1,
      frequency_penalty: 0.1
    });

    const assistantResponse = completion.choices[0]?.message?.content || 
      "I apologize, but I'm having trouble processing your request right now. Please try again or contact us directly at info@crispai.ca";

    // Add assistant response to session
    session.messages.push({
      role: 'assistant',
      content: assistantResponse,
      timestamp: new Date()
    });

    return {
      response: assistantResponse,
      sessionId: sessionId
    };

  } catch (error) {
    console.error('Chat error:', error);
    
    return {
      response: "I'm experiencing technical difficulties right now. Please contact our team directly at info@crispai.ca or +1 (343) 580-1393 for immediate assistance.",
      sessionId: sessionId
    };
  }
}

export function generateSessionId(): string {
  return `chat_${Date.now()}_${Math.random().toString(36).substr(2, 9)}`;
}

// Clean up old sessions (run periodically)
export function cleanupOldSessions() {
  const oneHourAgo = new Date(Date.now() - 60 * 60 * 1000);
  
  Array.from(chatSessions.entries()).forEach(([sessionId, session]) => {
    if (session.lastActivity < oneHourAgo) {
      chatSessions.delete(sessionId);
    }
  });
}

// Run cleanup every 30 minutes
setInterval(cleanupOldSessions, 30 * 60 * 1000);