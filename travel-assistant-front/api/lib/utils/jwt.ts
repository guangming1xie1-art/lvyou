import * as jwt from 'jsonwebtoken'
import type { PublicUser } from '../models/types'
import { nowIso, uuid } from './generators'

function requireEnv(name: string, fallback: string): string {
  return process.env[name] || fallback
}

export const JWT_SECRET = requireEnv('JWT_SECRET', 'dev-mock-secret-key-change-in-production')
export const JWT_EXPIRE_IN = requireEnv('JWT_EXPIRE_IN', '1h')
export const JWT_REFRESH_EXPIRE_IN = requireEnv('JWT_REFRESH_EXPIRE_IN', '7d')

export type JwtTokenType = 'access' | 'refresh'

export interface AccessTokenClaims {
  sub: string
  typ: 'access'
  username: string
  email: string
}

export interface RefreshTokenClaims {
  sub: string
  typ: 'refresh'
  jti: string
}

export function parseExpiresInToSeconds(expiresIn: string): number {
  const m = /^([0-9]+)([smhd])$/.exec(expiresIn.trim())
  if (!m) return 3600
  const value = Number(m[1])
  const unit = m[2]
  switch (unit) {
    case 's':
      return value
    case 'm':
      return value * 60
    case 'h':
      return value * 60 * 60
    case 'd':
      return value * 60 * 60 * 24
    default:
      return 3600
  }
}

export function issueAccessToken(user: PublicUser): { token: string; expires_in: number } {
  const claims: AccessTokenClaims = {
    sub: user.id,
    typ: 'access',
    username: user.username,
    email: user.email,
  }

  const token = jwt.sign(claims as object, JWT_SECRET, {
    algorithm: 'HS256',
    expiresIn: JWT_EXPIRE_IN,
  } as jwt.SignOptions)

  return { token, expires_in: parseExpiresInToSeconds(JWT_EXPIRE_IN) }
}

export function issueRefreshToken(user: PublicUser): { token: string; jti: string; expires_at: string } {
  const jti = uuid()
  const claims: RefreshTokenClaims = {
    sub: user.id,
    typ: 'refresh',
    jti,
  }

  const token = jwt.sign(claims as object, JWT_SECRET, {
    algorithm: 'HS256',
    expiresIn: JWT_REFRESH_EXPIRE_IN,
  } as jwt.SignOptions)

  const expiresSeconds = parseExpiresInToSeconds(JWT_REFRESH_EXPIRE_IN)
  const expires_at = new Date(Date.now() + expiresSeconds * 1000).toISOString()

  return { token, jti, expires_at }
}

export function verifyToken<T extends object>(token: string): T {
  return jwt.verify(token, JWT_SECRET, {
    algorithms: ['HS256'],
  }) as T
}

export function safeNowIso(): string {
  return nowIso()
}
