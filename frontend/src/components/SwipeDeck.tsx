import type { Movie } from '../api/client'
import { MovieCard } from './MovieCard'

interface SwipeDeckProps {
  queue: Movie[]
  forceExit: 'left' | 'right' | null
  onSwipe: (movie: Movie, liked: boolean) => void
  onExitHandled: () => void
  onDragStateChange: (dragging: boolean) => void
}

const VISIBLE_CARDS = 3

export function SwipeDeck({ queue, forceExit, onSwipe, onExitHandled, onDragStateChange }: SwipeDeckProps) {
  const visible = queue.slice(0, VISIBLE_CARDS)

  if (visible.length === 0) {
    return (
      <div className="neu-inset flex h-full w-full items-center justify-center rounded-[28px] p-6 text-center text-ink-soft">
        Sem mais filmes por agora.
      </div>
    )
  }

  return (
    <>
      {visible.map((movie, index) => (
        <MovieCard
          key={movie.id}
          movie={movie}
          isTop={index === 0}
          stackIndex={index}
          forceExit={index === 0 ? forceExit : null}
          onSwipe={(liked) => onSwipe(movie, liked)}
          onExitHandled={onExitHandled}
          onDragStateChange={onDragStateChange}
        />
      ))}
    </>
  )
}
