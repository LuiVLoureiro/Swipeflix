interface ActionButtonsProps {
  disabled: boolean
  onLike: () => void
  onDislike: () => void
}

export function ActionButtons({ disabled, onLike, onDislike }: ActionButtonsProps) {
  return (
    <div className="flex items-center justify-center gap-8">
      <button
        type="button"
        disabled={disabled}
        onClick={onDislike}
        aria-label="Não gostei"
        className="neu-raised flex h-14 w-14 items-center justify-center rounded-full text-2xl leading-none text-nope transition active:scale-90 disabled:opacity-40"
      >
        ✕
      </button>
      <button
        type="button"
        disabled={disabled}
        onClick={onLike}
        aria-label="Gostei"
        className="neu-raised flex h-14 w-14 items-center justify-center rounded-full text-2xl leading-none text-like transition active:scale-90 disabled:opacity-40"
      >
        ♥
      </button>
    </div>
  )
}
