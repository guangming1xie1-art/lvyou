/**
 * 懒加载工具
 * 提供路由级别的代码分割支持
 */
import React, { Suspense, ComponentType, LazyExoticComponent } from 'react'

/**
 * 加载中组件
 */
const LoadingFallback: React.FC = () => (
  <div className="flex items-center justify-center min-h-screen">
    <div className="text-center">
      <div className="inline-block animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600"></div>
      <p className="mt-4 text-gray-600">加载中...</p>
    </div>
  </div>
)

/**
 * 错误边界组件
 */
interface ErrorBoundaryState {
  hasError: boolean
  error?: Error
}

class ErrorBoundary extends React.Component<
  { children: React.ReactNode },
  ErrorBoundaryState
> {
  constructor(props: { children: React.ReactNode }) {
    super(props)
    this.state = { hasError: false }
  }

  static getDerivedStateFromError(error: Error): ErrorBoundaryState {
    return { hasError: true, error }
  }

  componentDidCatch(error: Error, errorInfo: React.ErrorInfo) {
    console.error('组件加载错误:', error, errorInfo)
  }

  render() {
    if (this.state.hasError) {
      return (
        <div className="flex items-center justify-center min-h-screen">
          <div className="text-center">
            <h2 className="text-2xl font-bold text-red-600 mb-4">页面加载失败</h2>
            <p className="text-gray-600 mb-4">
              {this.state.error?.message || '未知错误'}
            </p>
            <button
              onClick={() => window.location.reload()}
              className="px-4 py-2 bg-blue-600 text-white rounded hover:bg-blue-700"
            >
              重新加载
            </button>
          </div>
        </div>
      )
    }

    return this.props.children
  }
}

/**
 * 懒加载包装器
 * 
 * @param importFunc - 动态导入函数
 * @param fallback - 自定义加载中组件
 * @returns 包装后的组件
 * 
 * @example
 * ```tsx
 * // 在路由配置中使用
 * const HomePage = lazyLoad(() => import('./pages/HomePage'))
 * 
 * // 使用自定义加载组件
 * const Dashboard = lazyLoad(
 *   () => import('./pages/Dashboard'),
 *   <div>加载仪表盘中...</div>
 * )
 * ```
 */
export function lazyLoad<T extends ComponentType<any>>(
  importFunc: () => Promise<{ default: T }>,
  fallback?: React.ReactNode
): React.FC {
  const LazyComponent = React.lazy(importFunc)

  return function LazyLoadedComponent(props: any) {
    return (
      <ErrorBoundary>
        <Suspense fallback={fallback || <LoadingFallback />}>
          <LazyComponent {...props} />
        </Suspense>
      </ErrorBoundary>
    )
  }
}

/**
 * 预加载组件
 * 
 * @param importFunc - 动态导入函数
 * @returns Promise
 * 
 * @example
 * ```tsx
 * // 鼠标悬停时预加载
 * <Link
 *   to="/dashboard"
 *   onMouseEnter={() => preloadComponent(() => import('./pages/Dashboard'))}
 * >
 *   Dashboard
 * </Link>
 * ```
 */
export function preloadComponent<T>(
  importFunc: () => Promise<{ default: T }>
): Promise<{ default: T }> {
  return importFunc()
}

/**
 * 带重试机制的懒加载
 * 
 * @param importFunc - 动态导入函数
 * @param retries - 重试次数
 * @returns Promise
 */
export function lazyLoadWithRetry<T>(
  importFunc: () => Promise<{ default: T }>,
  retries = 3
): Promise<{ default: T }> {
  return new Promise((resolve, reject) => {
    const attemptLoad = (retriesLeft: number) => {
      importFunc()
        .then(resolve)
        .catch((error) => {
          if (retriesLeft === 0) {
            reject(error)
            return
          }

          console.warn(
            `组件加载失败，剩余重试次数: ${retriesLeft}`,
            error
          )

          // 延迟后重试
          setTimeout(() => {
            attemptLoad(retriesLeft - 1)
          }, 1000)
        })
    }

    attemptLoad(retries)
  })
}

/**
 * 路由懒加载辅助函数
 * 自动处理重试和错误
 */
export function lazyRoute<T extends ComponentType<any>>(
  importFunc: () => Promise<{ default: T }>
): LazyExoticComponent<T> {
  return React.lazy(() => lazyLoadWithRetry(importFunc))
}

export default lazyLoad
