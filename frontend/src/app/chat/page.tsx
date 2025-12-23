'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';
import { useAuthStore } from '@/store/authStore';
import { useChatStore } from '@/store/chatStore';
import { wsClient } from '@/lib/websocket';
import { WSNewMessage, WSTyping } from '@/types';
import ChatSidebar from '@/components/chat/ChatSidebar';
import ChatWindow from '@/components/chat/ChatWindow';
import EmptyChat from '@/components/chat/EmptyChat';

export default function ChatPage() {
  const router = useRouter();
  const { user, isAuthenticated, isLoading: authLoading, checkAuth } = useAuthStore();
  const { activeChatId, loadChats, addNewMessage, setTyping, updateOnlineStatus } = useChatStore();

  // Check authentication
  useEffect(() => {
    checkAuth();
  }, [checkAuth]);

  useEffect(() => {
    if (!authLoading && !isAuthenticated) {
      router.push('/login');
    }
  }, [isAuthenticated, authLoading, router]);

  // Load initial data
  useEffect(() => {
    if (isAuthenticated) {
      loadChats();
    }
  }, [isAuthenticated, loadChats]);

  // WebSocket event handlers
  useEffect(() => {
    if (!isAuthenticated) return;

    // New message handler
    const unsubNewMessage = wsClient.on<WSNewMessage>('message.new', (data) => {
      addNewMessage(data);
    });

    // Typing handlers
    const unsubTypingStart = wsClient.on<WSTyping>('typing.start', (data) => {
      setTyping(data.chat_id, data.username, true);
    });

    const unsubTypingStop = wsClient.on<WSTyping>('typing.stop', (data) => {
      setTyping(data.chat_id, data.username, false);
    });

    // Online status handlers
    const unsubOnline = wsClient.on('user.online', (data: any) => {
      updateOnlineStatus(data.user_id, true);
    });

    const unsubOffline = wsClient.on('user.offline', (data: any) => {
      updateOnlineStatus(data.user_id, false);
    });

    return () => {
      unsubNewMessage();
      unsubTypingStart();
      unsubTypingStop();
      unsubOnline();
      unsubOffline();
    };
  }, [isAuthenticated, addNewMessage, setTyping, updateOnlineStatus]);

  if (authLoading) {
    return (
      <div className="min-h-screen aurora-bg flex items-center justify-center">
        <div className="w-8 h-8 border-2 border-primary-500/30 border-t-primary-500 rounded-full animate-spin" />
      </div>
    );
  }

  if (!isAuthenticated) {
    return null;
  }

  return (
    <main className="h-screen bg-dark-950 flex overflow-hidden">
      {/* Sidebar */}
      <ChatSidebar />
      
      {/* Main content */}
      <div className="flex-1 flex flex-col">
        {activeChatId ? <ChatWindow /> : <EmptyChat />}
      </div>
    </main>
  );
}

