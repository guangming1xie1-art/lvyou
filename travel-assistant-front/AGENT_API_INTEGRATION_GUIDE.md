# React 前端 Agent API 集成指南

## 概述

本文档描述了如何在 React 前端中集成 Agent REST API，实现搜索、推荐、预订功能的完整交互流程。

## 架构概览

```
前端 (React/Mobile)
       ↓
自定义 Hooks 层 (useSearch, useRecommend, useBook, useTaskStatus)
       ↓
API 服务层 (AgentApiService)
       ↓
HTTP 客户端 (axios + 拦截器)
       ↓
Agent REST API 层
       ↓
JavaAPIClient 层
       ↓
Java API (后端服务)
```

## 核心组件

### 1. API 服务层 (`src/services/agentApi.ts`)

AgentApiService 类提供了与后端 Agent REST API 的所有交互：

```typescript
import { AgentApiService } from '@/services/agentApi'

const agentApi = new AgentApiService({
  baseURL: 'http://localhost:8000',
  timeout: 30000,
  retries: 3,
})

// 或者使用便捷方法
import { agentApiService } from '@/services/agentApi'
const result = await agentApiService.search(searchParams)
```

#### 核心方法

- **search(params)** - 搜索航班和酒店
- **recommend(params)** - 获取旅行推荐
- **book(params)** - 创建预订
- **getStatus(taskId)** - 获取任务状态
- **getTasks(params)** - 获取任务列表
- **healthCheck()** - 健康检查

#### 特性

- ✅ 集中的 API 端点配置
- ✅ 请求拦截（添加 headers、token 等）
- ✅ 响应拦截（统一错误处理）
- ✅ 重试机制（网络失败时）
- ✅ 请求超时控制
- ✅ 详细的日志记录

### 2. 自定义 Hooks

#### useSearch Hook

```typescript
import { useSearch } from '@/hooks/useSearch'

const SearchComponent = () => {
  const { data, loading, error, search, outboundFlights, hotels } = useSearch()
  
  const handleSearch = () => {
    search({
      origin: 'Beijing',
      destination: 'Tokyo',
      departure_date: '2025-02-01',
      passengers: 2,
      trip_type: 'round-trip'
    })
  }
  
  if (loading) return <div>搜索中...</div>
  if (error) return <div>错误: {error.message}</div>
  
  return (
    <div>
      <button onClick={handleSearch}>搜索</button>
      {data && (
        <div>
          <h3>去程航班 ({data.outbound_flights.length})</h3>
          {data.outbound_flights.map(flight => (
            <FlightCard key={flight.id} flight={flight} />
          ))}
          <h3>酒店 ({data.hotels.length})</h3>
          {data.hotels.map(hotel => (
            <HotelCard key={hotel.id} hotel={hotel} />
          ))}
        </div>
      )}
    </div>
  )
}
```

#### useRecommend Hook

```typescript
import { useRecommend } from '@/hooks/useRecommend'

const RecommendComponent = () => {
  const { data, loading, error, recommend } = useRecommend()
  
  const getRecommendations = () => {
    recommend({
      destination: 'Tokyo',
      start_date: '2025-02-01',
      end_date: '2025-02-05',
      include_attractions: true,
      include_weather: true,
      include_reviews: true
    })
  }
  
  return (
    <div>
      {loading && <div>获取推荐中...</div>}
      {error && <div>错误: {error.message}</div>}
      {data && (
        <div>
          <h2>{data.destination_info.name}</h2>
          <p>{data.destination_info.description}</p>
          
          <h3>景点推荐</h3>
          {data.attractions.map(attraction => (
            <AttractionCard key={attraction.id} attraction={attraction} />
          ))}
          
          <h3>天气预报</h3>
          {data.weather_forecast.map(day => (
            <WeatherCard key={day.date} weather={day} />
          ))}
          
          <h3>用户评价</h3>
          <ReviewSummary reviews={data.reviews} />
        </div>
      )}
    </div>
  )
}
```

