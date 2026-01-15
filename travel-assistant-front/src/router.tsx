import { createBrowserRouter, Navigate } from 'react-router-dom'
import { Layout } from './components/common/Layout'
import ChatInterfacePage from './pages/ChatInterface'
import { NotFound } from './pages/NotFound'
import Login from './pages/Login'
import Register from './pages/Register'
import ProtectedRoute from './components/ProtectedRoute'

export const router = createBrowserRouter([
  {
    path: '/',
    element: (
      <ProtectedRoute>
        <Layout>
          <ChatInterfacePage />
        </Layout>
      </ProtectedRoute>
    ),
  },
  {
    path: '/login',
    element: <Login />,
  },
  {
    path: '/register',
    element: <Register />,
  },
  {
    path: '/404',
    element: (
      <Layout>
        <NotFound />
      </Layout>
    ),
  },
  {
    path: '*',
    element: <Navigate to="/404" replace />,
  },
])
