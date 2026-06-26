import { useEffect, useState } from 'react'
import { animate, motion, useMotionValue, useTransform } from 'framer-motion'
import type { PanInfo } from 'framer-motion'
import type { Movie } from '../api/client'
import { genreHue } from '../lib/colors'
import { formatRuntime } from '../lib/format'

const SWIPE_THRESHOLD = 120
const SWIPE_VELOCITY = 600
const FLY_OUT_X = 600

type MovieCardProps = {
  movie: Movie
  isTop: boolean
  stackIndex: number
  forceExit: 'left' | 'right' | null
  onSwipe: (liked: boolean) => void
  onExitHandled: () => void
  onDragStateChange: (dragging: boolean) => void
}

export function MovieCard({
  movie,
  isTop,
  stackIndex,
  forceExit,
  onSwipe,
  onExitHandled,
  onDragStateChange,
}: MovieCardProps) {
  const [posterFailed, setPosterFailed] = useState(false)
  const [posterLoaded, setPosterLoaded] = useState(false)
  const showPoster = Boolean(movie.poster_url) && !posterFailed

  const x = useMotionValue(0)
  const rotate = useTransform(x, [-300, 300], [-16, 16])
  const cardOpacity = useTransform(x, [-FLY_OUT_X, -40, 0, 40, FLY_OUT_X], [0, 1, 1, 1, 0])
  const likeOpacity = useTransform(x, [20, 120], [0, 1])
  const nopeOpacity = useTransform(x, [-120, -20], [1, 0])
  const likeTintOpacity = useTransform(x, [0, 220], [0, 0.55])
  const nopeTintOpacity = useTransform(x, [-220, 0], [0.55, 0])

  useEffect(() => {
    if (!isTop || !forceExit) return
    const liked = forceExit === 'right'
    const controls = animate(x, liked ? FLY_OUT_X : -FLY_OUT_X, {
      duration: 0.35,
      ease: 'easeIn',
      onComplete: () => {
        onSwipe(liked)
        onExitHandled()
      },
    })
    return () => controls.stop()
  }, [forceExit, isTop])

  function handleDragEnd(_event: PointerEvent, info: PanInfo) {
    const passedThreshold =
      Math.abs(info.offset.x) > SWIPE_THRESHOLD || Math.abs(info.velocity.x) > SWIPE_VELOCITY
    if (!passedThreshold) {
      animate(x, 0, { type: 'spring', stiffness: 300, damping: 24 })
      onDragStateChange(false)
      return
    }
    const liked = info.offset.x > 0
    animate(x, liked ? FLY_OUT_X : -FLY_OUT_X, {
      duration: 0.3,
      ease: 'easeOut',
      onComplete: () => onSwipe(liked),
    })
  }

  const hue = genreHue(movie.genres[0] ?? movie.title)

  return (
    <motion.div
      className="neu-raised absolute inset-0 grid select-none grid-rows-[1fr_auto] overflow-hidden rounded-[28px]"
      style={{
        x: isTop ? x : 0,
        rotate: isTop ? rotate : 0,
        opacity: isTop ? cardOpacity : 1,
        zIndex: 10 - stackIndex,
      }}
      animate={!isTop ? { scale: 1 - stackIndex * 0.04, y: stackIndex * 14 } : undefined}
      drag={isTop ? 'x' : false}
      dragConstraints={{ left: 0, right: 0 }}
      dragElastic={1}
      dragMomentum={false}
      onDragStart={isTop ? () => onDragStateChange(true) : undefined}
      onDragEnd={isTop ? handleDragEnd : undefined}
    >
      <div
        className="relative flex min-h-0 items-end overflow-hidden p-5"
        style={{
          background: `linear-gradient(135deg, hsl(${hue} 70% 55%), hsl(${(hue + 40) % 360} 70% 45%))`,
        }}
      >
        {showPoster && !posterLoaded && (
          <div className="absolute inset-0 flex items-center justify-center">
            <div className="h-10 w-10 animate-spin rounded-full border-4 border-white/30 border-t-white" />
          </div>
        )}
        {showPoster && (
          <img
            src={movie.poster_url ?? undefined}
            alt={`Poster de ${movie.title}`}
            className={`absolute inset-0 h-full w-full object-cover transition-opacity duration-500 ${
              posterLoaded ? 'opacity-100' : 'opacity-0'
            }`}
            draggable={false}
            onLoad={() => setPosterLoaded(true)}
            onError={() => setPosterFailed(true)}
          />
        )}
        {showPoster && posterLoaded && (
          <div className="absolute inset-0 bg-gradient-to-t from-black/75 via-black/10 to-transparent" />
        )}
        <h2 className="relative line-clamp-2 text-2xl font-bold leading-tight tracking-tight text-white drop-shadow">
          {movie.title}
        </h2>
      </div>

      <div className="flex flex-wrap items-center gap-1.5 px-4 py-2">
        <span className="text-xs font-medium text-ink-soft">
          {movie.year} &middot; {formatRuntime(movie.runtime)} &middot; ⭐ {movie.rating.toFixed(1)}
        </span>
        {movie.genres.map((genre) => (
          <span
            key={genre}
            className="rounded-full px-2 py-0.5 text-[10px] font-semibold tracking-wide text-white uppercase"
            style={{ backgroundColor: `hsl(${genreHue(genre)} 65% 50%)` }}
          >
            {genre}
          </span>
        ))}
      </div>

      {isTop && (
        <>
          <motion.div
            className="pointer-events-none absolute inset-0"
            style={{
              opacity: likeTintOpacity,
              background: 'linear-gradient(135deg, transparent, var(--color-like))',
            }}
          />
          <motion.div
            className="pointer-events-none absolute inset-0"
            style={{
              opacity: nopeTintOpacity,
              background: 'linear-gradient(225deg, transparent, var(--color-nope))',
            }}
          />
          <motion.span
            style={{ opacity: likeOpacity }}
            className="pointer-events-none absolute top-8 left-6 -rotate-12 rounded-lg border-4 border-like px-3 py-1 text-2xl font-extrabold tracking-wider text-like"
          >
            LIKE
          </motion.span>
          <motion.span
            style={{ opacity: nopeOpacity }}
            className="pointer-events-none absolute top-8 right-6 rotate-12 rounded-lg border-4 border-nope px-3 py-1 text-2xl font-extrabold tracking-wider text-nope"
          >
            NOPE
          </motion.span>
        </>
      )}
    </motion.div>
  )
}
