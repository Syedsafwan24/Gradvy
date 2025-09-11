# 👨‍💻 Developer Guide - Gradvy Frontend

## 🚀 Quick Start

### Prerequisites
- Node.js 18+ 
- npm or yarn
- Basic understanding of React and Next.js

### Development Setup
```bash
# Install dependencies
npm install

# Start development server
npm run dev

# Run linting
npm run lint

# Type checking
npm run type-check
```

## 🏗️ Architecture Overview

### Component Structure
The codebase follows a modular architecture with clear separation of concerns:

```
src/
├── app/                    # Next.js App Router pages
├── components/             # Reusable UI components
├── config/                 # Configuration files
├── hooks/                  # Custom React hooks  
├── services/               # API services
├── store/                  # Redux store
├── utils/                  # Utility functions
└── styles/                 # Global styles
```

## 🧩 Key Components

### Error Handling
```jsx
import ErrorBoundary from '@/components/error/ErrorBoundary';
import { useErrorHandler } from '@/hooks/useErrorHandler';

// Wrap components with error boundaries
<ErrorBoundary fallback={CustomErrorFallback}>
  <YourComponent />
</ErrorBoundary>

// Use error handling hook
const { error, handleAsync, retry } = useErrorHandler();
```

### Authentication
```jsx
import { getAuthHeaders, authenticatedApiCall } from '@/utils/authHelpers';

// Get auth headers for API calls
const headers = getAuthHeaders();

// Make authenticated API calls
const { data } = await authenticatedApiCall('/api/endpoint');
```

### Accessibility
```jsx
import { createAriaProps, handleKeyboardNavigation } from '@/utils/accessibility';

// Add ARIA attributes
<div {...createAriaProps('Button label', 'description-id')}>

// Handle keyboard navigation
const handleKeyDown = (event) => {
  handleKeyboardNavigation(event, {
    onEnter: () => console.log('Enter pressed'),
    onSpace: () => console.log('Space pressed'),
  });
};
```

## 🎨 Component Patterns

### Performance Optimized Components
```jsx
import { memo, useMemo, useCallback } from 'react';

const OptimizedComponent = memo(({ data, onUpdate }) => {
  // Memoize expensive computations
  const processedData = useMemo(() => 
    data.filter(item => item.active).sort((a, b) => a.name.localeCompare(b.name)),
    [data]
  );
  
  // Memoize event handlers
  const handleClick = useCallback((id) => {
    onUpdate(id);
  }, [onUpdate]);

  return (
    <div>
      {processedData.map(item => (
        <div key={item.id} onClick={() => handleClick(item.id)}>
          {item.name}
        </div>
      ))}
    </div>
  );
});

export default OptimizedComponent;
```

### Accessible Components
```jsx
import { createAriaProps, generateId } from '@/utils/accessibility';

const AccessibleCard = ({ title, description, onClick }) => {
  const titleId = generateId('card-title');
  const descId = generateId('card-desc');
  
  return (
    <div 
      role="article"
      tabIndex={0}
      aria-labelledby={titleId}
      aria-describedby={descId}
      onClick={onClick}
      onKeyDown={(e) => {
        if (e.key === 'Enter' || e.key === ' ') {
          e.preventDefault();
          onClick();
        }
      }}
    >
      <h3 id={titleId}>{title}</h3>
      <p id={descId}>{description}</p>
    </div>
  );
};
```

## 📡 API Integration

### Using Centralized API Config
```jsx
import { API_CONFIG } from '@/config/api';

// API endpoints are centralized
const response = await fetch(`${API_CONFIG.BASE_URL}/${API_CONFIG.ENDPOINTS.USER_PROFILE}`);
```

### Error Handling with API Calls
```jsx
import { useApiErrorHandler } from '@/hooks/useErrorHandler';

const MyComponent = () => {
  const { handleApiCall, error, isLoading } = useApiErrorHandler();
  
  const fetchData = () => {
    handleApiCall(
      () => fetch('/api/data').then(res => res.json()),
      {
        onSuccess: (data) => console.log('Success:', data),
        onError: (error) => console.error('Error:', error)
      }
    );
  };
  
  if (error) return <div>Error: {error.message}</div>;
  if (isLoading) return <div>Loading...</div>;
  
  return <button onClick={fetchData}>Fetch Data</button>;
};
```

## 🔒 Security Best Practices

### Authentication
- Never access localStorage directly for auth tokens
- Use `authHelpers.js` utilities for all auth operations
- Always use authenticated API helpers for protected routes

```jsx
// ❌ Don't do this
const token = localStorage.getItem('accessToken');

// ✅ Do this instead
import { getAccessToken } from '@/utils/authHelpers';
const token = getAccessToken();
```

