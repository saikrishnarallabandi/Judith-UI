# LibreChat-Inspired AI Chat Interface

A clean, professional chat interface that provides an intuitive conversational AI experience with a custom LLM backend.

**Experience Qualities**:
1. **Professional** - Clean, polished interface that feels reliable and trustworthy for serious conversations
2. **Intuitive** - Familiar chat patterns that users can navigate without learning new interaction models
3. **Responsive** - Fast, fluid interactions with immediate feedback and seamless message flow

**Complexity Level**: Light Application (multiple features with basic state)
- Multi-conversation management with persistent chat history, real-time message streaming simulation, and customizable interface options

## Essential Features

### Chat Interface
- **Functionality**: Real-time conversation with AI using custom LLM backend
- **Purpose**: Core conversational experience that feels natural and engaging
- **Trigger**: User types message and presses enter or clicks send
- **Progression**: Type message → Send → Show loading indicator → Stream response → Display complete message
- **Success criteria**: Messages send reliably, responses appear smoothly, conversation flows naturally

### Conversation Management
- **Functionality**: Create, switch between, and delete multiple chat conversations
- **Purpose**: Organize different topics and maintain conversation context
- **Trigger**: User clicks "New Chat" or selects existing conversation from sidebar
- **Progression**: Click new chat → Generate conversation title → Switch to empty chat → Begin new conversation
- **Success criteria**: Conversations persist between sessions, switching is instant, titles are descriptive

### Message History
- **Functionality**: Persistent storage of all conversations and messages
- **Purpose**: Allow users to reference previous conversations and maintain context
- **Trigger**: Automatic on every message sent/received
- **Progression**: Send/receive message → Save to persistent storage → Update UI → Maintain scroll position
- **Success criteria**: All messages persist across browser sessions, scroll performance remains smooth

### Custom LLM Integration
- **Functionality**: Connect to custom GPT client backend simulation
- **Purpose**: Demonstrate integration with custom AI models rather than standard APIs
- **Trigger**: User sends message, system formats as OpenAI-compatible request
- **Progression**: Format message → Call custom LLM → Parse response → Display to user
- **Success criteria**: Messages process correctly, responses feel natural, error handling is graceful

## Edge Case Handling

- **Empty messages**: Disable send button when input is empty or only whitespace
- **Very long messages**: Handle messages exceeding reasonable limits with graceful truncation warnings
- **Network simulation**: Show appropriate loading states and retry options for simulated backend calls
- **Empty conversation state**: Provide welcoming placeholder content with usage suggestions
- **Rapid message sending**: Prevent duplicate sends and queue messages appropriately

## Design Direction

The interface should feel professional and trustworthy like ChatGPT or Claude, with clean typography and generous whitespace that prioritizes readability and focus over visual flair.

## Color Selection

Complementary (opposite colors) - Using a sophisticated blue-gray primary with warm accent highlights to create a professional yet approachable feeling that balances trust with warmth.

- **Primary Color**: Deep Blue-Gray oklch(0.25 0.02 240) - Communicates professionalism, reliability, and technological sophistication
- **Secondary Colors**: Light Gray oklch(0.96 0.005 240) for subtle backgrounds and Neutral Gray oklch(0.45 0.01 240) for supporting text
- **Accent Color**: Warm Blue oklch(0.55 0.15 240) for interactive elements, send buttons, and focus states
- **Foreground/Background Pairings**: 
  - Background (White oklch(1 0 0)): Dark Gray text oklch(0.15 0.005 240) - Ratio 14.2:1 ✓
  - Card (Light Gray oklch(0.96 0.005 240)): Dark Gray text oklch(0.15 0.005 240) - Ratio 13.1:1 ✓
  - Primary (Deep Blue-Gray oklch(0.25 0.02 240)): White text oklch(1 0 0) - Ratio 12.8:1 ✓
  - Accent (Warm Blue oklch(0.55 0.15 240)): White text oklch(1 0 0) - Ratio 4.7:1 ✓

## Font Selection

Clean, highly readable sans-serif typography that supports extended reading sessions and maintains clarity across all interface densities.

- **Typographic Hierarchy**: 
  - H1 (Page Title): Inter Semibold/24px/tight letter spacing
  - H2 (Conversation Titles): Inter Medium/16px/normal letter spacing  
  - Body (Messages): Inter Regular/14px/relaxed line height 1.6
  - Small (Timestamps): Inter Regular/12px/muted color
  - Code (Code blocks): JetBrains Mono Regular/13px/monospace

## Animations

Subtle, purposeful animations that guide attention and provide feedback without distracting from the conversation flow - prioritizing smooth message appearance and loading states over decorative effects.

- **Purposeful Meaning**: Gentle fade-ins for new messages reinforce the conversational flow, while subtle hover states on interactive elements communicate availability without being distracting
- **Hierarchy of Movement**: Message sending/receiving gets primary animation focus, followed by navigation transitions, with minimal movement on secondary interface elements

## Component Selection

- **Components**: Card for message bubbles, Button for send actions, ScrollArea for chat history, Input for message composition, Separator for conversation boundaries, Avatar for user/AI identification
- **Customizations**: Custom message bubble component with proper spacing and typography, custom loading indicator for message streaming simulation
- **States**: Send button should show loading spinner during processing, input should have subtle focus ring, messages should have hover states for actions
- **Icon Selection**: Send (paper airplane), Add/Plus for new conversations, Menu/Hamburger for sidebar toggle, Copy for message copying
- **Spacing**: Consistent 16px padding for messages, 8px gaps between related elements, 24px margins for section separation
- **Mobile**: Collapsible sidebar that slides over content, full-width message input with send button, touch-friendly 44px minimum tap targets