#### useBook Hook

```typescript
import { useBook } from '@/hooks/useBook'

const BookingComponent = () => {
  const { data, loading, error, book } = useBook()
  
  const handleBooking = () => {
    book({
      customer_info: {
        name: '张三',
        email: 'zhangsan@example.com',
        phone: '13800138000',
        address: '北京市朝阳区'
      },
      trip_details: {
        destination: 'Tokyo',
        departure_date: '2025-02-01',
        return_date: '2025-02-05',
        travelers: 2,
        trip_type: 'round-trip',
        cabin_class: 'business'
      },
      selected_flight: {
        id: 'flight_123',
        flight_number: 'NH123',
        price: 5000,
        passengers: 2
      },
      selected_hotel: {
        id: 'hotel_456',
        name: '东京王子酒店',
        check_in: '2025-02-01',
        check_out: '2025-02-05',
        rooms: 1,
        guests: 2,
        price_per_night: 800,
        total_nights: 4
      },
      passengers: [
        {
          first_name: '三',
          last_name: '张',
          date_of_birth: '1990-01-01'
        },
        {
          first_name: '四',
          last_name: '李',
          date_of_birth: '1992-05-15'
        }
      ],
      additional_services: [
        {
          type: 'insurance',
          name: '旅行保险',
          price: 200,
          quantity: 2
        }
      ],
      special_requests: '请安排靠窗座位'
    })
  }
  
  if (loading) return <div>预订中...</div>
  if (error) return <div>错误: {error.message}</div>
  
  return (
    <div>
      <button onClick={handleBooking}>确认预订</button>
      {data && (
        <BookingConfirmation booking={data} />
      )}
    </div>
  )
}
```

#### useTaskStatus Hook

```typescript
import { useTaskStatus } from '@/hooks/useTaskStatus'

const TaskStatusComponent = ({ taskId }) => {
  const { status, progress, isCompleted, isFailed, data } = useTaskStatus(taskId, {
    onComplete: (result) => {
      console.log('任务完成:', result)
      // 可以在这里处理成功后的逻辑
    },
    onError: (error) => {
      console.error('任务失败:', error)
      // 可以在这里处理错误后的逻辑
    }
  })
  
  return (
    <div className="task-status">
      <div className="status-indicator">
        <span className={`status ${status}`}>{status}</span>
        <div className="progress-bar">
          <div 
            className="progress-fill" 
            style={{ width: `${progress * 100}%` }}
          />
        </div>
        <span className="progress-text">{Math.round(progress * 100)}%</span>
      </div>
      
      {isCompleted && (
        <div className="completion-message">
          ✅ 任务已完成！
          <TaskResult result={data?.result} />
        </div>
      )}
      
      {isFailed && (
        <div className="error-message">
          ❌ 任务失败: {data?.error?.message}
        </div>
      )}
      
      {status === 'processing' && (
        <div className="processing-message">
          🔄 正在处理中...
        </div>
      )}
    </div>
  )
}
```

### 3. 类型定义

所有 API 相关类型都在 `src/types/api.ts` 中定义：

```typescript
import type {
  SearchRequest,
  SearchResponse,
  RecommendRequest,
  RecommendResponse,
  BookRequest,
  BookResponse,
  StatusResponse,
  FlightInfo,
  HotelInfo,
  DestinationInfo,
  AttractionInfo,
  WeatherDay,
  ReviewSummary
} from '@/types/api'
```

#### 核心类型说明

**SearchRequest**:
```typescript
{
  origin: string           // 出发地
  destination: string     // 目的地
  departure_date: string  // 出发日期
  passengers: number     // 乘客数量
  return_date?: string   // 返程日期（可选）
  cabin_class?: string    // 舱位等级
  trip_type?: 'one-way' | 'round-trip'
}
```

**SearchResponse**:
```typescript
{
  outbound_flights: FlightInfo[]
  return_flights?: FlightInfo[]
  hotels: HotelInfo[]
  search_metadata: SearchMetadata
  task_id: string
  error?: ErrorDetail
}
```