### API Calls
```jsx
// ✅ Use authenticated helpers
import { authenticatedApiCall } from '@/utils/authHelpers';

const response = await authenticatedApiCall('/api/protected-endpoint', {
  method: 'POST',
  body: JSON.stringify(data)
});
```

## ♿ Accessibility Guidelines

### Essential Requirements
1. **Semantic HTML**: Use proper HTML elements
2. **ARIA Labels**: Provide descriptive labels
3. **Keyboard Navigation**: Support Tab, Enter, Space, Arrow keys
4. **Focus Management**: Visible focus indicators
5. **Color Contrast**: Meet WCAG 2.1 AA standards

### Implementation Examples
```jsx
// Proper button with accessibility
<button
  aria-label="Delete item"
  aria-describedby="delete-help-text"
  onClick={handleDelete}
>
  <TrashIcon aria-hidden="true" />
</button>
<div id="delete-help-text" className="sr-only">
  This action cannot be undone
</div>

// Form with proper labels
<div>
  <label htmlFor="email-input">Email Address</label>
  <input 
    id="email-input"
    type="email"
    aria-describedby="email-error"
    aria-invalid={hasError}
    required
  />
  {hasError && (
    <div id="email-error" role="alert">
      Please enter a valid email address
    </div>
  )}
</div>
```

## 🎯 Performance Optimization

### Component Optimization
```jsx
// Prevent unnecessary re-renders
const MemoizedComponent = memo(Component);

// Optimize expensive calculations
const expensiveValue = useMemo(() => {
  return heavyComputation(data);
}, [data]);

// Stable event handlers
const handleClick = useCallback(() => {
  // handler logic
}, [dependency]);
```

### Bundle Optimization
- Use dynamic imports for code splitting
- Implement lazy loading for routes
- Optimize images with Next.js Image component

```jsx
// Code splitting
const LazyComponent = lazy(() => import('./LazyComponent'));

// Next.js dynamic imports
const DynamicComponent = dynamic(() => import('./DynamicComponent'), {
  loading: () => <p>Loading...</p>
});
```

## 🧪 Testing Patterns

### Component Testing
```jsx
import { render, screen } from '@testing-library/react';
import { axe, toHaveNoViolations } from 'jest-axe';

expect.extend(toHaveNoViolations);

test('component should be accessible', async () => {
  const { container } = render(<MyComponent />);
  const results = await axe(container);
  expect(results).toHaveNoViolations();
});
```

### Error Boundary Testing
```jsx
test('error boundary catches and displays errors', () => {
  const ThrowError = () => {
    throw new Error('Test error');
  };
  
  render(
    <ErrorBoundary>
      <ThrowError />
    </ErrorBoundary>
  );
  
  expect(screen.getByText(/something went wrong/i)).toBeInTheDocument();
});
```

## 📁 File Organization

### Component Structure
```
ComponentName/
├── index.js              # Export file
├── ComponentName.jsx     # Main component
├── ComponentName.test.js # Tests
├── ComponentName.stories.js # Storybook stories
└── styles.module.css     # Component styles (if needed)
```

### Page Structure
```
app/feature/
├── page.jsx              # Main page component
├── components/           # Page-specific components
│   ├── FeatureCard.jsx
│   └── FeatureFilters.jsx
├── data/                 # Static data and utilities
│   └── FeatureData.js
└── hooks/               # Page-specific hooks
    └── useFeature.js
```

## 🔧 Development Tools

### Code Quality
- **ESLint**: Enforces code quality and accessibility rules
- **Prettier**: Consistent code formatting
- **Husky**: Git hooks for pre-commit checks

### Debugging
```jsx
// Error boundary with development info
if (process.env.NODE_ENV === 'development') {
  console.error('Component Error:', error, errorInfo);
}

// Performance debugging
const MyComponent = () => {
  console.log('MyComponent rendered');
  return <div>Content</div>;
};
```

## 📚 Additional Resources

### Documentation
- [Next.js Documentation](https://nextjs.org/docs)
- [React Accessibility](https://react.dev/learn/accessibility)
- [WCAG Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)

### Tools
- [React DevTools](https://react.dev/learn/react-developer-tools)
- [axe DevTools](https://www.deque.com/axe/devtools/)
- [Lighthouse](https://developers.google.com/web/tools/lighthouse)

## 🚀 Deployment

### Environment Variables
Create `.env.local` for local development:
```env
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000
NODE_ENV=development
```

### Production Build
```bash
# Build for production
npm run build

# Start production server
npm start
```

---

## 💡 Best Practices Summary

1. **Always use error boundaries** for production stability
2. **Centralize API configuration** for environment flexibility
3. **Follow accessibility guidelines** for inclusive design
4. **Optimize performance** with React patterns
5. **Secure authentication** through centralized helpers
6. **Modular components** for maintainability
7. **Consistent code style** with ESLint and Prettier