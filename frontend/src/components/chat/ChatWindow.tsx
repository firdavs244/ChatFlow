'use client';

import { useState, useRef, useEffect, useCallback } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import {
  Send,
  Paperclip,
  Smile,
  Phone,
  Video,
  MoreVertical,
  ArrowLeft,
  Image as ImageIcon,
  Mic,
  X,
  UserPlus,
  Settings,
  Trash2,
  LogOut,
  Pin,
  Search,
} from 'lucide-react';
import EmojiPicker from 'emoji-picker-react';
import { useChatStore } from '@/store/chatStore';
import { useAuthStore } from '@/store/authStore';
import { api } from '@/lib/api';
import { wsClient } from '@/lib/websocket';
import { cn, formatLastSeen, getInitials, getAvatarColor, debounce } from '@/lib/utils';
import MessageBubble from './MessageBubble';
import toast from 'react-hot-toast';

export default function ChatWindow() {
  const { activeChat, activeChatId, messages, sendMessage, loadMessages, hasMoreMessages, messagesLoading, typingUsers, clearActiveChat, loadChats } = useChatStore();
  const { user } = useAuthStore();
  
  const [messageText, setMessageText] = useState('');
  const [showEmoji, setShowEmoji] = useState(false);
  const [isSending, setIsSending] = useState(false);
  const [showChatMenu, setShowChatMenu] = useState(false);
  const [isUploading, setIsUploading] = useState(false);
  
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const messagesContainerRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  const chatMessages = activeChatId ? messages.get(activeChatId) || [] : [];
  const typingList = activeChatId ? Array.from(typingUsers.get(activeChatId) || []) : [];

  // Get chat display info
  const chatName = activeChat?.name || 
    (activeChat?.chat_type === 'private' && activeChat?.members.find(m => m.user_id !== user?.id)?.user?.full_name) || 
    'Chat';
  const chatAvatar = activeChat?.avatar_url ||
    (activeChat?.chat_type === 'private' && activeChat?.members.find(m => m.user_id !== user?.id)?.user?.avatar_url);
  const otherUser = activeChat?.chat_type === 'private' 
    ? activeChat?.members.find(m => m.user_id !== user?.id)?.user 
    : null;

  // Scroll to bottom on new messages
  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: 'smooth' });
  }, [chatMessages.length]);

  // Typing indicator debounce
  const sendTypingStop = useCallback(
    debounce(() => {
      if (activeChatId) {
        wsClient.sendTypingStop(activeChatId);
      }
    }, 2000),
    [activeChatId]
  );

  const handleInputChange = (e: React.ChangeEvent<HTMLTextAreaElement>) => {
    setMessageText(e.target.value);
    
    // Send typing indicator
    if (activeChatId && e.target.value.length > 0) {
      wsClient.sendTypingStart(activeChatId);
      sendTypingStop();
    }
  };

  const handleSend = async () => {
    if (!messageText.trim() || isSending) return;
    
    const text = messageText;
    setMessageText('');
    setIsSending(true);
    
    try {
      await sendMessage(text);
    } catch (error) {
      setMessageText(text); // Restore on error
      toast.error('Xabar yuborilmadi');
    } finally {
      setIsSending(false);
      inputRef.current?.focus();
    }
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === 'Enter' && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  const handleEmojiSelect = (emojiData: any) => {
    setMessageText((prev) => prev + emojiData.emoji);
    inputRef.current?.focus();
  };

  const handleLoadMore = async () => {
    if (activeChatId && hasMoreMessages && !messagesLoading) {
      await loadMessages(activeChatId, true);
    }
  };

  const handlePhoneCall = () => {
    toast('Audio qo\'ng\'iroq tez orada qo\'shiladi!', { icon: '📞' });
  };

  const handleVideoCall = () => {
    toast('Video qo\'ng\'iroq tez orada qo\'shiladi!', { icon: '📹' });
  };

  const handleFileSelect = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    // Check file size (50MB max)
    if (file.size > 50 * 1024 * 1024) {
      toast.error('Fayl hajmi 50MB dan oshmasligi kerak');
      return;
    }

    setIsUploading(true);
    try {
      const result = await api.uploadFile(file);
      // Send message with attachment info
      toast.success('Fayl yuklandi!');
      // For now, just send the file URL as message
      await sendMessage(`📎 ${result.file_name}: ${result.file_url}`);
    } catch (error) {
      toast.error('Fayl yuklanmadi');
    } finally {
      setIsUploading(false);
      if (fileInputRef.current) {
        fileInputRef.current.value = '';
      }
    }
  };

  const handleLeaveChat = async () => {
    if (!activeChatId || !user) return;
    
    try {
      await api.removeMember(activeChatId, user.id);
      await loadChats();
      clearActiveChat();
      toast.success('Chatdan chiqdingiz');
    } catch (error) {
      toast.error('Xatolik yuz berdi');
    }
  };

  const handleDeleteChat = async () => {
    if (!activeChatId) return;
    
    if (!confirm('Chatni o\'chirishni xohlaysizmi?')) return;
    
    try {
      await api.deleteChat(activeChatId);
      await loadChats();
      clearActiveChat();
      toast.success('Chat o\'chirildi');
    } catch (error) {
      toast.error('Xatolik yuz berdi');
    }
  };

  return (
    <div className="flex-1 flex flex-col h-full bg-dark-950">
      {/* Header */}
      <header className="px-4 py-3 bg-dark-900 border-b border-dark-700 flex items-center justify-between">
        <div className="flex items-center gap-3">
          <button
            onClick={clearActiveChat}
            className="lg:hidden p-2 -ml-2 hover:bg-dark-700 rounded-lg text-dark-300"
          >
            <ArrowLeft className="w-5 h-5" />
          </button>
          
          {/* Avatar */}
          <div className="relative">
            {chatAvatar ? (
              <img
                src={chatAvatar}
                alt={chatName}
                className="w-10 h-10 rounded-full object-cover"
              />
            ) : (
              <div
                className={cn(
                  'w-10 h-10 rounded-full flex items-center justify-center text-white font-medium',
                  getAvatarColor(chatName)
                )}
              >
                {getInitials(chatName)}
              </div>
            )}
            {otherUser?.status === 'online' && (
              <span className="absolute bottom-0 right-0 w-3 h-3 bg-green-500 rounded-full border-2 border-dark-900" />
            )}
          </div>
          
          <div>
            <h2 className="font-semibold text-white">{chatName}</h2>
            <p className="text-xs text-dark-400">
              {typingList.length > 0 ? (
                <span className="text-primary-400">
                  {typingList.join(', ')} yozmoqda...
                </span>
              ) : otherUser ? (
                otherUser.status === 'online' ? 'Online' : formatLastSeen(otherUser.last_seen)
              ) : (
                `${activeChat?.member_count || 0} ta a'zo`
              )}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-1">
          <button 
            onClick={handlePhoneCall}
            className="p-2 hover:bg-dark-700 rounded-lg text-dark-300 hover:text-white transition-colors"
            title="Audio qo'ng'iroq"
          >
            <Phone className="w-5 h-5" />
          </button>
          <button 
            onClick={handleVideoCall}
            className="p-2 hover:bg-dark-700 rounded-lg text-dark-300 hover:text-white transition-colors"
            title="Video qo'ng'iroq"
          >
            <Video className="w-5 h-5" />
          </button>
          
          {/* Chat menu */}
          <div className="relative">
            <button 
              onClick={() => setShowChatMenu(!showChatMenu)}
              className="p-2 hover:bg-dark-700 rounded-lg text-dark-300 hover:text-white transition-colors"
            >
              <MoreVertical className="w-5 h-5" />
            </button>
            
            <AnimatePresence>
              {showChatMenu && (
                <>
                  <div 
                    className="fixed inset-0 z-40" 
                    onClick={() => setShowChatMenu(false)}
                  />
                  <motion.div
                    initial={{ opacity: 0, scale: 0.95, y: -10 }}
                    animate={{ opacity: 1, scale: 1, y: 0 }}
                    exit={{ opacity: 0, scale: 0.95, y: -10 }}
                    className="absolute right-0 top-full mt-2 w-48 glass-dark rounded-xl py-2 z-50"
                  >
                    <button 
                      onClick={() => {
                        setShowChatMenu(false);
                        toast('Xabarlarni qidirish tez orada!', { icon: '🔍' });
                      }}
                      className="w-full px-3 py-2 flex items-center gap-3 text-dark-300 hover:text-white hover:bg-dark-700 transition-colors"
                    >
                      <Search className="w-4 h-4" />
                      <span className="text-sm">Qidirish</span>
                    </button>
                    
                    {activeChat?.chat_type === 'group' && (
                      <button 
                        onClick={() => {
                          setShowChatMenu(false);
                          toast('A\'zo qo\'shish tez orada!', { icon: '👥' });
                        }}
                        className="w-full px-3 py-2 flex items-center gap-3 text-dark-300 hover:text-white hover:bg-dark-700 transition-colors"
                      >
                        <UserPlus className="w-4 h-4" />
                        <span className="text-sm">A'zo qo'shish</span>
                      </button>
                    )}
                    
                    <button 
                      onClick={() => {
                        setShowChatMenu(false);
                        toast('Pinned xabarlar tez orada!', { icon: '📌' });
                      }}
                      className="w-full px-3 py-2 flex items-center gap-3 text-dark-300 hover:text-white hover:bg-dark-700 transition-colors"
                    >
                      <Pin className="w-4 h-4" />
                      <span className="text-sm">Pinned xabarlar</span>
                    </button>
                    
                    <div className="border-t border-dark-600 mt-1 pt-1">
                      {activeChat?.chat_type === 'group' && (
                        <button
                          onClick={() => {
                            setShowChatMenu(false);
                            handleLeaveChat();
                          }}
                          className="w-full px-3 py-2 flex items-center gap-3 text-orange-400 hover:text-orange-300 hover:bg-orange-500/10 transition-colors"
                        >
                          <LogOut className="w-4 h-4" />
                          <span className="text-sm">Chatdan chiqish</span>
                        </button>
                      )}
                      
                      <button
                        onClick={() => {
                          setShowChatMenu(false);
                          handleDeleteChat();
                        }}
                        className="w-full px-3 py-2 flex items-center gap-3 text-red-400 hover:text-red-300 hover:bg-red-500/10 transition-colors"
                      >
                        <Trash2 className="w-4 h-4" />
                        <span className="text-sm">Chatni o'chirish</span>
                      </button>
                    </div>
                  </motion.div>
                </>
              )}
            </AnimatePresence>
          </div>
        </div>
      </header>

      {/* Messages */}
      <div
        ref={messagesContainerRef}
        className="flex-1 overflow-y-auto px-4 py-4 space-y-4"
        style={{
          backgroundImage: 'radial-gradient(circle at 50% 50%, rgba(30, 27, 75, 0.3) 0%, transparent 50%)',
        }}
      >
        {/* Load more button */}
        {hasMoreMessages && (
          <div className="text-center">
            <button
              onClick={handleLoadMore}
              disabled={messagesLoading}
              className="px-4 py-2 text-sm text-primary-400 hover:text-primary-300 disabled:opacity-50"
            >
              {messagesLoading ? 'Yuklanmoqda...' : 'Avvalgi xabarlarni yuklash'}
            </button>
          </div>
        )}

        {/* Messages */}
        <AnimatePresence initial={false}>
          {chatMessages.map((message, index) => {
            const isSent = message.sender_id === user?.id;
            const showAvatar = !isSent && (
              index === 0 || 
              chatMessages[index - 1]?.sender_id !== message.sender_id
            );

            return (
              <MessageBubble
                key={message.id}
                message={message}
                isSent={isSent}
                showAvatar={showAvatar}
              />
            );
          })}
        </AnimatePresence>

        {/* Typing indicator */}
        {typingList.length > 0 && (
          <motion.div
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex items-center gap-2"
          >
            <div className="px-4 py-3 bg-dark-800 rounded-2xl rounded-bl-sm">
              <div className="flex gap-1">
                <span className="w-2 h-2 bg-dark-400 rounded-full typing-dot" />
                <span className="w-2 h-2 bg-dark-400 rounded-full typing-dot" />
                <span className="w-2 h-2 bg-dark-400 rounded-full typing-dot" />
              </div>
            </div>
          </motion.div>
        )}

        <div ref={messagesEndRef} />
      </div>

      {/* Input area */}
      <div className="p-4 bg-dark-900 border-t border-dark-700">
        <div className="flex items-end gap-2">
          {/* Attachments */}
          <input
            ref={fileInputRef}
            type="file"
            onChange={handleFileSelect}
            className="hidden"
            accept="image/*,video/*,audio/*,.pdf,.doc,.docx,.zip"
          />
          <button 
            onClick={() => fileInputRef.current?.click()}
            disabled={isUploading}
            className="p-2.5 hover:bg-dark-700 rounded-xl text-dark-300 hover:text-white transition-colors flex-shrink-0 disabled:opacity-50"
            title="Fayl yuklash"
          >
            {isUploading ? (
              <div className="w-5 h-5 border-2 border-dark-400 border-t-primary-500 rounded-full animate-spin" />
            ) : (
              <Paperclip className="w-5 h-5" />
            )}
          </button>

          {/* Message input */}
          <div className="flex-1 relative">
            <textarea
              ref={inputRef}
              value={messageText}
              onChange={handleInputChange}
              onKeyDown={handleKeyDown}
              placeholder="Xabar yozing..."
              rows={1}
              className="w-full px-4 py-3 bg-dark-800 border border-dark-600 rounded-2xl text-white placeholder-dark-400 resize-none focus:outline-none focus:border-primary-500/50 transition-colors max-h-32 no-scrollbar"
              style={{ minHeight: '48px' }}
            />
            
            {/* Emoji button */}
            <div className="absolute right-2 bottom-2">
              <button
                onClick={() => setShowEmoji(!showEmoji)}
                className="p-1.5 hover:bg-dark-700 rounded-lg text-dark-400 hover:text-white transition-colors"
              >
                <Smile className="w-5 h-5" />
              </button>
              
              {showEmoji && (
                <>
                  <div
                    className="fixed inset-0 z-40"
                    onClick={() => setShowEmoji(false)}
                  />
                  <div className="absolute bottom-full right-0 mb-2 z-50">
                    <EmojiPicker
                      onEmojiClick={handleEmojiSelect}
                      width={320}
                      height={400}
                      theme={"dark" as any}
                    />
                  </div>
                </>
              )}
            </div>
          </div>

          {/* Send button */}
          <motion.button
            onClick={handleSend}
            disabled={!messageText.trim() || isSending}
            className={cn(
              'p-3 rounded-xl flex-shrink-0 transition-all duration-200',
              messageText.trim()
                ? 'bg-primary-500 text-white hover:bg-primary-600 shadow-glow'
                : 'bg-dark-700 text-dark-400'
            )}
            whileTap={{ scale: 0.95 }}
          >
            {isSending ? (
              <div className="w-5 h-5 border-2 border-white/30 border-t-white rounded-full animate-spin" />
            ) : (
              <Send className="w-5 h-5" />
            )}
          </motion.button>
        </div>
      </div>
    </div>
  );
}
