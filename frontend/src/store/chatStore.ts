// ===========================================
// ChatFlow - Chat Store (Zustand)
// ===========================================

import { create } from 'zustand';
import { Chat, ChatListItem, Message, MessageList, WSNewMessage, WSTyping } from '@/types';
import { api } from '@/lib/api';
import { wsClient } from '@/lib/websocket';

interface ChatState {
  // Chat list
  chats: ChatListItem[];
  chatsLoading: boolean;
  
  // Active chat
  activeChat: Chat | null;
  activeChatId: string | null;
  
  // Messages
  messages: Map<string, Message[]>;
  messagesLoading: boolean;
  hasMoreMessages: boolean;
  
  // Typing indicators
  typingUsers: Map<string, Set<string>>; // chatId -> Set<username>
  
  // Unread counts
  totalUnread: number;
  
  // Actions
  loadChats: () => Promise<void>;
  selectChat: (chatId: string) => Promise<void>;
  loadMessages: (chatId: string, loadMore?: boolean) => Promise<void>;
  sendMessage: (content: string, replyToId?: string) => Promise<void>;
  
  // Real-time updates
  addNewMessage: (message: WSNewMessage) => void;
  updateMessage: (messageId: string, updates: Partial<Message>) => void;
  deleteMessage: (chatId: string, messageId: string) => void;
  setTyping: (chatId: string, username: string, isTyping: boolean) => void;
  updateOnlineStatus: (userId: string, isOnline: boolean) => void;
  
  // UI helpers
  clearActiveChat: () => void;
}

