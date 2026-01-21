import { db } from './db'
import type { DbAttraction, DbRestaurant } from './types'

export function listAttractions(destination?: string): DbAttraction[] {
  if (!destination) return db.attractions
  return db.attractions.filter((a) => a.destination === destination)
}

export function getAttraction(id: string): DbAttraction | undefined {
  return db.attractions.find((a) => a.id === id)
}

export function searchAttractions(params: {
  destination?: string
  keyword?: string
}): DbAttraction[] {
  const keyword = (params.keyword || '').toLowerCase()
  return db.attractions.filter((a) => {
    if (params.destination && a.destination !== params.destination) return false
    if (!keyword) return true
    return (
      a.name.toLowerCase().includes(keyword) ||
      a.description.toLowerCase().includes(keyword) ||
      a.tags.some((t) => t.toLowerCase().includes(keyword))
    )
  })
}

export function listRestaurants(destination?: string): DbRestaurant[] {
  if (!destination) return db.restaurants
  return db.restaurants.filter((r) => r.destination === destination)
}

export function getRestaurant(id: string): DbRestaurant | undefined {
  return db.restaurants.find((r) => r.id === id)
}

export function searchRestaurants(params: {
  destination?: string
  keyword?: string
  cuisine_type?: string
}): DbRestaurant[] {
  const keyword = (params.keyword || '').toLowerCase()
  return db.restaurants.filter((r) => {
    if (params.destination && r.destination !== params.destination) return false
    if (params.cuisine_type && r.cuisine_type !== params.cuisine_type) return false
    if (!keyword) return true
    return (
      r.name.toLowerCase().includes(keyword) ||
      r.address.toLowerCase().includes(keyword) ||
      r.specialties.some((s) => s.toLowerCase().includes(keyword))
    )
  })
}
