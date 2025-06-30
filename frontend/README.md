# CMU Health Services RAG Chatbot - Next.js Frontend

A beautiful, modern Next.js frontend for the CMU Health Services RAG Chatbot with a healthcare-focused design.

## Features

- 🎨 **Modern UI**: Built with Next.js 15, TypeScript, and Tailwind CSS
- 🏥 **Healthcare-Themed Design**: CMU red color scheme with health-focused icons
- 💬 **Real-time Chat Interface**: Smooth animations with Framer Motion
- 📱 **Responsive Design**: Works seamlessly on desktop and mobile
- 🌓 **Dark Mode Support**: Automatic theme switching based on system preferences
- 📄 **Document Upload**: Drag-and-drop file upload for PDFs, TXT, and MD files
- ⚡ **Quick Actions**: Pre-configured buttons for common health service questions
- 🔍 **Contact Information**: Always-visible health center details

## Tech Stack

- **Framework**: Next.js 15 with App Router
- **Language**: TypeScript
- **Styling**: Tailwind CSS with custom healthcare theme
- **Components**: Custom UI components inspired by shadcn/ui
- **Icons**: Lucide React icons
- **Animations**: Framer Motion

## Getting Started

1. **Install dependencies**:
   ```bash
   npm install
   ```

2. **Run the development server**:
   ```bash
   npm run dev
   ```

3. **Open your browser**:
   Navigate to [http://localhost:3000](http://localhost:3000)

## Configuration

The frontend connects to the Spring Boot backend at `http://localhost:8080`. Make sure the backend is running before using the chat interface.

## UI Components

- **Chat Interface**: Full-featured chat with message history and typing indicators
- **Quick Actions Sidebar**: Common questions and actions for easy access
- **Contact Card**: CMU Health Services location, hours, and phone number
- **Document Upload**: Integrated file upload for expanding the knowledge base

## Design Features

- **CMU Branding**: Uses CMU's signature red (#DC2626) as the primary color
- **Healthcare Icons**: Medical-themed icons from Lucide React
- **Smooth Animations**: Subtle animations for better user experience
- **Accessibility**: Proper contrast ratios and keyboard navigation support

## Development

- **Hot Reload**: Changes are reflected immediately during development
- **Type Safety**: Full TypeScript support for better developer experience
- **Component Structure**: Modular components for easy maintenance

## Production Build

```bash
npm run build
npm start
```

## Integration with Backend

The frontend expects the following endpoints from the Spring Boot backend:
- `POST /api/v1/chat` - Send chat messages
- `POST /api/v1/documents/upload` - Upload documents
- `GET /api/v1/health` - Health check endpoint

## Learn More

To learn more about Next.js, take a look at the following resources:

- [Next.js Documentation](https://nextjs.org/docs) - learn about Next.js features and API.
- [Learn Next.js](https://nextjs.org/learn) - an interactive Next.js tutorial.

## Deploy on Vercel

The easiest way to deploy your Next.js app is to use the [Vercel Platform](https://vercel.com/new?utm_medium=default-template&filter=next.js&utm_source=create-next-app&utm_campaign=create-next-app-readme) from the creators of Next.js.