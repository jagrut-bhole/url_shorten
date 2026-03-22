import { getSession, signOut } from "next-auth/react";

export async function apiFetch(path: string, options: RequestInit = {}) {
    const session = await getSession();

    if(session?.error === "RefreshFailed") {
        signOut();
        throw new Error("Session expired")
    }

    const res = await fetch(`${process.env.BACKEND_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      Authorization: `Bearer ${session?.accessToken}`,
      ...options.headers,
    },
  })

  if (!res.ok) {
    const error = await res.json()
    throw new Error(error.detail || "API error")
  }

  return res.json()
}