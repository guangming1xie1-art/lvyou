import { describe, it, expect } from 'vitest'

describe('Basic Tests', () => {
  it('should pass basic test', () => {
    expect(1 + 1).toBe(2)
  })

  it('should test string', () => {
    expect('Hello World').toBe('Hello World')
  })
})
