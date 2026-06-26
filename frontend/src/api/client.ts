const BASE_URL = import.meta.env.VITE_API_URL ?? 'http://localhost:8000/api'

export type Movie = {
  id: string
  title: string
  year: number
  genres: string[]
  rating: number
  votes: number
  runtime: number
  poster_url: string | null
}

export type GenomeSummary = {
  top_genres: [string, number][]
  least_liked_genres: [string, number][]
  w_rating: number
  w_votes: number
  w_year: number
  w_runtime: number
  preferred_runtime_norm: number
}

export type Summary = {
  generation: number
  population_size: number
  fitness_mean: number
  fitness_best: number
  best_genome: GenomeSummary
  total_feedback: number
  total_shown: number
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  const res = await fetch(`${BASE_URL}${path}`, {
    headers: { 'Content-Type': 'application/json' },
    ...init,
  })
  if (!res.ok) {
    throw new Error(`Swipeflix API ${path} falhou com status ${res.status}`)
  }
  return res.json() as Promise<T>
}

export const api = {
  getBatch: (n?: number) => request<Movie[]>(`/movies/batch${n ? `?n=${n}` : ''}`),
  sendFeedback: (movieId: string, title: string, liked: boolean) =>
    request<{ ok: boolean }>('/feedback', {
      method: 'POST',
      body: JSON.stringify({ movie_id: movieId, title, liked }),
    }),
  evolve: () => request<Summary>('/evolve', { method: 'POST' }),
  getSummary: () => request<Summary>('/summary'),
}
