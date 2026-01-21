/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: false,
  async rewrites() {
    return [
      { source: '/chat', destination: '/api/chat' },
      { source: '/agent/:path*', destination: '/api/agent/:path*' },
      { source: '/auth/:path*', destination: '/api/auth/:path*' },
      { source: '/travel/:path*', destination: '/api/v1/travel/:path*' },
      { source: '/attractions/:path*', destination: '/api/v1/attractions/:path*' },
      { source: '/restaurants/:path*', destination: '/api/v1/restaurants/:path*' },
      { source: '/orders/:path*', destination: '/api/v1/orders/:path*' },
    ]
  },
}

export default nextConfig
