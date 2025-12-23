'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import Link from 'next/link';
import { motion } from 'framer-motion';
import { MessageCircle, Mail, Lock, User, AtSign, ArrowRight, Eye, EyeOff, Check } from 'lucide-react';
import { useAuthStore } from '@/store/authStore';
import toast from 'react-hot-toast';

export default function RegisterPage() {
  const router = useRouter();
  const { register, isLoading, error, clearError } = useAuthStore();
  
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    fullName: '',
    password: '',
    confirmPassword: '',
  });
  const [showPassword, setShowPassword] = useState(false);

  const passwordRequirements = [
    { label: 'Kamida 8 ta belgi', met: formData.password.length >= 8 },
    { label: 'Katta harf', met: /[A-Z]/.test(formData.password) },
    { label: 'Kichik harf', met: /[a-z]/.test(formData.password) },
    { label: 'Raqam', met: /\d/.test(formData.password) },
  ];

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    clearError();

    if (formData.password !== formData.confirmPassword) {
      toast.error('Parollar mos kelmaydi');
      return;
    }

    if (!passwordRequirements.every((r) => r.met)) {
      toast.error('Parol talablarini bajaring');
      return;
    }

    try {
      await register(formData.email, formData.username, formData.fullName, formData.password);
      toast.success('Muvaffaqiyatli ro\'yxatdan o\'tdingiz!');
      router.push('/chat');
    } catch (err) {
      toast.error('Ro\'yxatdan o\'tishda xatolik');
    }
  };

  return (
    <main className="min-h-screen aurora-bg flex items-center justify-center p-4">
      <motion.div
        initial={{ opacity: 0, y: 20 }}
        animate={{ opacity: 1, y: 0 }}
        transition={{ duration: 0.5 }}
        className="w-full max-w-md"
      >
        {/* Logo */}
        <div className="text-center mb-8">
          <motion.div
            initial={{ scale: 0 }}
            animate={{ scale: 1 }}
            transition={{ type: 'spring', duration: 0.6 }}
            className="w-16 h-16 mx-auto bg-gradient-to-br from-primary-500 to-accent-500 rounded-2xl flex items-center justify-center shadow-glow mb-4"
          >
            <MessageCircle className="w-8 h-8 text-white" />
          </motion.div>
          <h1 className="text-2xl font-bold text-white">ChatFlow</h1>
          <p className="text-dark-400 mt-1">Yangi hisob yarating</p>
        </div>

        {/* Form */}
        <motion.form
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.2 }}
          onSubmit={handleSubmit}
          className="glass rounded-2xl p-6 space-y-4"
        >
          {/* Full Name */}
          <div>
            <label className="block text-sm font-medium text-dark-300 mb-2">
              To'liq ism
            </label>
            <div className="relative">
              <User className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-dark-400" />
              <input
                type="text"
                value={formData.fullName}
                onChange={(e) => setFormData({ ...formData, fullName: e.target.value })}
                placeholder="Ism Familiya"
                required
                className="w-full pl-11 pr-4 py-3 bg-dark-800/50 border border-dark-600 rounded-xl text-white placeholder-dark-400 focus:outline-none focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 transition-all"
              />
            </div>
          </div>

          {/* Username */}
          <div>
            <label className="block text-sm font-medium text-dark-300 mb-2">
              Username
            </label>
            <div className="relative">
              <AtSign className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-dark-400" />
              <input
                type="text"
                value={formData.username}
                onChange={(e) => setFormData({ ...formData, username: e.target.value.toLowerCase() })}
                placeholder="username"
                required
                pattern="[a-z0-9_.]+"
                className="w-full pl-11 pr-4 py-3 bg-dark-800/50 border border-dark-600 rounded-xl text-white placeholder-dark-400 focus:outline-none focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 transition-all"
              />
            </div>
          </div>

          {/* Email */}
          <div>
            <label className="block text-sm font-medium text-dark-300 mb-2">
              Email
            </label>
            <div className="relative">
              <Mail className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-dark-400" />
              <input
                type="email"
                value={formData.email}
                onChange={(e) => setFormData({ ...formData, email: e.target.value })}
                placeholder="email@example.com"
                required
                className="w-full pl-11 pr-4 py-3 bg-dark-800/50 border border-dark-600 rounded-xl text-white placeholder-dark-400 focus:outline-none focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 transition-all"
              />
            </div>
          </div>

          {/* Password */}
          <div>
            <label className="block text-sm font-medium text-dark-300 mb-2">
              Parol
            </label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-dark-400" />
              <input
                type={showPassword ? 'text' : 'password'}
                value={formData.password}
                onChange={(e) => setFormData({ ...formData, password: e.target.value })}
                placeholder="••••••••"
                required
                className="w-full pl-11 pr-12 py-3 bg-dark-800/50 border border-dark-600 rounded-xl text-white placeholder-dark-400 focus:outline-none focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 transition-all"
              />
              <button
                type="button"
                onClick={() => setShowPassword(!showPassword)}
                className="absolute right-3 top-1/2 -translate-y-1/2 text-dark-400 hover:text-white transition-colors"
              >
                {showPassword ? <EyeOff className="w-5 h-5" /> : <Eye className="w-5 h-5" />}
              </button>
            </div>
            
            {/* Password requirements */}
            {formData.password && (
              <div className="mt-2 grid grid-cols-2 gap-1">
                {passwordRequirements.map((req, i) => (
                  <div
                    key={i}
                    className={`flex items-center gap-1 text-xs ${
                      req.met ? 'text-green-400' : 'text-dark-400'
                    }`}
                  >
                    <Check className={`w-3 h-3 ${req.met ? 'opacity-100' : 'opacity-30'}`} />
                    {req.label}
                  </div>
                ))}
              </div>
            )}
          </div>

          {/* Confirm Password */}
          <div>
            <label className="block text-sm font-medium text-dark-300 mb-2">
              Parolni tasdiqlang
            </label>
            <div className="relative">
              <Lock className="absolute left-3 top-1/2 -translate-y-1/2 w-5 h-5 text-dark-400" />
              <input
                type={showPassword ? 'text' : 'password'}
                value={formData.confirmPassword}
                onChange={(e) => setFormData({ ...formData, confirmPassword: e.target.value })}
                placeholder="••••••••"
                required
                className="w-full pl-11 pr-4 py-3 bg-dark-800/50 border border-dark-600 rounded-xl text-white placeholder-dark-400 focus:outline-none focus:border-primary-500 focus:ring-2 focus:ring-primary-500/20 transition-all"
              />
            </div>
            {formData.confirmPassword && formData.password !== formData.confirmPassword && (
              <p className="mt-1 text-xs text-red-400">Parollar mos kelmaydi</p>
            )}
          </div>

          {/* Error */}
          {error && (
            <motion.div
              initial={{ opacity: 0, y: -10 }}
              animate={{ opacity: 1, y: 0 }}
              className="p-3 bg-red-500/10 border border-red-500/20 rounded-lg text-red-400 text-sm"
            >
              {error}
            </motion.div>
          )}

          {/* Submit */}
          <button
            type="submit"
            disabled={isLoading}
            className="w-full py-3 bg-gradient-to-r from-primary-500 to-primary-600 hover:from-primary-600 hover:to-primary-700 text-white font-medium rounded-xl flex items-center justify-center gap-2 transition-all duration-200 disabled:opacity-50 disabled:cursor-not-allowed shadow-lg hover:shadow-glow"
          >
            {isLoading ? (
              <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            ) : (
              <>
                Ro'yxatdan o'tish
                <ArrowRight className="w-5 h-5" />
              </>
            )}
          </button>

          {/* Login link */}
          <p className="text-center text-dark-400">
            Hisobingiz bormi?{' '}
            <Link href="/login" className="text-primary-400 hover:text-primary-300 font-medium transition-colors">
              Kirish
            </Link>
          </p>
        </motion.form>
      </motion.div>
    </main>
  );
}

