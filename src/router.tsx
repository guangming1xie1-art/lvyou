import { createBrowserRouter } from 'react-router-dom'
import { Layout } from './components/common/Layout'
import { Home } from './pages/Home'
import { InfoCollection } from './pages/InfoCollection'
import { PlanDisplay } from './pages/PlanDisplay'
import { PlanDetail } from './pages/PlanDetail'
import { Attractions } from './pages/Attractions'
import { OrderConfirm } from './pages/OrderConfirm'
import { NotFound } from './pages/NotFound'

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
      <Layout>
        <InfoCollection />
      </Layout>
    ),
  },
  {
    path: '/plans',
    element: (
      <Layout>
        <PlanDisplay />
      </Layout>
    ),
  },
  {
    path: '/plans/:id',
    element: (
      <Layout>
        <PlanDetail />
      </Layout>
    ),
  },
  {
    path: '/attractions',
    element: (
      <Layout>
        <Attractions />
      </Layout>
    ),
  },
  {
    path: '/order-confirm',
    element: (
      <Layout>
        <OrderConfirm />
      </Layout>
    ),
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
