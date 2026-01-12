import { createBrowserRouter } from 'react-router-dom'
import { Layout } from './components/common/Layout'
import { Home } from './pages/Home'
import { InfoCollection } from './pages/InfoCollection'
import { PlanDisplay } from './pages/PlanDisplay'
import { PlanDetail } from './pages/PlanDetail'
import { Attractions } from './pages/Attractions'
import { OrderConfirm } from './pages/OrderConfirm'
import { NotFound } from './pages/NotFound'
import Login from './pages/Login'
import Register from './pages/Register'
import ProtectedRoute from './components/ProtectedRoute'

export const router = createBrowserRouter([
  {
    path: '/',
    element: (
      <Layout>
        <Home />
      </Layout>
    ),
  },
  {
    path: '/info-collection',
    element: (
      <ProtectedRoute>
        <Layout>
          <InfoCollection />
        </Layout>
      </ProtectedRoute>
    ),
  },
  {
    path: '/plan-display',
    element: (
      <ProtectedRoute>
        <Layout>
          <PlanDisplay />
        </Layout>
      </ProtectedRoute>
    ),
  },
  {
    path: '/plan-detail',
    element: (
      <ProtectedRoute>
        <Layout>
          <PlanDetail />
        </Layout>
      </ProtectedRoute>
    ),
  },
  {
    path: '/attractions',
    element: (
      <ProtectedRoute>
        <Layout>
          <Attractions />
        </Layout>
      </ProtectedRoute>
    ),
  },
  {
    path: '/order-confirm',
    element: (
      <ProtectedRoute>
        <Layout>
          <OrderConfirm />
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
    path: '*',
    element: (
      <Layout>
        <NotFound />
      </Layout>
    ),
  },
])
