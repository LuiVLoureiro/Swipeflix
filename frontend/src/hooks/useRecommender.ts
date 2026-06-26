import { useCallback, useEffect, useRef, useState } from 'react'
import { api } from '../api/client'
import type { Movie, Summary } from '../api/client'

export type DeckStatus = 'loading' | 'evolving' | 'ready' | 'empty' | 'error'

export function useRecommender() {
  const [queue, setQueue] = useState<Movie[]>([])
  const [summary, setSummary] = useState<Summary | null>(null)
  const [status, setStatus] = useState<DeckStatus>('loading')
  const [error, setError] = useState<string | null>(null)
  const lastEvolve = useRef(false)

  const loadBatch = useCallback(async (shouldEvolve: boolean) => {
    lastEvolve.current = shouldEvolve
    setStatus(shouldEvolve ? 'evolving' : 'loading')
    try {
      // So evolui quando o lote anterior foi realmente esgotado por swipe.
      // Sem isso, recarregar a pagina disparava /evolve de novo e inflava
      // a geracao sem nenhum feedback novo do usuario.
      if (shouldEvolve) {
        await api.evolve()
      }
      const batch = await api.getBatch()
      setSummary(await api.getSummary())
      if (batch.length === 0) {
        setQueue([])
        setStatus('empty')
        return
      }
      setQueue(batch)
      setStatus('ready')
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Nao foi possivel falar com a API')
      setStatus('error')
    }
  }, [])

  useEffect(() => {
    loadBatch(false)
  }, [loadBatch])

  useEffect(() => {
    if (status === 'ready' && queue.length === 0) {
      loadBatch(true)
    }
  }, [status, queue.length, loadBatch])

  const swipe = useCallback((movie: Movie, liked: boolean) => {
    setQueue((prev) => prev.filter((m) => m.id !== movie.id))
    void api.sendFeedback(movie.id, movie.title, liked)
  }, [])

  const retry = useCallback(() => loadBatch(lastEvolve.current), [loadBatch])

  return { queue, summary, status, error, swipe, retry }
}
