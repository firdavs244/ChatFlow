'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/authStore';
import { motion } from 'framer-motion';
import { MessageCircle } from 'lucide-react';

export default function Home() {
  const router = useRouter();
  const { isAuthenticated, isLoading, checkAuth } = useAuthStore();

  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  useEffect(() => {
    if (!isLoading) {
      if (isAuthenticated) {
        router.push('/chat');
      } else {
        router.push('/login');
      }
    }
  }, [isAuthenticated, isLoading, router]);

  return (
    <main className="min-h-screen aurora-bg flex items-center justify-center">
      <motion.div
        initial={{ opacity: 0, scale: 0.9 }}
        animate={{ opacity: 1, scale: 1 }}
        transition={{ duration: 0.5 }}
        className="text-center"
      >
        <motion.div
          animate={{ y: [0, -10, 0] }}
          transition={{ duration: 2, repeat: Infinity, ease: 'easeInOut' }}
          className="mb-6"
        >
          <div className="w-20 h-20 mx-auto bg-gradient-to-br from-primary-500 to-accent-500 rounded-2xl flex items-center justify-center shadow-glow">
            <MessageCircle className="w-10 h-10 text-white" />
          </div>
        </motion.div>
        
        <h1 className="text-3xl font-bold text-white mb-2">ChatFlow</h1>
        <p className="text-dark-400">Yuklanmoqda...</p>
        
        <div className="mt-8 flex justify-center gap-1">
          {[0, 1, 2].map((i) => (
            <motion.div
              key={i}
              animate={{ opacity: [0.3, 1, 0.3] }}
              transition={{ duration: 1.5, repeat: Infinity, delay: i * 0.2 }}
              className="w-2 h-2 bg-primary-500 rounded-full"
            />
          ))}
        </div>
      </motion.div>
    </main>
  );
}

