import { ReactNode } from 'react'
import { useLocation } from 'react-router-dom'
import { Header } from './Header'
import { Footer } from './Footer'

interface LayoutProps {
  children: ReactNode
}

export const Layout = ({ children }: LayoutProps) => {
  const location = useLocation()
  const isChatPage = location.pathname === '/'

  return (
    <div className="min-h-screen flex flex-col">
      {!isChatPage && <Header />}
      <main className="flex-grow">{children}</main>
      {!isChatPage && <Footer />}
    </div>
  )
}
