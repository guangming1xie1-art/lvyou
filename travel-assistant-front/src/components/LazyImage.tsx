/**
 * 图片懒加载组件
 * 提供占位符、加载状态和错误处理
 */
import React, { useState, useEffect, useRef } from 'react'

interface LazyImageProps {
  src: string
  alt: string
  className?: string
  placeholderSrc?: string
  threshold?: number
  onLoad?: () => void
  onError?: (error: Error) => void
}

/**
 * 懒加载图片组件
 * 
 * 功能:
 * - 视口可见时才加载图片
 * - 显示占位符图片
 * - 加载状态反馈
 * - 加载失败处理
 * 
 * @example
 * ```tsx
 * <LazyImage
 *   src="/images/hotel.jpg"
 *   alt="Hotel"
 *   className="w-full h-64 object-cover"
 *   placeholderSrc="/images/placeholder.svg"
 * />
 * ```
 */
export const LazyImage: React.FC<LazyImageProps> = ({
  src,
  alt,
  className = '',
  placeholderSrc = 'data:image/svg+xml,%3Csvg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 400 300"%3E%3Crect fill="%23f0f0f0" width="400" height="300"/%3E%3Ctext fill="%23999" font-family="sans-serif" font-size="30" dy="150" dx="50"%3ELoading...%3C/text%3E%3C/svg%3E',
  threshold = 0.1,
  onLoad,
  onError,
}) => {
  const [imageSrc, setImageSrc] = useState<string>(placeholderSrc)
  const [isLoading, setIsLoading] = useState(true)
  const [hasError, setHasError] = useState(false)
  const imgRef = useRef<HTMLImageElement>(null)

  useEffect(() => {
    // 检查浏览器是否支持 IntersectionObserver
    if (!('IntersectionObserver' in window)) {
      // 不支持则直接加载图片
      loadImage()
      return
    }

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            loadImage()
            // 加载后停止观察
            if (imgRef.current) {
              observer.unobserve(imgRef.current)
            }
          }
        })
      },
      {
        threshold,
        rootMargin: '50px', // 提前 50px 开始加载
      }
    )

    if (imgRef.current) {
      observer.observe(imgRef.current)
    }

    return () => {
      if (imgRef.current) {
        observer.unobserve(imgRef.current)
      }
    }
  }, [src, threshold])

  const loadImage = () => {
    const img = new Image()
    img.src = src

    img.onload = () => {
      setImageSrc(src)
      setIsLoading(false)
      setHasError(false)
      onLoad?.()
    }

    img.onerror = () => {
      setIsLoading(false)
      setHasError(true)
      onError?.(new Error(`Failed to load image: ${src}`))
    }
  }

  return (
    <div className={`relative ${className}`}>
      <img
        ref={imgRef}
        src={imageSrc}
        alt={alt}
        className={`
          ${className}
          ${isLoading ? 'blur-sm' : 'blur-0'}
          transition-all duration-300
        `}
      />
      
      {isLoading && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-100">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      )}

      {hasError && (
        <div className="absolute inset-0 flex items-center justify-center bg-gray-100">
          <div className="text-center text-gray-500">
            <svg
              className="mx-auto h-12 w-12 text-gray-400"
              fill="none"
              viewBox="0 0 24 24"
              stroke="currentColor"
            >
              <path
                strokeLinecap="round"
                strokeLinejoin="round"
                strokeWidth={2}
                d="M4 16l4.586-4.586a2 2 0 012.828 0L16 16m-2-2l1.586-1.586a2 2 0 012.828 0L20 14m-6-6h.01M6 20h12a2 2 0 002-2V6a2 2 0 00-2-2H6a2 2 0 00-2 2v12a2 2 0 002 2z"
              />
            </svg>
            <p className="mt-2 text-sm">加载失败</p>
          </div>
        </div>
      )}
    </div>
  )
}

/**
 * 背景图片懒加载组件
 */
interface LazyBackgroundImageProps {
  src: string
  className?: string
  children?: React.ReactNode
  threshold?: number
}

export const LazyBackgroundImage: React.FC<LazyBackgroundImageProps> = ({
  src,
  className = '',
  children,
  threshold = 0.1,
}) => {
  const [backgroundImage, setBackgroundImage] = useState<string>('none')
  const [isLoading, setIsLoading] = useState(true)
  const divRef = useRef<HTMLDivElement>(null)

  useEffect(() => {
    if (!('IntersectionObserver' in window)) {
      loadBackgroundImage()
      return
    }

    const observer = new IntersectionObserver(
      (entries) => {
        entries.forEach((entry) => {
          if (entry.isIntersecting) {
            loadBackgroundImage()
            if (divRef.current) {
              observer.unobserve(divRef.current)
            }
          }
        })
      },
      { threshold, rootMargin: '50px' }
    )

    if (divRef.current) {
      observer.observe(divRef.current)
    }

    return () => {
      if (divRef.current) {
        observer.unobserve(divRef.current)
      }
    }
  }, [src, threshold])

  const loadBackgroundImage = () => {
    const img = new Image()
    img.src = src

    img.onload = () => {
      setBackgroundImage(`url('${src}')`)
      setIsLoading(false)
    }

    img.onerror = () => {
      setIsLoading(false)
    }
  }

  return (
    <div
      ref={divRef}
      className={`
        ${className}
        ${isLoading ? 'bg-gray-100' : ''}
        transition-all duration-300
      `}
      style={{
        backgroundImage,
        backgroundSize: 'cover',
        backgroundPosition: 'center',
      }}
    >
      {isLoading && (
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
        </div>
      )}
      {children}
    </div>
  )
}

export default LazyImage
