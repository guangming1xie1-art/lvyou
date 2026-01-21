import { randomUUID } from 'crypto'

export function uuid(): string {
  return randomUUID()
}

export function nowIso(): string {
  return new Date().toISOString()
}

export function id(prefix: string): string {
  return `${prefix}_${uuid().replaceAll('-', '').slice(0, 16)}`
}

export function clamp(n: number, min: number, max: number): number {
  return Math.max(min, Math.min(max, n))
}

export function randomInt(minInclusive: number, maxInclusive: number): number {
  const min = Math.ceil(minInclusive)
  const max = Math.floor(maxInclusive)
  return Math.floor(Math.random() * (max - min + 1)) + min
}

export function pickOne<T>(arr: T[]): T {
  if (arr.length === 0) throw new Error('pickOne called with empty array')
  return arr[randomInt(0, arr.length - 1)]
}

export function pickMany<T>(arr: T[], count: number): T[] {
  const copy = [...arr]
  const result: T[] = []
  for (let i = 0; i < Math.min(count, copy.length); i += 1) {
    const idx = randomInt(0, copy.length - 1)
    result.push(copy[idx] as T)
    copy.splice(idx, 1)
  }
  return result
}

export async function delay(ms: number): Promise<void> {
  await new Promise<void>((resolve) => setTimeout(resolve, ms))
}
