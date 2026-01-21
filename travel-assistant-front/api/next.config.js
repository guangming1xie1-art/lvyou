/** @type {import('next').NextConfig} */
const nextConfig = {
  reactStrictMode: true,
  swcMinify: true,
  poweredByHeader: false,
  
  // API 路由配置
  experimental: {
    serverComponentsExternalPackages: [],
  },

  // 禁用图片优化（Mock API 不需要）
  images: {
    unoptimized: true,
  },

  // 环境变量
  env: {
    NEXT_PUBLIC_API_BASE_URL: process.env.NEXT_PUBLIC_API_BASE_URL || 'http://localhost:3001/api',
    MOCK_API_DEBUG: process.env.MOCK_API_DEBUG || 'false',
  },

  // 重定向和重写
  async redirects() {
    return []
  },

  async rewrites() {
    return {
      beforeFiles: [],
      afterFiles: [],
      fallback: [],
    }
  },
}

module.exports = nextConfig