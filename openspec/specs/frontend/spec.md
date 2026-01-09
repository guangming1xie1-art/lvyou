# Frontend Specification

> OpenSpec specification for travel-assistant-front

## Overview

This document defines the technical specifications, patterns, and standards for the React + TypeScript frontend application.

## Component Architecture

### Design Principles

1. **Composition over Inheritance**: Build complex UIs from simple, composable components
2. **Single Responsibility**: Each component should have one clear purpose
3. **Functional Components**: Use React hooks for state and lifecycle management
4. **Prop Types**: Define clear TypeScript interfaces for all component props

### Component Categories

| Category | Location | Responsibility |
|----------|----------|----------------|
| Common | `src/components/common/` | Reusable UI primitives (Button, Input, Modal, Card) |
| Layout | `src/components/layout/` | Page structure (Header, Footer, Sidebar) |
| Feature | `src/components/{feature}/` | Domain-specific components |
| Pages | `src/pages/` | Route-level components |

### Component File Structure

```
src/components/common/
├── Button/
│   ├── Button.tsx          # Main component
│   ├── Button.types.ts     # TypeScript interfaces
│   └── index.ts            # Exports
├── Input/
├── Modal/
└── Card/
```

### Component Naming

- **Directory**: camelCase (`travelCard/`)
- **Component File**: PascalCase (`TravelCard.tsx`)
- **Index Export**: Default export with component name
- **CSS File**: Component-scoped or Tailwind classes

### Component Props Pattern

```typescript
// Good pattern
interface TravelCardProps {
  id: string;
  title: string;
  destination: string;
  price: number;
  coverImage?: string;
  onSelect?: (id: string) => void;
  variant?: 'default' | 'compact' | 'featured';
  className?: string;
}

export function TravelCard({
  id,
  title,
  destination,
  price,
  coverImage,
  onSelect,
  variant = 'default',
  className = '',
}: TravelCardProps) {
  // Component implementation
}
```

## State Management

### State Strategy

| State Type | Solution | Examples |
|------------|----------|----------|
| Server State | TanStack Query | API data, cache, mutations |
| UI State | React local state | Modal open/close, form fields |
| Global UI State | Zustand | Theme, sidebar toggle |
| User State | Zustand | Auth token, user profile |
| Travel Session | Zustand + persistence | Current travel request, preferences |

### Zustand Store Pattern

```typescript
// store/travelStore.ts
import { create } from 'zustand';
import { persist } from 'zustand/middleware';

interface TravelState {
  currentRequest: TravelRequest | null;
  plans: TravelPlan[];
  selectedPlanId: string | null;
  setCurrentRequest: (request: TravelRequest | null) => void;
  selectPlan: (planId: string) => void;
  clearSession: () => void;
}

export const useTravelStore = create<TravelState>()(
  persist(
    (set) => ({
      currentRequest: null,
      plans: [],
      selectedPlanId: null,
      setCurrentRequest: (request) => set({ currentRequest: request }),
      selectPlan: (planId) => set({ selectedPlanId: planId }),
      clearSession: () => set({ currentRequest: null, plans: [], selectedPlanId: null }),
    }),
    {
      name: 'travel-session',
      partialize: (state) => ({ currentRequest: state.currentRequest }),
    }
  )
);
```

### TanStack Query Pattern

```typescript
// hooks/useTravel.ts
import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { travelService } from '@/services/travelService';

export function usePlansQuery(requestId: string) {
  return useQuery({
    queryKey: ['plans', requestId],
    queryFn: () => travelService.getPlans(requestId),
    staleTime: 5 * 60 * 1000, // 5 minutes
    gcTime: 30 * 60 * 1000,   // 30 minutes
  });
}

export function useCreatePlanMutation() {
  const queryClient = useQueryClient();
  
  return useMutation({
    mutationFn: (data: CreatePlanRequest) => travelService.createPlan(data),
    onSuccess: (newPlan) => {
      queryClient.invalidateQueries({ queryKey: ['plans'] });
    },
  });
}
```

