// ===========================================
// ChatFlow - TypeScript Types
// ===========================================

export interface User {
  id: string;
  email: string;
  username: string;
  full_name: string;
  avatar_url?: string;
  bio?: string;
  status: 'online' | 'offline' | 'away' | 'busy';
  last_seen?: string;
  status_message?: string;
  is_active: boolean;
  is_verified: boolean;
  created_at: string;
}

export interface UserProfile {
  id: string;
  username: string;
  full_name: string;
  avatar_url?: string;
  bio?: string;
  status: string;
  last_seen?: string;
  status_message?: string;
}

export interface Chat {
  id: string;
  name?: string;
  description?: string;
  avatar_url?: string;
  chat_type: 'private' | 'group' | 'channel';
  is_active: boolean;
  invite_link?: string;
  last_message_at?: string;
  created_at: string;
  members: ChatMember[];
  member_count: number;
}

export interface ChatListItem {
  id: string;
  name?: string;
  avatar_url?: string;
  chat_type: 'private' | 'group' | 'channel';
  is_muted: boolean;
  is_pinned: boolean;
  unread_count: number;
  last_message?: LastMessagePreview;
  last_message_at?: string;
  other_user?: UserProfile;
  is_online: boolean;
}

export interface ChatMember {
  id: string;
  user_id: string;
  role: 'owner' | 'admin' | 'member';
  nickname?: string;
  is_active: boolean;
  joined_at: string;
  user?: UserProfile;
}

export interface LastMessagePreview {
  id: string;
  content?: string;
  message_type: string;
  sender_id?: string;
  sender_name?: string;
  created_at: string;
}

export interface Message {
  id: string;
  chat_id: string;
  sender_id?: string;
  sender?: UserProfile;
  content?: string;
  message_type: MessageType;
  status: 'sending' | 'sent' | 'delivered' | 'read' | 'failed';
  reply_to?: ReplyPreview;
  forwarded_from_id?: string;
  is_edited: boolean;
  edited_at?: string;
  is_deleted: boolean;
  is_pinned: boolean;
  attachments: Attachment[];
  reactions: ReactionSummary[];
  created_at: string;
  updated_at: string;
}

export type MessageType = 
  | 'text'
  | 'image'
  | 'video'
  | 'audio'
  | 'file'
  | 'voice'
  | 'sticker'
  | 'gif'
  | 'location'
  | 'contact'
  | 'system';

export interface ReplyPreview {
  id: string;
  content?: string;
  message_type: string;
  sender?: UserProfile;
}

export interface Attachment {
  id: string;
  file_name: string;
  file_url: string;
  file_type: string;
  file_size: number;
  width?: number;
  height?: number;
  duration?: number;
  thumbnail_url?: string;
  created_at: string;
}

export interface ReactionSummary {
  emoji: string;
  count: number;
  users: string[];
  has_reacted: boolean;
}

export interface MessageList {
  messages: Message[];
  total: number;
  has_more: boolean;
  next_cursor?: string;
}

// Auth types
export interface TokenResponse {
  access_token: string;
  refresh_token: string;
  token_type: string;
  expires_in: number;
  user: User;
}

export interface LoginRequest {
  username: string;
  password: string;
}

export interface RegisterRequest {
  email: string;
  username: string;
  full_name: string;
  password: string;
}

// WebSocket event types
export type WSEventType =
  | 'connect'
  | 'disconnect'
  | 'ping'
  | 'pong'
  | 'message.new'
  | 'message.update'
  | 'message.delete'
  | 'message.reaction'
  | 'message.read'
  | 'typing.start'
  | 'typing.stop'
  | 'user.online'
  | 'user.offline'
  | 'user.status'
  | 'chat.new'
  | 'chat.update'
  | 'chat.delete'
  | 'chat.member.join'
  | 'chat.member.leave'
  | 'notification'
  | 'error';

export interface WSMessage<T = any> {
  event: WSEventType;
  data: T;
  timestamp: string;
}

export interface WSTyping {
  chat_id: string;
  user_id: string;
  username: string;
}

export interface WSNewMessage {
  id: string;
  chat_id: string;
  sender_id?: string;
  sender_name?: string;
  sender_avatar?: string;
  content?: string;
  message_type: string;
  reply_to_id?: string;
  attachments: any[];
  created_at: string;
}

