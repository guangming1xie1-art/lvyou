import { db } from './db'
import type { DbUser, PublicUser } from './types'
import { hashPassword } from '../utils/password'
import { nowIso, uuid } from '../utils/generators'

export function toPublicUser(u: DbUser): PublicUser {
  // eslint-disable-next-line @typescript-eslint/no-unused-vars
  const { password_hash, ...rest } = u
  return rest
}

export function findUserById(id: string): DbUser | undefined {
  return db.users.find((u) => u.id === id)
}

export function findUserByUsername(username: string): DbUser | undefined {
  return db.users.find((u) => u.username.toLowerCase() === username.toLowerCase())
}

export function findUserByEmail(email: string): DbUser | undefined {
  return db.users.find((u) => u.email.toLowerCase() === email.toLowerCase())
}

export async function createUser(params: {
  username: string
  email: string
  password: string
}): Promise<DbUser> {
  const created_at = nowIso()

  const user: DbUser = {
    id: uuid(),
    username: params.username,
    email: params.email,
    is_active: true,
    created_at,
    last_login: null,
    password_hash: await hashPassword(params.password),
  }

  db.users.push(user)
  return user
}

export function touchLastLogin(userId: string): void {
  const user = findUserById(userId)
  if (!user) return
  user.last_login = nowIso()
}
