'use client';

import { motion } from 'framer-motion';
import { MessageCircle, Users, Shield, Zap } from 'lucide-react';

export default function EmptyChat() {
  const features = [
    {
      icon: MessageCircle,
      title: 'Real-time xabarlar',
      description: 'Tezkor va ishonchli xabar almashish',
    },
    {
      icon: Users,
      title: 'Guruhli chatlar',
      description: 'Jamoa bilan samarali muloqot',
    },
    {
      icon: Shield,
      title: 'Xavfsiz',
      description: 'End-to-end shifrlangan aloqa',
    },
    {
      icon: Zap,
      title: 'Tezkor',
      description: 'WebSocket orqali real-time yangilanishlar',
    },
  ];

  return (
    <div className="flex-1 flex flex-col items-center justify-center p-8 aurora-bg">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        className="text-center max-w-md"
      >
        {/* Logo */}
        <motion.div
          animate={{ y: [0, -10, 0] }}
          transition={{ duration: 3, repeat: Infinity, ease: 'easeInOut' }}
          className="w-24 h-24 mx-auto mb-6 bg-gradient-to-br from-primary-500 to-accent-500 rounded-3xl flex items-center justify-center shadow-glow"
        >
          <MessageCircle className="w-12 h-12 text-white" />
        </motion.div>

        <h2 className="text-2xl font-bold text-white mb-2">
          ChatFlow ga xush kelibsiz!
        </h2>
        <p className="text-dark-400 mb-8">
          Chatni tanlang yoki yangi suhbat boshlang
        </p>

        {/* Features grid */}
        <div className="grid grid-cols-2 gap-4">
          {features.map((feature, index) => (
            <motion.div
              key={feature.title}
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ delay: 0.1 * index }}
              className="glass p-4 rounded-xl text-left"
            >
              <feature.icon className="w-8 h-8 text-primary-400 mb-2" />
              <h3 className="font-medium text-white mb-1">{feature.title}</h3>
              <p className="text-xs text-dark-400">{feature.description}</p>
            </motion.div>
          ))}
        </div>

        {/* Keyboard shortcut hint */}
        <div className="mt-8 text-sm text-dark-500">
          <kbd className="px-2 py-1 bg-dark-800 rounded text-dark-400 font-mono text-xs">
            Ctrl
          </kbd>
          {' + '}
          <kbd className="px-2 py-1 bg-dark-800 rounded text-dark-400 font-mono text-xs">
            N
          </kbd>
          {' yangi chat yaratish'}
        </div>
      </motion.div>
    </div>
  );
}

