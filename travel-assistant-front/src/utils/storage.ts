/**
 * 本地存储工具类
 */

// 存储键名常量
export const STORAGE_KEYS = {
  TOKEN: 'token',
  USER: 'user',
  TRAVEL_REQUEST: 'travel_request',
  SELECTED_PLAN: 'selected_plan',
} as const

/**
 * 设置本地存储
 */
export const setStorage = <T>(key: string, value: T): void => {
  try {
    const serializedValue = JSON.stringify(value)
    localStorage.setItem(key, serializedValue)
  } catch (error) {
    console.error('Error setting localStorage:', error)
  }
}

/**
 * 获取本地存储
 */
export const getStorage = <T>(key: string): T | null => {
  try {
    const serializedValue = localStorage.getItem(key)
    if (serializedValue === null) {
      return null
    }
    return JSON.parse(serializedValue) as T
  } catch (error) {
    console.error('Error getting localStorage:', error)
    return null
  }
}

/**
 * 移除本地存储
 */
export const removeStorage = (key: string): void => {
  try {
    localStorage.removeItem(key)
  } catch (error) {
    console.error('Error removing localStorage:', error)
  }
}

/**
 * 清除所有本地存储
 */
export const clearStorage = (): void => {
  try {
    localStorage.clear()
  } catch (error) {
    console.error('Error clearing localStorage:', error)
  }
}

/**
 * 会话存储工具
 */
export const sessionStorage = {
  set: <T>(key: string, value: T): void => {
    try {
      const serializedValue = JSON.stringify(value)
      window.sessionStorage.setItem(key, serializedValue)
    } catch (error) {
      console.error('Error setting sessionStorage:', error)
    }
  },

  get: <T>(key: string): T | null => {
    try {
      const serializedValue = window.sessionStorage.getItem(key)
      if (serializedValue === null) {
        return null
      }
      return JSON.parse(serializedValue) as T
    } catch (error) {
      console.error('Error getting sessionStorage:', error)
      return null
    }
  },

  remove: (key: string): void => {
    try {
      window.sessionStorage.removeItem(key)
    } catch (error) {
      console.error('Error removing sessionStorage:', error)
    }
  },

  clear: (): void => {
    try {
      window.sessionStorage.clear()
    } catch (error) {
      console.error('Error clearing sessionStorage:', error)
    }
  },
}
