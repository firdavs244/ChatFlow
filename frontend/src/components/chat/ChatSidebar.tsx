'use client';

import { useState, useMemo } from 'react';
import { useRouter } from 'next/navigation';
import { motion, AnimatePresence } from 'framer-motion';
import {
  MessageCircle,
  Search,
  Settings,
  LogOut,
  Plus,
  Users,
  Bell,
  Moon,
  User,
  X,
  Camera,
} from 'lucide-react';
import { useChatStore } from '@/store/chatStore';
import { useAuthStore } from '@/store/authStore';
import { cn, formatChatTime, getInitials, getAvatarColor, truncateText } from '@/lib/utils';
import NewChatModal from './NewChatModal';
import toast from 'react-hot-toast';

export default function ChatSidebar() {
  const router = useRouter();
  const { chats, activeChatId, selectChat, totalUnread, chatsLoading } = useChatStore();
  const { user, logout, updateUser } = useAuthStore();
  
  const [searchQuery, setSearchQuery] = useState('');
  const [showNewChat, setShowNewChat] = useState(false);
  const [showMenu, setShowMenu] = useState(false);
  const [showProfile, setShowProfile] = useState(false);
  const [profileData, setProfileData] = useState({
    full_name: user?.full_name || '',
    bio: user?.bio || '',
    status_message: user?.status_message || '',
  });
  const [isSaving, setIsSaving] = useState(false);

  const filteredChats = useMemo(() => {
    if (!searchQuery.trim()) return chats;
    
    const query = searchQuery.toLowerCase();
    return chats.filter((chat) => {
      const name = chat.name || chat.other_user?.full_name || '';
      return name.toLowerCase().includes(query);
    });
  }, [chats, searchQuery]);

  const handleLogout = () => {
    logout();
    router.push('/login');
    toast.success('Chiqish muvaffaqiyatli');
  };

  const handleSaveProfile = async () => {
    setIsSaving(true);
    try {
      await updateUser(profileData);
      toast.success('Profil yangilandi');
      setShowProfile(false);
    } catch (error) {
      toast.error('Xatolik yuz berdi');
    } finally {
      setIsSaving(false);
    }
  };

  return (
    <>
      <aside className="w-80 lg:w-96 bg-dark-900 border-r border-dark-700 flex flex-col">
        {/* Header */}
        <div className="p-4 border-b border-dark-700">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <div className="w-10 h-10 bg-gradient-to-br from-primary-500 to-accent-500 rounded-xl flex items-center justify-center shadow-glow">
                <MessageCircle className="w-5 h-5 text-white" />
              </div>
              <div>
                <h1 className="font-bold text-white">ChatFlow</h1>
                {totalUnread > 0 && (
                  <span className="text-xs text-primary-400">{totalUnread} yangi xabar</span>
                )}
              </div>
            </div>
            
            <div className="flex items-center gap-1">
              <button
                onClick={() => setShowNewChat(true)}
                className="p-2 hover:bg-dark-700 rounded-lg text-dark-300 hover:text-white transition-colors"
                title="Yangi chat"
              >
                <Plus className="w-5 h-5" />
              </button>
              
              <div className="relative">
                <button
                  onClick={() => setShowMenu(!showMenu)}
                  className="p-2 hover:bg-dark-700 rounded-lg text-dark-300 hover:text-white transition-colors"
                >
                  <Settings className="w-5 h-5" />
                </button>
                
                <AnimatePresence>
                  {showMenu && (
                    <>
                      <div 
                        className="fixed inset-0 z-40" 
                        onClick={() => setShowMenu(false)}
                      />
                      <motion.div
                        initial={{ opacity: 0, scale: 0.95, y: -10 }}
                        animate={{ opacity: 1, scale: 1, y: 0 }}
                        exit={{ opacity: 0, scale: 0.95, y: -10 }}
                        className="absolute right-0 top-full mt-2 w-48 glass-dark rounded-xl py-2 z-50"
                      >
                        <div className="px-3 py-2 border-b border-dark-600">
                          <p className="font-medium text-white truncate">{user?.full_name}</p>
                          <p className="text-xs text-dark-400">@{user?.username}</p>
                        </div>
                        
                        <button 
                          onClick={() => {
                            setShowMenu(false);
                            setShowProfile(true);
                            setProfileData({
                              full_name: user?.full_name || '',
                              bio: user?.bio || '',
                              status_message: user?.status_message || '',
                            });
                          }}
                          className="w-full px-3 py-2 flex items-center gap-3 text-dark-300 hover:text-white hover:bg-dark-700 transition-colors"
                        >
                          <User className="w-4 h-4" />
                          <span className="text-sm">Profil</span>
                        </button>
                        
                        <button 
                          onClick={() => {
                            setShowMenu(false);
                            toast('Bildirishnomalar sozlamalari tez orada!', { icon: '🔔' });
                          }}
                          className="w-full px-3 py-2 flex items-center gap-3 text-dark-300 hover:text-white hover:bg-dark-700 transition-colors"
                        >
                          <Bell className="w-4 h-4" />
                          <span className="text-sm">Bildirishnomalar</span>
                        </button>
                        
                        <button 
                          onClick={() => {
                            setShowMenu(false);
                            toast('Qorong\'i rejim allaqachon yoqilgan!', { icon: '🌙' });
                          }}
                          className="w-full px-3 py-2 flex items-center gap-3 text-dark-300 hover:text-white hover:bg-dark-700 transition-colors"
                        >
                          <Moon className="w-4 h-4" />
                          <span className="text-sm">Qorong'i rejim</span>
                        </button>
                        
                        <div className="border-t border-dark-600 mt-1 pt-1">
                          <button
                            onClick={handleLogout}
                            className="w-full px-3 py-2 flex items-center gap-3 text-red-400 hover:text-red-300 hover:bg-red-500/10 transition-colors"
                          >
                            <LogOut className="w-4 h-4" />
                            <span className="text-sm">Chiqish</span>
                          </button>
                        </div>
                      </motion.div>
                    </>
                  )}
                </AnimatePresence>
              </div>
            </div>
          </div>

          {/* Search */}
          <div className="relative">
            <Search className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-dark-400" />
            <input
              type="text"
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
              placeholder="Chatlarni qidirish..."
              className="w-full pl-10 pr-4 py-2.5 bg-dark-800 border border-dark-600 rounded-xl text-white placeholder-dark-400 text-sm focus:outline-none focus:border-primary-500/50 transition-colors"
            />
          </div>
        </div>

        {/* Chat list */}
        <div className="flex-1 overflow-y-auto">
          {chatsLoading ? (
            <div className="p-4 space-y-3">
              {[1, 2, 3, 4, 5].map((i) => (
                <div key={i} className="flex items-center gap-3 animate-pulse">
                  <div className="w-12 h-12 bg-dark-700 rounded-full" />
                  <div className="flex-1">
                    <div className="h-4 bg-dark-700 rounded w-24 mb-2" />
                    <div className="h-3 bg-dark-700 rounded w-32" />
                  </div>
                </div>
              ))}
            </div>
          ) : filteredChats.length === 0 ? (
            <div className="flex flex-col items-center justify-center h-full text-dark-400 p-4">
              <Users className="w-12 h-12 mb-3 opacity-50" />
              <p className="text-center">
                {searchQuery ? 'Chat topilmadi' : 'Hozircha chatlar yo\'q'}
              </p>
              <button
                onClick={() => setShowNewChat(true)}
                className="mt-3 text-primary-400 hover:text-primary-300 text-sm font-medium"
              >
                Yangi chat boshlash
              </button>
            </div>
          ) : (
            <div className="py-2">
              {filteredChats.map((chat) => {
                const chatName = chat.name || chat.other_user?.full_name || 'Noma\'lum';
                const avatarUrl = chat.avatar_url || chat.other_user?.avatar_url;
                const isActive = activeChatId === chat.id;

                return (
                  <motion.button
                    key={chat.id}
                    onClick={() => selectChat(chat.id)}
                    className={cn(
                      'w-full px-4 py-3 flex items-center gap-3 transition-all duration-200 chat-item',
                      isActive && 'active'
                    )}
                    whileTap={{ scale: 0.98 }}
                  >
                    {/* Avatar */}
                    <div className="relative flex-shrink-0">
                      {avatarUrl ? (
                        <img
                          src={avatarUrl}
                          alt={chatName}
                          className="w-12 h-12 rounded-full object-cover"
                        />
                      ) : (
                        <div
                          className={cn(
                            'w-12 h-12 rounded-full flex items-center justify-center text-white font-medium',
                            getAvatarColor(chatName)
                          )}
                        >
                          {chat.chat_type === 'group' ? (
                            <Users className="w-5 h-5" />
                          ) : (
                            getInitials(chatName)
                          )}
                        </div>
                      )}
                      
                      {/* Online indicator */}
                      {chat.chat_type === 'private' && chat.is_online && (
                        <span className="absolute bottom-0 right-0 w-3.5 h-3.5 bg-green-500 rounded-full border-2 border-dark-900 online-pulse" />
                      )}
                    </div>

                    {/* Content */}
                    <div className="flex-1 min-w-0 text-left">
                      <div className="flex items-center justify-between mb-0.5">
                        <span className="font-medium text-white truncate">
                          {chatName}
                        </span>
                        {chat.last_message_at && (
                          <span className="text-xs text-dark-400 flex-shrink-0 ml-2">
                            {formatChatTime(chat.last_message_at)}
                          </span>
                        )}
                      </div>
                      
                      <div className="flex items-center justify-between">
                        <span className="text-sm text-dark-400 truncate">
                          {chat.last_message
                            ? truncateText(
                                chat.last_message.message_type === 'text'
                                  ? chat.last_message.content || ''
                                  : `📎 ${chat.last_message.message_type}`,
                                30
                              )
                            : 'Xabarlar yo\'q'}
                        </span>
                        
                        {chat.unread_count > 0 && (
                          <span className="flex-shrink-0 ml-2 min-w-[20px] h-5 px-1.5 bg-primary-500 text-white text-xs font-medium rounded-full flex items-center justify-center">
                            {chat.unread_count > 99 ? '99+' : chat.unread_count}
                          </span>
                        )}
                      </div>
                    </div>
                  </motion.button>
                );
              })}
            </div>
          )}
        </div>
      </aside>

      {/* New chat modal */}
      <NewChatModal isOpen={showNewChat} onClose={() => setShowNewChat(false)} />

      {/* Profile modal */}
      <AnimatePresence>
        {showProfile && (
          <>
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              exit={{ opacity: 0 }}
              onClick={() => setShowProfile(false)}
              className="fixed inset-0 bg-black/60 backdrop-blur-sm z-50"
            />
            <motion.div
              initial={{ opacity: 0, scale: 0.95, y: 20 }}
              animate={{ opacity: 1, scale: 1, y: 0 }}
              exit={{ opacity: 0, scale: 0.95, y: 20 }}
              className="fixed left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2 w-full max-w-md glass rounded-2xl overflow-hidden z-50"
            >
              <div className="px-4 py-3 border-b border-dark-600 flex items-center justify-between">
                <h2 className="text-lg font-semibold text-white">Profil</h2>
                <button
                  onClick={() => setShowProfile(false)}
                  className="p-1.5 hover:bg-dark-600 rounded-lg text-dark-300 hover:text-white transition-colors"
                >
                  <X className="w-5 h-5" />
                </button>
              </div>

              <div className="p-4 space-y-4">
                {/* Avatar */}
                <div className="flex justify-center">
                  <div className="relative">
                    {user?.avatar_url ? (
                      <img
                        src={user.avatar_url}
                        alt={user.full_name}
                        className="w-24 h-24 rounded-full object-cover"
                      />
                    ) : (
                      <div className={cn(
                        'w-24 h-24 rounded-full flex items-center justify-center text-white text-2xl font-medium',
                        getAvatarColor(user?.full_name || '')
                      )}>
                        {getInitials(user?.full_name || '')}
                      </div>
                    )}
                    <button className="absolute bottom-0 right-0 p-2 bg-primary-500 rounded-full text-white hover:bg-primary-600 transition-colors">
                      <Camera className="w-4 h-4" />
                    </button>
                  </div>
                </div>

                {/* Username (readonly) */}
                <div>
                  <label className="block text-sm font-medium text-dark-300 mb-1">Username</label>
                  <input
                    type="text"
                    value={`@${user?.username || ''}`}
                    disabled
                    className="w-full px-4 py-2.5 bg-dark-800 border border-dark-600 rounded-xl text-dark-400 cursor-not-allowed"
                  />
                </div>

                {/* Full name */}
                <div>
                  <label className="block text-sm font-medium text-dark-300 mb-1">To'liq ism</label>
                  <input
                    type="text"
                    value={profileData.full_name}
                    onChange={(e) => setProfileData({ ...profileData, full_name: e.target.value })}
                    className="w-full px-4 py-2.5 bg-dark-700 border border-dark-600 rounded-xl text-white focus:outline-none focus:border-primary-500/50"
                  />
                </div>

                {/* Bio */}
                <div>
                  <label className="block text-sm font-medium text-dark-300 mb-1">Bio</label>
                  <textarea
                    value={profileData.bio}
                    onChange={(e) => setProfileData({ ...profileData, bio: e.target.value })}
                    rows={3}
                    className="w-full px-4 py-2.5 bg-dark-700 border border-dark-600 rounded-xl text-white focus:outline-none focus:border-primary-500/50 resize-none"
                    placeholder="O'zingiz haqingizda..."
                  />
                </div>

                {/* Status message */}
                <div>
                  <label className="block text-sm font-medium text-dark-300 mb-1">Status</label>
                  <input
                    type="text"
                    value={profileData.status_message}
                    onChange={(e) => setProfileData({ ...profileData, status_message: e.target.value })}
                    className="w-full px-4 py-2.5 bg-dark-700 border border-dark-600 rounded-xl text-white focus:outline-none focus:border-primary-500/50"
                    placeholder="Hozirgi holatingiz..."
                  />
                </div>

                {/* Save button */}
                <button
                  onClick={handleSaveProfile}
                  disabled={isSaving}
                  className="w-full py-3 bg-primary-500 hover:bg-primary-600 disabled:bg-dark-600 text-white font-medium rounded-xl transition-colors flex items-center justify-center gap-2"
                >
                  {isSaving ? (
                    <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
                  ) : (
                    'Saqlash'
                  )}
                </button>
              </div>
            </motion.div>
          </>
        )}
      </AnimatePresence>
    </>
  );
}
