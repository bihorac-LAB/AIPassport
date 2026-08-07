import { lazy, Suspense } from 'react';
import { createBrowserRouter, RouterProvider } from 'react-router-dom';
import { QueryClient, QueryClientProvider } from '@tanstack/react-query';
import { ApiError } from '@/api/client';
import { AuthProvider } from '@/auth/AuthProvider';
import { RequireAuth } from '@/auth/RequireAuth';
import { AppShell } from '@/components/AppShell';
import { LoadingPage } from '@/components/Spinner';
import { ErrorBoundary } from '@/components/ErrorBoundary';
import {
  ForgotPasswordPage,
  RegisterPage,
  ResetPasswordPage,
  SignInPage,
} from '@/pages/AuthPages';

// Route-level code splitting: each screen and each module page is its own chunk.
const HomePage = lazy(() => import('@/pages/HomePage'));
const ModulePage = lazy(() => import('@/pages/ModulePage'));
const LessonPage = lazy(() => import('@/pages/LessonPage'));
const ProgressPage = lazy(() => import('@/pages/ProgressPage'));
const AccountPage = lazy(() => import('@/pages/AccountPage'));

const queryClient = new QueryClient({
  defaultOptions: {
    queries: {
      staleTime: 60 * 1000,
      refetchOnWindowFocus: false,
      retry: (failureCount, error) => {
        // Never retry an auth or validation failure; retry transient ones twice.
        if (error instanceof ApiError && !error.isTransient) return false;
        return failureCount < 2;
      },
    },
  },
});

function Screen({ children }: { children: React.ReactNode }) {
  return <Suspense fallback={<LoadingPage />}>{children}</Suspense>;
}

const router = createBrowserRouter([
  {
    element: <AppShell />,
    children: [
      { path: '/', element: <Screen><HomePage /></Screen> },
      { path: '/modules/:moduleKey', element: <Screen><ModulePage /></Screen> },
      { path: '/modules/:moduleKey/:pageKey', element: <Screen><LessonPage /></Screen> },
      {
        path: '/progress',
        element: (
          <RequireAuth>
            <Screen>
              <ProgressPage />
            </Screen>
          </RequireAuth>
        ),
      },
      {
        path: '/account',
        element: (
          <RequireAuth>
            <Screen>
              <AccountPage />
            </Screen>
          </RequireAuth>
        ),
      },
      { path: '/sign-in', element: <SignInPage /> },
      { path: '/register', element: <RegisterPage /> },
      { path: '/forgot-password', element: <ForgotPasswordPage /> },
      { path: '/reset-password', element: <ResetPasswordPage /> },
      {
        path: '*',
        element: (
          <div className="content-width page">
            <h1 className="page__title">Page not found</h1>
            <p className="page__lede">
              <a href="/">Back to the modules</a>
            </p>
          </div>
        ),
      },
    ],
  },
]);

export function App() {
  return (
    <ErrorBoundary>
      <QueryClientProvider client={queryClient}>
        <AuthProvider>
          <RouterProvider router={router} />
        </AuthProvider>
      </QueryClientProvider>
    </ErrorBoundary>
  );
}