## UI/UX Standards

### Design System

Based on the design specification in `DESIGN_SPEC.md`:

#### Color Palette

| Role | Token | Value | Usage |
|------|-------|-------|-------|
| Primary | `primary-600` | `#2563eb` | Brand, main CTAs |
| Primary | `primary-900` | `#1e3a8a` | Headers, hero sections |
| Secondary | `secondary-500` | `#f97316` | Accents, prices, highlights |
| Secondary | `secondary-600` | `#ea580c` | Active CTAs |
| Background | `bg-gray-50` | `#f9fafb` | Page background |
| Surface | `bg-white` | `#ffffff` | Cards, modals |
| Text | `text-gray-900` | `#111827` | Headings |
| Text | `text-gray-600` | `#4b5563` | Body text |
| Text | `text-gray-400` | `#9ca3af` | Muted text |

#### Typography

| Element | Size | Weight | Line Height |
|---------|------|--------|------------|
| Hero | 72px / 36px mobile | Bold | 1.1 |
| Page Title | 48px | Bold | 1.2 |
| Section | 30px | Bold | 1.3 |
| Card Title | 20px | Bold | 1.4 |
| Body | 16px | Regular | 1.6 |
| Caption | 14px | Medium | 1.5 |

#### Spacing

- Base unit: 4px
- Common spacing: `4px, 8px, 12px, 16px, 24px, 32px, 48px, 64px`
- Border radius: `8px` (small), `12px` (medium), `24px` (large)

#### Shadows

- Small: `shadow-sm` for cards
- Medium: `shadow-md` for hover states
- Large: `shadow-lg` for modals, dropdowns

### Responsive Breakpoints

| Breakpoint | Width | Container Max |
|------------|-------|---------------|
| Mobile | < 640px | 100% |
| Tablet | 640px - 1024px | 640px / 768px |
| Desktop | > 1024px | 1024px / 1280px |

### Component States

#### Loading States

- **Skeleton Loading**: For content that takes > 200ms to load
- **Spinner**: For user-initiated actions (buttons, form submissions)
- **Progress Bar**: For multi-step processes

#### Error States

- Inline error: `text-red-500 text-sm mt-1`
- Error boundary: Full-page error with retry button
- Toast/Snackbar: Non-blocking notifications

#### Empty States

- Illustrated empty state with message
- Call-to-action to create content

### Interaction Patterns

| Interaction | Behavior |
|-------------|----------|
| Hover | Shadow increase, slight image scale (1.05) |
| Active | Button scale (0.95) |
| Focus | Visible focus ring (`ring-2 ring-primary-500`) |
| Transition | 150-200ms ease-in-out |

## API Client Interface

### Axios Configuration

```typescript
// utils/request.ts
import axios from 'axios';
import { useAuthStore } from '@/store/authStore';

const http = axios.create({
  baseURL: import.meta.env.VITE_API_BASE_URL,
  timeout: 30000,
  headers: {
    'Content-Type': 'application/json',
  },
});

// Request interceptor
http.interceptors.request.use(
  (config) => {
    const token = useAuthStore.getState().token;
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

// Response interceptor
http.interceptors.response.use(
  (response) => response.data,
  (error) => {
    // Handle errors consistently
    const message = error.response?.data?.message || 'An error occurred';
    // Toast or notification
    return Promise.reject(error);
  }
);

export { http };
```

### API Service Structure