### 4. 环境配置

在 `.env` 文件中配置：

```env
# Agent API 配置
VITE_AGENT_API_BASE_URL=http://localhost:8000
VITE_API_TIMEOUT=30000
VITE_ENABLE_TASK_POLLING=true
VITE_TASK_POLLING_INTERVAL=2000
```

## 完整使用示例

### 搜索页面组件

```tsx
// src/pages/SearchPage.tsx
import React, { useState } from 'react'
import { useSearch } from '@/hooks/useSearch'
import { useTaskStatus } from '@/hooks/useTaskStatus'
import type { SearchRequest } from '@/types/api'

const SearchPage: React.FC = () => {
  const [searchParams, setSearchParams] = useState<SearchRequest>({
    origin: '',
    destination: '',
    departure_date: '',
    passengers: 1,
    trip_type: 'round-trip'
  })
  
  const { data: searchData, loading: searchLoading, error: searchError, search } = useSearch()
  const { data: taskData } = useTaskStatus(searchData?.task_id)
  
  const handleSearch = (e: React.FormEvent) => {
    e.preventDefault()
    search(searchParams)
  }
  
  const handleInputChange = (field: keyof SearchRequest, value: string | number) => {
    setSearchParams(prev => ({ ...prev, [field]: value }))
  }
  
  return (
    <div className="search-page">
      <h1>搜索航班和酒店</h1>
      
      <form onSubmit={handleSearch} className="search-form">
        <input
          type="text"
          placeholder="出发地"
          value={searchParams.origin}
          onChange={(e) => handleInputChange('origin', e.target.value)}
        />
        <input
          type="text"
          placeholder="目的地"
          value={searchParams.destination}
          onChange={(e) => handleInputChange('destination', e.target.value)}
        />
        <input
          type="date"
          placeholder="出发日期"
          value={searchParams.departure_date}
          onChange={(e) => handleInputChange('departure_date', e.target.value)}
        />
        <input
          type="number"
          placeholder="乘客数量"
          value={searchParams.passengers}
          onChange={(e) => handleInputChange('passengers', parseInt(e.target.value))}
        />
        <select
          value={searchParams.trip_type}
          onChange={(e) => handleInputChange('trip_type', e.target.value as 'one-way' | 'round-trip')}
        >
          <option value="one-way">单程</option>
          <option value="round-trip">往返</option>
        </select>
        <button type="submit" disabled={searchLoading}>
          {searchLoading ? '搜索中...' : '搜索'}
        </button>
      </form>
      
      {/* 任务状态显示 */}
      {searchData?.task_id && taskData && (
        <TaskStatus taskId={searchData.task_id} />
      )}
      
      {/* 搜索结果 */}
      {searchError && (
        <div className="error">错误: {searchError.message}</div>
      )}
      
      {searchData && (
        <div className="search-results">
          <div className="flights-section">
            <h2>去程航班 ({searchData.outbound_flights.length})</h2>
            {searchData.outbound_flights.map(flight => (
              <FlightCard key={flight.id} flight={flight} />
            ))}
          </div>
          
          {searchData.return_flights && (
            <div className="flights-section">
              <h2>返程航班 ({searchData.return_flights.length})</h2>
              {searchData.return_flights.map(flight => (
                <FlightCard key={flight.id} flight={flight} />
              ))}
            </div>
          )}
          
          <div className="hotels-section">
            <h2>推荐酒店 ({searchData.hotels.length})</h2>
            {searchData.hotels.map(hotel => (
              <HotelCard key={hotel.id} hotel={hotel} />
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

// 任务状态组件
const TaskStatus: React.FC<{ taskId: string }> = ({ taskId }) => {
  const { status, progress, isCompleted, isFailed } = useTaskStatus(taskId)
  
  return (
    <div className="task-status">
      <div className="status">
        <span className={`status-badge ${status}`}>{status}</span>
        <div className="progress">
          <div className="progress-bar">
            <div 
              className="progress-fill" 
              style={{ width: `${progress * 100}%` }}
            />
          </div>
          <span className="progress-text">{Math.round(progress * 100)}%</span>
        </div>
      </div>
    </div>
  )
}

export default SearchPage
```

