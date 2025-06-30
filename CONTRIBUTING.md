# Contributing to CMU UHS RAG Chatbot

We're excited that you're interested in contributing to the CMU UHS RAG Chatbot! This document provides guidelines and instructions for contributing to the project.

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Process](#development-process)
- [Pull Request Process](#pull-request-process)
- [Coding Standards](#coding-standards)
- [Testing Guidelines](#testing-guidelines)
- [Documentation](#documentation)
- [Community](#community)

## Code of Conduct

By participating in this project, you agree to maintain a respectful and inclusive environment. We expect all contributors to:

- Be respectful and considerate in all interactions
- Welcome newcomers and help them get started
- Focus on constructive criticism and feedback
- Respect differing viewpoints and experiences

## Getting Started

1. **Fork the repository** on GitHub
2. **Clone your fork** locally:
   ```bash
   git clone https://github.com/your-username/CMU-UHS-RAG-CHATBOT.git
   cd CMU-UHS-RAG-CHATBOT
   ```
3. **Add the upstream remote**:
   ```bash
   git remote add upstream https://github.com/original-owner/CMU-UHS-RAG-CHATBOT.git
   ```
4. **Create a new branch** for your feature:
   ```bash
   git checkout -b feature/your-feature-name
   ```

## Development Process

### 1. Before You Start

- Check existing issues and pull requests to avoid duplicate work
- For major changes, open an issue first to discuss your proposal
- Ensure your development environment is properly set up (see README.md)

### 2. Making Changes

- Write clear, self-documenting code
- Follow the existing code style and conventions
- Add comments for complex logic
- Update documentation as needed
- Write tests for new functionality

### 3. Commit Guidelines

We follow conventional commit messages:

```
type(scope): description

[optional body]

[optional footer]
```

Types:
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation changes
- `style`: Code style changes (formatting, etc.)
- `refactor`: Code refactoring
- `test`: Adding or updating tests
- `chore`: Maintenance tasks

Example:
```
feat(chat): add support for markdown in responses

- Implemented markdown parser for chat responses
- Added syntax highlighting for code blocks
- Updated UI components to render formatted text

Closes #123
```

## Pull Request Process

1. **Update your fork** with the latest upstream changes:
   ```bash
   git fetch upstream
   git checkout main
   git merge upstream/main
   ```

2. **Rebase your feature branch**:
   ```bash
   git checkout feature/your-feature-name
   git rebase main
   ```

3. **Run tests** and ensure they pass:
   ```bash
   # Backend tests
   cd backend
   mvn test
   
   # Frontend tests
   cd frontend
   npm test
   ```

4. **Push to your fork**:
   ```bash
   git push origin feature/your-feature-name
   ```

5. **Create a Pull Request** on GitHub with:
   - Clear title and description
   - Reference to any related issues
   - Screenshots/GIFs for UI changes
   - Test results and coverage information

6. **Address review feedback** promptly and professionally

## Coding Standards

### Java (Backend)

- Follow standard Java naming conventions
- Use meaningful variable and method names
- Keep methods focused and under 50 lines
- Use dependency injection appropriately
- Document public APIs with Javadoc

Example:
```java
/**
 * Processes a chat message and returns an AI-generated response.
 * 
 * @param message the user's input message
 * @param context optional conversation context
 * @return ChatResponse containing the AI response and metadata
 * @throws ChatException if processing fails
 */
public ChatResponse processMessage(String message, ChatContext context) {
    // Implementation
}
```

### TypeScript/JavaScript (Frontend)

- Use TypeScript for type safety
- Follow React best practices and hooks guidelines
- Keep components small and focused
- Use meaningful prop names
- Document complex components

Example:
```typescript
interface ChatMessageProps {
  message: string;
  timestamp: Date;
  isUser: boolean;
  onEdit?: (newMessage: string) => void;
}

/**
 * Renders a single chat message with formatting and actions
 */
export const ChatMessage: React.FC<ChatMessageProps> = ({
  message,
  timestamp,
  isUser,
  onEdit
}) => {
  // Implementation
};
```

## Testing Guidelines

### Backend Testing

- Write unit tests for all service methods
- Use mocking for external dependencies
- Aim for >80% code coverage
- Include integration tests for API endpoints

### Frontend Testing

- Write unit tests for utility functions
- Test React components with React Testing Library
- Include snapshot tests for UI components
- Test user interactions and edge cases

### E2E Testing

- Cover critical user journeys
- Test across different browsers
- Include mobile responsiveness tests

## Documentation

### Code Documentation

- Document all public APIs
- Include examples in documentation
- Keep README files up to date
- Document configuration options

### User Documentation

- Update user guides for new features
- Include screenshots and examples
- Keep FAQ section current
- Document troubleshooting steps

## Community

### Communication Channels

- **GitHub Issues**: Bug reports and feature requests
- **Discussions**: General questions and ideas
- **Pull Requests**: Code contributions and reviews

### Getting Help

If you need help:

1. Check the documentation
2. Search existing issues
3. Ask in discussions
4. Reach out to maintainers

## Recognition

Contributors will be:
- Listed in the CONTRIBUTORS.md file
- Mentioned in release notes
- Given credit in relevant documentation

Thank you for contributing to make CMU UHS RAG Chatbot better!