```typescript
// services/travelService.ts
import { http } from '@/utils/request';
import type { TravelRequest, CreateRequestDto, Plan, CreatePlanDto } from '@/types';

export const travelService = {
  // Travel Requests
  async createRequest(data: CreateRequestDto): Promise<TravelRequest> {
    return http.post('/travel-requests', data);
  },
  
  async getRequest(id: string): Promise<TravelRequest> {
    return http.get(`/travel-requests/${id}`);
  },
  
  async listRequests(params: ListParams): Promise<PageResponse<TravelRequest>> {
    return http.get('/travel-requests', { params });
  },
  
  // Plans
  async getPlans(requestId: string): Promise<Plan[]> {
    return http.get(`/travel-requests/${requestId}/plans`);
  },
  
  async createPlan(data: CreatePlanDto): Promise<Plan> {
    return http.post('/plans', data);
  },
  
  async getPlan(id: string): Promise<Plan> {
    return http.get(`/plans/${id}`);
  },
};
```

### Error Handling

```typescript
// types/api.ts
export interface ApiError {
  code: number;
  message: string;
  details?: Record<string, string[]>;
}

export interface ApiResponse<T> {
  code: number;
  message: string;
  data: T;
  timestamp: string;
}

// Error codes
export const ErrorCodes = {
  VALIDATION_ERROR: 40001,
  UNAUTHORIZED: 40101,
  FORBIDDEN: 40301,
  NOT_FOUND: 40401,
  SERVER_ERROR: 50001,
} as const;
```

## Error Handling & User Feedback

### Global Error Boundary

```typescript
// components/ErrorBoundary.tsx
import { Component, ErrorInfo, ReactNode } from 'react';
import { Button } from '@/components/common';

interface Props {
  children: ReactNode;
}

interface State {
  hasError: boolean;
  error: Error | null;
}

export class ErrorBoundary extends Component<Props, State> {
  public state: State = { hasError: false, error: null };
  
  public static getDerivedStateFromError(error: Error): State {
    return { hasError: true, error };
  }
  
  public componentDidCatch(error: Error, errorInfo: ErrorInfo) {
    console.error('Error caught by boundary:', error, errorInfo);
  }
  
  public render() {
    if (this.state.hasError) {
      return (
        <div className="flex flex-col items-center justify-center min-h-[400px]">
          <h2 className="text-2xl font-bold text-gray-900 mb-4">
            Something went wrong
          </h2>
          <Button onClick={() => window.location.reload()}>
            Refresh Page
          </Button>
        </div>
      );
    }
    return this.props.children;
  }
}
```

### Toast Notifications

```typescript
// hooks/useToast.ts (or use a library like react-hot-toast)
import { useCallback } from 'react';

type ToastType = 'success' | 'error' | 'warning' | 'info';

export function useToast() {
  const showToast = useCallback((message: string, type: ToastType = 'info') => {
    // Implementation using toast library or custom
  }, []);
  
  return { showToast };
}
```

## Performance Targets

### Core Web Vitals

| Metric | Target | Measurement |
|--------|--------|-------------|
| LCP (Largest Contentful Paint) | < 2.5s | 75th percentile |
| FID (First Input Delay) | < 100ms | 75th percentile |
| CLS (Cumulative Layout Shift) | < 0.1 | 75th percentile |

### Application Performance

| Metric | Target | Description |
|--------|--------|-------------|
| FCP | < 1.5s | First Contentful Paint |
| TTI | < 3s | Time to Interactive |
| API Response (P95) | < 500ms | Excluding AI calls |
| Route Transition | < 300ms | Between pages |

### Optimization Strategies

1. **Code Splitting**: Route-based lazy loading
   ```typescript
   const TravelPlan = lazy(() => import('@/pages/TravelPlan'));
   ```

2. **Image Optimization**: WebP format, lazy loading
3. **Caching**: TanStack Query for API data
4. **Bundle Size**: Target < 200KB gzipped initial

## Responsive Design Requirements

### Mobile-First Approach

- Write base styles for mobile
- Use `md:`, `lg:` prefixes for larger screens
- Test on real devices (iOS Safari, Chrome Mobile)

### Touch Targets

- Minimum touch target: 44x44px
- Spacing between targets: 8px minimum
- Consider thumb zone for mobile

### Flexible Images