### 预订页面组件

```tsx
// src/pages/BookingPage.tsx
import React, { useState } from 'react'
import { useBook } from '@/hooks/useBook'
import { useTaskStatus } from '@/hooks/useTaskStatus'
import type { BookRequest } from '@/types/api'

const BookingPage: React.FC = () => {
  const [bookingData, setBookingData] = useState<BookRequest>({
    customer_info: {
      name: '',
      email: '',
      phone: '',
      address: ''
    },
    trip_details: {
      destination: '',
      departure_date: '',
      return_date: '',
      travelers: 1,
      trip_type: 'round-trip'
    },
    passengers: [],
    selected_flight: undefined,
    selected_hotel: undefined
  })
  
  const { data: bookingData, loading: bookingLoading, error: bookingError, book } = useBook()
  const { data: taskData } = useTaskStatus(bookingData?.task_id)
  
  const handleBooking = (e: React.FormEvent) => {
    e.preventDefault()
    book(bookingData)
  }
  
  return (
    <div className="booking-page">
      <h1>预订详情</h1>
      
      <form onSubmit={handleBooking} className="booking-form">
        {/* 客户信息 */}
        <section>
          <h2>客户信息</h2>
          <input
            type="text"
            placeholder="姓名"
            value={bookingData.customer_info.name}
            onChange={(e) => setBookingData(prev => ({
              ...prev,
              customer_info: { ...prev.customer_info, name: e.target.value }
            }))}
          />
          <input
            type="email"
            placeholder="邮箱"
            value={bookingData.customer_info.email}
            onChange={(e) => setBookingData(prev => ({
              ...prev,
              customer_info: { ...prev.customer_info, email: e.target.value }
            }))}
          />
          <input
            type="tel"
            placeholder="电话"
            value={bookingData.customer_info.phone}
            onChange={(e) => setBookingData(prev => ({
              ...prev,
              customer_info: { ...prev.customer_info, phone: e.target.value }
            }))}
          />
        </section>
        
        {/* 行程信息 */}
        <section>
          <h2>行程信息</h2>
          <input
            type="text"
            placeholder="目的地"
            value={bookingData.trip_details.destination}
            onChange={(e) => setBookingData(prev => ({
              ...prev,
              trip_details: { ...prev.trip_details, destination: e.target.value }
            }))}
          />
          <input
            type="date"
            placeholder="出发日期"
            value={bookingData.trip_details.departure_date}
            onChange={(e) => setBookingData(prev => ({
              ...prev,
              trip_details: { ...prev.trip_details, departure_date: e.target.value }
            }))}
          />
          <input
            type="number"
            placeholder="旅行人数"
            value={bookingData.trip_details.travelers}
            onChange={(e) => setBookingData(prev => ({
              ...prev,
              trip_details: { ...prev.trip_details, travelers: parseInt(e.target.value) }
            }))}
          />
        </section>
        
        <button type="submit" disabled={bookingLoading}>
          {bookingLoading ? '预订中...' : '确认预订'}
        </button>
      </form>
      
      {/* 预订状态 */}
      {bookingData?.task_id && taskData && (
        <TaskStatus taskId={bookingData.task_id} />
      )}
      
      {/* 预订确认 */}
      {bookingData && (
        <BookingConfirmation booking={bookingData} />
      )}
    </div>
  )
}

export default BookingPage
```

## 错误处理

API 服务层提供了统一的错误处理：

```typescript
// 自动重试机制
try {
  const result = await agentApiService.search(params)
  // 处理成功结果
} catch (error) {
  if (error.code === 'NETWORK_ERROR') {
    // 网络错误处理
  } else if (error.code === 'TIMEOUT_ERROR') {
    // 超时错误处理
  } else if (error.code === 'JAVA_API_ERROR') {
    // Java API 错误处理
  } else {
    // 其他错误处理
  }
}
```