export const useChatStore = create<ChatState>((set, get) => ({
  chats: [],
  chatsLoading: false,
  activeChat: null,
  activeChatId: null,
  messages: new Map(),
  messagesLoading: false,
  hasMoreMessages: true,
  typingUsers: new Map(),
  totalUnread: 0,

  loadChats: async () => {
    set({ chatsLoading: true });
    try {
      const chats = await api.getChats();
      const totalUnread = chats.reduce((sum, chat) => sum + chat.unread_count, 0);
      set({ chats, totalUnread, chatsLoading: false });
    } catch (error) {
      console.error('Failed to load chats:', error);
      set({ chatsLoading: false });
    }
  },

  selectChat: async (chatId: string) => {
    set({ activeChatId: chatId, messagesLoading: true });
    
    try {
      // Load chat details
      const chat = await api.getChat(chatId);
      set({ activeChat: chat });
      
      // Load messages if not cached
      const cached = get().messages.get(chatId);
      if (!cached || cached.length === 0) {
        await get().loadMessages(chatId);
      } else {
        set({ messagesLoading: false });
      }
      
      // Mark as read
      await api.markAsRead(chatId);
      
      // Update unread count in chat list
      set((state) => ({
        chats: state.chats.map((c) =>
          c.id === chatId ? { ...c, unread_count: 0 } : c
        ),
        totalUnread: Math.max(0, state.totalUnread - (
          state.chats.find((c) => c.id === chatId)?.unread_count || 0
        )),
      }));
      
      // Subscribe to chat updates
      wsClient.subscribeToChat(chatId);
    } catch (error) {
      console.error('Failed to select chat:', error);
      set({ messagesLoading: false });
    }
  },

  loadMessages: async (chatId: string, loadMore = false) => {
    const currentMessages = get().messages.get(chatId) || [];
    const before = loadMore && currentMessages.length > 0
      ? currentMessages[0].id
      : undefined;
    
    set({ messagesLoading: true });
    
    try {
      const result = await api.getMessages(chatId, before);
      
      set((state) => {
        const existingMessages = state.messages.get(chatId) || [];
        const newMessages = loadMore
          ? [...result.messages, ...existingMessages]
          : result.messages;
        
        const updatedMessages = new Map(state.messages);
        updatedMessages.set(chatId, newMessages);
        
        return {
          messages: updatedMessages,
          hasMoreMessages: result.has_more,
          messagesLoading: false,
        };
      });
    } catch (error) {
      console.error('Failed to load messages:', error);
      set({ messagesLoading: false });
    }
  },

  sendMessage: async (content: string, replyToId?: string) => {
    const chatId = get().activeChatId;
    if (!chatId || !content.trim()) return;
    
    try {
      const message = await api.sendMessage(chatId, content.trim(), replyToId);
      
      // Add message to local state
      set((state) => {
        const messages = state.messages.get(chatId) || [];
        const updatedMessages = new Map(state.messages);
        updatedMessages.set(chatId, [...messages, message]);
        
        // Update chat list
        const updatedChats = state.chats.map((chat) => {
          if (chat.id === chatId) {
            return {
              ...chat,
              last_message: {
                id: message.id,
                content: message.content,
                message_type: message.message_type,
                sender_id: message.sender_id,
                sender_name: message.sender?.full_name,
                created_at: message.created_at,
              },
              last_message_at: message.created_at,
            };
          }
          return chat;
        });
        
        return {
          messages: updatedMessages,
          chats: updatedChats,
        };
      });
      
      // Stop typing indicator
      wsClient.sendTypingStop(chatId);
    } catch (error) {
      console.error('Failed to send message:', error);
      throw error;
    }
  },

  addNewMessage: (wsMessage: WSNewMessage) => {
    set((state) => {
      const messages = state.messages.get(wsMessage.chat_id) || [];
      
      // Check if message already exists
      if (messages.some((m) => m.id === wsMessage.id)) {
        return state;
      }
      
      // Convert WSNewMessage to Message format
      const message: Message = {
        id: wsMessage.id,
        chat_id: wsMessage.chat_id,
        sender_id: wsMessage.sender_id,
        sender: wsMessage.sender_id
          ? {
              id: wsMessage.sender_id,
              username: wsMessage.sender_name || '',
              full_name: wsMessage.sender_name || '',
              avatar_url: wsMessage.sender_avatar,
              status: 'online',
            }
          : undefined,
        content: wsMessage.content,
        message_type: wsMessage.message_type as any,
        status: 'delivered',
        is_edited: false,
        is_deleted: false,
        is_pinned: false,
        attachments: wsMessage.attachments,
        reactions: [],
        created_at: wsMessage.created_at,
        updated_at: wsMessage.created_at,
      };
      
      const updatedMessages = new Map(state.messages);
      updatedMessages.set(wsMessage.chat_id, [...messages, message]);
      
      // Update chat list
      const isActiveChat = state.activeChatId === wsMessage.chat_id;
      const updatedChats = state.chats.map((chat) => {
        if (chat.id === wsMessage.chat_id) {
          return {
            ...chat,
            last_message: {
              id: message.id,
              content: message.content,
              message_type: message.message_type,
              sender_id: message.sender_id,
              sender_name: wsMessage.sender_name,
              created_at: message.created_at,
            },
            last_message_at: message.created_at,
            unread_count: isActiveChat ? 0 : chat.unread_count + 1,
          };
        }
        return chat;
      });
      
      return {
        messages: updatedMessages,
        chats: updatedChats,
        totalUnread: isActiveChat ? state.totalUnread : state.totalUnread + 1,
      };
    });
  },

  updateMessage: (messageId: string, updates: Partial<Message>) => {
    set((state) => {
      const updatedMessages = new Map(state.messages);
      
      updatedMessages.forEach((messages, chatId) => {
        const index = messages.findIndex((m) => m.id === messageId);
        if (index !== -1) {
          const newMessages = [...messages];
          newMessages[index] = { ...newMessages[index], ...updates };
          updatedMessages.set(chatId, newMessages);
        }
      });
      
      return { messages: updatedMessages };
    });
  },

  deleteMessage: (chatId: string, messageId: string) => {
    set((state) => {
      const messages = state.messages.get(chatId) || [];
      const updatedMessages = new Map(state.messages);
      updatedMessages.set(
        chatId,
        messages.filter((m) => m.id !== messageId)
      );
      
      return { messages: updatedMessages };
    });
  },

  setTyping: (chatId: string, username: string, isTyping: boolean) => {
    set((state) => {
      const typingUsers = new Map(state.typingUsers);
      const chatTyping = new Set(typingUsers.get(chatId) || []);
      
      if (isTyping) {
        chatTyping.add(username);
      } else {
        chatTyping.delete(username);
      }
      
      if (chatTyping.size > 0) {
        typingUsers.set(chatId, chatTyping);
      } else {
        typingUsers.delete(chatId);
      }
      
      return { typingUsers };
    });
  },

  updateOnlineStatus: (userId: string, isOnline: boolean) => {
    set((state) => ({
      chats: state.chats.map((chat) => {
        if (chat.chat_type === 'private' && chat.other_user?.id === userId) {
          return { ...chat, is_online: isOnline };
        }
        return chat;
      }),
    }));
  },

  clearActiveChat: () => {
    const currentChatId = get().activeChatId;
    if (currentChatId) {
      wsClient.unsubscribeFromChat(currentChatId);
    }
    set({ activeChat: null, activeChatId: null });
  },
}));