```css
img {
  max-width: 100%;
  height: auto;
  object-fit: cover;
}
```

## Testing Patterns

### Unit Testing with Vitest

```typescript
// components/TravelCard.test.tsx
import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent } from '@testing-library/react';
import { TravelCard } from './TravelCard';

describe('TravelCard', () => {
  const mockProps = {
    id: '1',
    title: 'Tokyo Adventure',
    destination: 'Tokyo, Japan',
    price: 2500,
    onSelect: vi.fn(),
  };
  
  it('renders correctly', () => {
    render(<TravelCard {...mockProps} />);
    expect(screen.getByText('Tokyo Adventure')).toBeInTheDocument();
    expect(screen.getByText('Tokyo, Japan')).toBeInTheDocument();
  });
  
  it('calls onSelect when clicked', () => {
    render(<TravelCard {...mockProps} />);
    fireEvent.click(screen.getByRole('article'));
    expect(mockProps.onSelect).toHaveBeenCalledWith('1');
  });
});
```

### Testing Best Practices

1. **Test behavior, not implementation**
2. **Use user-event for interactions**: `userEvent.click()`
3. **Mock API calls**: Mock service layer
4. **Test async components**: Use `waitFor()`, `findBy*()`
5. **Coverage target**: 70% minimum

## Accessibility (a11y)

### Requirements

- **Keyboard navigation**: All interactive elements accessible via keyboard
- **Focus management**: Visible focus indicators
- **Screen readers**: Proper ARIA labels
- **Color contrast**: Minimum 4.5:1 for text

### ARIA Pattern

```typescript
<button
  aria-label={`View details for ${title}`}
  aria-expanded={isOpen}
  aria-controls="details-panel"
>
  <Icon name="info" />
</button>
```

### Form Accessibility

```typescript
<label htmlFor="email" className="block text-sm font-medium text-gray-700">
  Email Address
</label>
<input
  id="email"
  type="email"
  aria-describedby="email-hint"
  aria-invalid={hasError}
/>
{hasError && (
  <p id="email-hint" className="text-red-500 text-sm" role="alert">
    Please enter a valid email address
  </p>
)}
```

## Code Style Guidelines

### TypeScript Strict Mode

```json
{
  "compilerOptions": {
    "strict": true,
    "noImplicitAny": true,
    "strictNullChecks": true,
    "strictFunctionTypes": true,
    "noUnusedLocals": true,
    "noUnusedParameters": true
  }
}
```

### Import Organization

```typescript
// 1. React and external libraries
import { useState, useEffect } from 'react';
import { useQuery } from '@tanstack/react-query';

// 2. Internal components
import { Button, Modal } from '@/components/common';
import { TravelCard } from '@/components/travel';

// 3. Hooks and stores
import { useAuthStore } from '@/store';

// 4. Types
import type { TravelRequest, User } from '@/types';

// 5. Utilities
import { formatCurrency, formatDate } from '@/utils';
```

### File Naming

| File Type | Convention | Examples |
|-----------|------------|----------|
| Component | PascalCase.tsx | `TravelCard.tsx` |
| Hook | useCamelCase.ts | `useTravel.ts` |
| Utility | camelCase.ts | `formatDate.ts` |
| Type | PascalCase.ts | `TravelRequest.ts` |
| Constant | UPPER_SNAKE_CASE.ts | `API_ENDPOINTS.ts` |
| Config | camelCase.ts | `router.tsx` |

## Routes

| Path | Component | Description |
|------|-----------|-------------|
| `/` | Home | Landing page |
| `/info-collection` | InfoCollection | Travel requirements form |
| `/plans` | PlansList | List of travel plans |
| `/plans/:id` | PlanDetail | Plan details |
| `/attractions` | Attractions | Scenic spots and dining |
| `/order-confirm` | OrderConfirm | Order confirmation |
| `*` | NotFound | 404 page |

---

*This specification is managed by OpenSpec. Refer to project.md for cross-project conventions.*