## 状态管理

每个 Hook 都提供了详细的状态信息：

- `loading` - 请求是否进行中
- `error` - 错误信息
- `data` - 响应数据
- `isSuccess` - 是否成功
- `isError` - 是否失败

## 性能优化

### 1. React Query 缓存

```typescript
// 自动缓存搜索结果
const { data, refetch } = useQuery({
  queryKey: ['search', searchParams],
  queryFn: () => agentApiService.search(searchParams),
  staleTime: 1000 * 60 * 5, // 5分钟
  cacheTime: 1000 * 60 * 10, // 10分钟
})
```

### 2. 防抖搜索

```typescript
import { useDebounce } from '@/hooks/useDebounce'

const SearchComponent = () => {
  const [query, setQuery] = useState('')
  const debouncedQuery = useDebounce(query, 300)
  
  const { data } = useSearch()
  
  useEffect(() => {
    if (debouncedQuery) {
      search({ query: debouncedQuery })
    }
  }, [debouncedQuery])
}
```

## 调试和日志

API 服务层包含详细的日志记录：

```typescript
// 启用详细日志
localStorage.setItem('debug', 'agent-api')
```

## 测试

### 单元测试示例

```typescript
// __tests__/hooks/useSearch.test.ts
import { renderHook, act } from '@testing-library/react'
import { useSearch } from '@/hooks/useSearch'
import { agentApiService } from '@/services/agentApi'

jest.mock('@/services/agentApi')

describe('useSearch', () => {
  it('should search successfully', async () => {
    const mockResponse = {
      outbound_flights: [],
      hotels: [],
      task_id: 'task-123'
    }
    
    ;(agentApiService.search as jest.Mock).mockResolvedValue(mockResponse)
    
    const { result } = renderHook(() => useSearch())
    
    await act(async () => {
      await result.current.searchAsync({
        origin: 'Beijing',
        destination: 'Tokyo',
        departure_date: '2025-02-01',
        passengers: 1
      })
    })
    
    expect(result.current.data).toEqual(mockResponse)
    expect(result.current.loading).toBe(false)
  })
})
```

## 部署配置

### 生产环境配置

```env
VITE_AGENT_API_BASE_URL=https://api.yourapp.com
VITE_API_TIMEOUT=30000
VITE_ENABLE_TASK_POLLING=true
VITE_TASK_POLLING_INTERVAL=2000
```

### API 限流

```typescript
// 在 API 服务中添加限流
const rateLimiter = new RateLimiter({
  windowMs: 60000, // 1分钟
  max: 10, // 最多10个请求
})

const searchWithRateLimit = async (params: SearchRequest) => {
  await rateLimiter.acquire()
  return agentApiService.search(params)
}
```

## 常见问题

### Q: 如何处理任务长时间运行？

A: 使用 `useTaskStatus` Hook 的轮询功能，它会自动处理任务状态更新。

### Q: 如何优化用户体验？

A: 
1. 使用加载状态
2. 显示进度条
3. 提供重试机制
4. 缓存常用搜索

### Q: 如何处理离线情况？

A: 
1. 检测网络状态
2. 缓存搜索结果
3. 离线提示
4. 同步机制

## 相关文档

- [Agent REST API 文档](../travel-assistant-agent/REST_API_IMPLEMENTATION_SUMMARY.md)
- [JavaAPIClient 文档](../travel-assistant-agent/src/utils/java_api_client.py)
- [React Query 文档](https://tanstack.com/query/latest)

## 更新日志

### v1.0.0 (2025-01-12)
- ✅ 创建 AgentApiService 类
- ✅ 实现所有核心 Hooks
- ✅ 添加完整的类型定义
- ✅ 实现错误处理和重试机制
- ✅ 支持任务状态追踪和轮询
- ✅ 完整的文档和使用示例