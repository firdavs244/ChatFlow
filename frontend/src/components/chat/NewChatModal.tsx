'use client';

import { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { X, Search, User, Users, Check } from 'lucide-react';
import { api } from '@/lib/api';
import { useChatStore } from '@/store/chatStore';
import { UserProfile } from '@/types';
import { cn, getInitials, getAvatarColor } from '@/lib/utils';
import toast from 'react-hot-toast';

interface NewChatModalProps {
  isOpen: boolean;
  onClose: () => void;
}

export default function NewChatModal({ isOpen, onClose }: NewChatModalProps) {
  const { selectChat, loadChats } = useChatStore();
  
  const [searchQuery, setSearchQuery] = useState('');
  const [searchResults, setSearchResults] = useState<UserProfile[]>([]);
  const [selectedUsers, setSelectedUsers] = useState<UserProfile[]>([]);
  const [isSearching, setIsSearching] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  const [mode, setMode] = useState<'private' | 'group'>('private');
  const [groupName, setGroupName] = useState('');

  const handleSearch = async (query: string) => {
    setSearchQuery(query);
    
    if (query.length < 2) {
      setSearchResults([]);
      return;
    }

    setIsSearching(true);
    try {
      const results = await api.searchUsers(query);
      setSearchResults(results);
    } catch (error) {
      console.error('Search error:', error);
    } finally {
      setIsSearching(false);
    }
  };

  const toggleUserSelection = (user: UserProfile) => {
    setSelectedUsers((prev) => {
      const isSelected = prev.some((u) => u.id === user.id);
      if (isSelected) {
        return prev.filter((u) => u.id !== user.id);
      }
      
      if (mode === 'private' && prev.length >= 1) {
        return [user]; // Replace for private chat
      }
      
      return [...prev, user];
    });
  };

  const handleCreate = async () => {
    if (selectedUsers.length === 0) return;

    setIsCreating(true);
    try {
      let chat;
      
      if (mode === 'private') {
        chat = await api.createPrivateChat(selectedUsers[0].id);
      } else {
        if (!groupName.trim()) {
          toast.error('Guruh nomini kiriting');
          return;
        }
        chat = await api.createGroupChat(groupName, selectedUsers.map((u) => u.id));
      }

      await loadChats();
      selectChat(chat.id);
      toast.success(mode === 'private' ? 'Chat yaratildi' : 'Guruh yaratildi');
      handleClose();
    } catch (error) {
      toast.error('Xatolik yuz berdi');
    } finally {
      setIsCreating(false);
    }
  };

  const handleClose = () => {
    setSearchQuery('');
    setSearchResults([]);
    setSelectedUsers([]);
    setGroupName('');
    setMode('private');
    onClose();
  };

  return (
    <AnimatePresence>
      {isOpen && (
        <>
          {/* Backdrop */}
          <motion.div
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            onClick={handleClose}
            className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50"
          />

          {/* Modal */}
          <motion.div
            initial={{ opacity: 0, scale: 0.95, y: 20 }}
            animate={{ opacity: 1, scale: 1, y: 0 }}
            exit={{ opacity: 0, scale: 0.95, y: 20 }}
            className="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-md glass rounded-2xl overflow-hidden z-50"
          >
            {/* Header */}
            <div className="px-4 py-3 border-b border-dark-600 flex items-center justify-between">
              <h2 className="text-lg font-semibold text-white">Yangi chat</h2>
              <button
                onClick={handleClose}
                className="p-1.5 hover:bg-dark-600 rounded-lg text-dark-300 hover:text-white transition-colors"
              >
                <X className="w-5 h-5" />
              </button>
            </div>

            {/* Mode selector */}
            <div className="p-4 border-b border-dark-600">
              <div className="flex gap-2">
                <button
                  onClick={() => {
                    setMode('private');
                    setSelectedUsers(selectedUsers.slice(0, 1));
                  }}
                  className={cn(
                    'flex-1 py-2 px-4 rounded-xl flex items-center justify-center gap-2 transition-colors',
                    mode === 'private'
                      ? 'bg-primary-500 text-white'
                      : 'bg-dark-700 text-dark-300 hover:bg-dark-600'
                  )}
                >
                  <User className="w-4 h-4" />
                  <span>Shaxsiy</span>
                </button>
                <button
                  onClick={() => setMode('group')}
                  className={cn(
                    'flex-1 py-2 px-4 rounded-xl flex items-center justify-center gap-2 transition-colors',
                    mode === 'group'
                      ? 'bg-primary-500 text-white'
                      : 'bg-dark-700 text-dark-300 hover:bg-dark-600'
                  )}
                >
                  <Users className="w-4 h-4" />
                  <span>Guruh</span>
                </button>
              </div>

              {/* Group name input */}
              {mode === 'group' && (
                <input
                  type="text"
                  value={groupName}
                  onChange={(e) => setGroupName(e.target.value)}
                  placeholder="Guruh nomi..."
                  className="w-full mt-3 px-4 py-2.5 bg-dark-700 border border-dark-600 rounded-xl text-white placeholder-dark-400 focus:outline-none focus:border-primary-500/50 transition-colors"
                />
              )}
            </div>

            {/* Search */}
            <div className="p-4 border-b border-dark-600">
              <div className="relative">
                <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-dark-400" />
                <input
                  type="text"
                  value={searchQuery}
                  onChange={(e) => handleSearch(e.target.value)}
                  placeholder="Foydalanuvchini qidiring..."
                  className="w-full pl-10 pr-4 py-2.5 bg-dark-700 border border-dark-600 rounded-xl text-white placeholder-dark-400 focus:outline-none focus:border-primary-500/50 transition-colors"
                  autoFocus
                />
              </div>

              {/* Selected users */}
              {selectedUsers.length > 0 && (
                <div className="flex flex-wrap gap-2 mt-3">
                  {selectedUsers.map((user) => (
                    <button
                      key={user.id}
                      onClick={() => toggleUserSelection(user)}
                      className="flex items-center gap-1.5 px-2 py-1 bg-primary-500/20 border border-primary-500/30 rounded-full text-sm text-primary-300"
                    >
                      <span>{user.full_name}</span>
                      <X className="w-3.5 h-3.5" />
                    </button>
                  ))}
                </div>
              )}
            </div>

            {/* Results */}
            <div className="max-h-64 overflow-y-auto">
              {isSearching ? (
                <div className="p-8 text-center text-dark-400">
                  <div className="w-6 h-6 border-2 border-primary-500/30 border-t-primary-500 rounded-full animate-spin mx-auto" />
                </div>
              ) : searchResults.length === 0 ? (
                <div className="p-8 text-center text-dark-400">
                  {searchQuery.length >= 2
                    ? 'Foydalanuvchi topilmadi'
                    : 'Qidirish uchun kamida 2 ta belgi kiriting'}
                </div>
              ) : (
                <div className="py-2">
                  {searchResults.map((user) => {
                    const isSelected = selectedUsers.some((u) => u.id === user.id);

                    return (
                      <button
                        key={user.id}
                        onClick={() => toggleUserSelection(user)}
                        className={cn(
                          'w-full px-4 py-3 flex items-center gap-3 hover:bg-dark-700 transition-colors',
                          isSelected && 'bg-primary-500/10'
                        )}
                      >
                        {user.avatar_url ? (
                          <img
                            src={user.avatar_url}
                            alt={user.full_name}
                            className="w-10 h-10 rounded-full object-cover"
                          />
                        ) : (
                          <div
                            className={cn(
                              'w-10 h-10 rounded-full flex items-center justify-center text-white font-medium',
                              getAvatarColor(user.full_name)
                            )}
                          >
                            {getInitials(user.full_name)}
                          </div>
                        )}
                        
                        <div className="flex-1 text-left">
                          <p className="font-medium text-white">{user.full_name}</p>
                          <p className="text-sm text-dark-400">@{user.username}</p>
                        </div>

                        <div
                          className={cn(
                            'w-5 h-5 rounded-full border-2 flex items-center justify-center transition-colors',
                            isSelected
                              ? 'bg-primary-500 border-primary-500'
                              : 'border-dark-500'
                          )}
                        >
                          {isSelected && <Check className="w-3 h-3 text-white" />}
                        </div>
                      </button>
                    );
                  })}
                </div>
              )}
            </div>

            {/* Footer */}
            <div className="p-4 border-t border-dark-600">
              <button
                onClick={handleCreate}
                disabled={
                  selectedUsers.length === 0 ||
                  isCreating ||
                  (mode === 'group' && !groupName.trim())
                }
                className="w-full py-3 bg-primary-500 hover:bg-primary-600 disabled:bg-dark-600 disabled:text-dark-400 text-white font-medium rounded-xl transition-colors flex items-center justify-center gap-2"
              >
                {isCreating ? (
                  <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                ) : (
                  <>
                    {mode === 'private' ? 'Chat boshlash' : 'Guruh yaratish'}
                  </>
                )}
              </button>
            </div>
          </motion.div>
        </>
      )}
    </AnimatePresence>
  );
}

