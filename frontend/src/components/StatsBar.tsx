import type { Summary } from '../api/client'

interface StatsBarProps {
  summary: Summary | null
}

function Stat({ label, value, align = 'left' }: { label: string; value: string; align?: 'left' | 'center' | 'right' }) {
  const alignClass = align === 'left' ? 'items-start' : align === 'right' ? 'items-end' : 'items-center'
  return (
    <span className={`flex flex-col gap-0.5 ${alignClass}`}>
      <span className="text-[10px] font-semibold uppercase tracking-wider text-ink-soft/70">{label}</span>
      <span className="truncate text-sm font-semibold text-ink">{value}</span>
    </span>
  )
}

export function StatsBar({ summary }: StatsBarProps) {
  if (!summary) return null
  const [topGenre] = summary.best_genome.top_genres

  return (
    <div className="neu-inset flex w-full max-w-sm items-center justify-between gap-2 rounded-2xl px-4 py-3">
      <Stat label="Geração" value={String(summary.generation)} />
      <Stat label="Avaliações" value={String(summary.total_feedback)} align="center" />
      {topGenre && <Stat label="Favorito" value={topGenre[0]} align="right" />}
    </div>
  )
}
