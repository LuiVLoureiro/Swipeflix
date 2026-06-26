import { motion } from 'framer-motion'

interface LoadingCardProps {
  label: string
}

export function LoadingCard({ label }: LoadingCardProps) {
  return (
    <div className="neu-inset flex h-full w-full flex-col items-center justify-center gap-4 rounded-[28px] p-6 text-center">
      <div className="relative flex h-14 w-14 items-center justify-center">
        <motion.span
          className="absolute inset-0 rounded-full border-4 border-accent/20 border-t-accent"
          animate={{ rotate: 360 }}
          transition={{ duration: 1, repeat: Infinity, ease: 'linear' }}
        />
        <motion.span
          className="h-2.5 w-2.5 rounded-full bg-accent"
          animate={{ scale: [1, 0.6, 1] }}
          transition={{ duration: 1.2, repeat: Infinity, ease: 'easeInOut' }}
        />
      </div>
      <motion.p
        className="text-sm text-ink-soft"
        animate={{ opacity: [0.5, 1, 0.5] }}
        transition={{ duration: 1.6, repeat: Infinity, ease: 'easeInOut' }}
      >
        {label}
      </motion.p>
    </div>
  )
}
