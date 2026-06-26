import { useState, type ReactNode } from 'react'
import { motion } from 'framer-motion'
import { ActionButtons } from './components/ActionButtons'
import { LoadingCard } from './components/LoadingCard'
import { StatsBar } from './components/StatsBar'
import { SwipeDeck } from './components/SwipeDeck'
import { useRecommender } from './hooks/useRecommender'

type ExitDirection = 'left' | 'right' | null

function DeckPlaceholder({ children }: { children: ReactNode }) {
  return (
    <div className="neu-inset flex h-full w-full items-center justify-center rounded-[28px] p-6 text-center text-ink-soft">
      {children}
    </div>
  )
}

function App() {
  const { queue, summary, status, error, swipe, retry } = useRecommender()
  const [forceExit, setForceExit] = useState<ExitDirection>(null)
  const [dragging, setDragging] = useState(false)
  const interactive = status === 'ready' && queue.length > 0 && !forceExit
  const showHint = interactive && !dragging

  function trigger(direction: 'left' | 'right') {
    if (!interactive) return
    setForceExit(direction)
  }

  return (
    <main className="relative grid h-dvh grid-rows-[auto_auto] content-center justify-items-center gap-4 p-4 sm:gap-6 sm:p-6 lg:p-10">
      <header className="text-center">
        <h1 className="text-2xl font-extrabold tracking-tight text-ink sm:text-3xl">Swipeflix</h1>
        <p className="mx-auto mt-1 max-w-[18rem] text-sm leading-snug text-ink-soft">
          Curta filmes e deixe o algoritmo genético aprender seu gosto.
        </p>
      </header>

      <div className="flex w-full max-w-[22rem] flex-col items-center gap-2 sm:max-w-[24rem]">
        <div className="relative aspect-[3/4] h-auto w-full max-h-[60dvh]">
          {status === 'loading' && <LoadingCard label="Carregando filmes..." />}
          {status === 'evolving' && <LoadingCard label="Evoluindo geração..." />}
          {status === 'empty' && <DeckPlaceholder>Você avaliou todo o catálogo disponível!</DeckPlaceholder>}
          {status === 'error' && (
            <div className="neu-inset flex h-full w-full flex-col items-center justify-center gap-3 rounded-[28px] p-6 text-center text-sm">
              <p className="font-medium text-nope">{error}</p>
              <p className="text-ink-soft">Confirme se a API está rodando em http://localhost:8000.</p>
              <button type="button" onClick={retry} className="neu-raised rounded-full px-4 py-1.5 text-ink">
                Tentar novamente
              </button>
            </div>
          )}
          {status === 'ready' && (
            <SwipeDeck
              queue={queue}
              forceExit={forceExit}
              onSwipe={swipe}
              onExitHandled={() => setForceExit(null)}
              onDragStateChange={setDragging}
            />
          )}
        </div>

        {showHint && (
          <motion.div
            className="flex items-center gap-3"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
          >
            <motion.span
              className="flex h-9 w-9 items-center justify-center rounded-full bg-nope text-lg font-bold text-white shadow-md"
              animate={{ x: [0, -6, 0] }}
              transition={{ duration: 1.1, repeat: Infinity, ease: 'easeInOut' }}
            >
              ←
            </motion.span>
            <motion.span
              className="text-sm font-semibold tracking-wide text-ink-soft"
              animate={{ opacity: [0.6, 1, 0.6] }}
              transition={{ duration: 1.4, repeat: Infinity, ease: 'easeInOut' }}
            >
              Deslize para avaliar
            </motion.span>
            <motion.span
              className="flex h-9 w-9 items-center justify-center rounded-full bg-like text-lg font-bold text-white shadow-md"
              animate={{ x: [0, 6, 0] }}
              transition={{ duration: 1.1, repeat: Infinity, ease: 'easeInOut' }}
            >
              →
            </motion.span>
          </motion.div>
        )}

        <div className="neu-raised flex w-full flex-col items-center gap-4 rounded-3xl p-4">
          <StatsBar summary={summary} />
          <ActionButtons disabled={!interactive} onDislike={() => trigger('left')} onLike={() => trigger('right')} />
        </div>
      </div>

      <footer className="absolute inset-x-0 bottom-2 text-center sm:bottom-4">
        <a
          href="https://luiloureiro.vercel.app/"
          target="_blank"
          rel="noopener noreferrer"
          className="text-[10px] tracking-wide text-ink-soft/40 transition hover:text-ink-soft"
        >
          Desenvolvido por Lui Loureiro
        </a>
      </footer>
    </main>
  )
}

export default App
