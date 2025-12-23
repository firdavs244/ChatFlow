'use client';

import { useState } from 'react';
import { motion } from 'framer-motion';
import { Check, CheckCheck, MoreHorizontal, Reply, Copy, Trash, Edit, Smile } from 'lucide-react';
import { Message } from '@/types';
import { cn, formatMessageTime, getInitials, getAvatarColor } from '@/lib/utils';

interface MessageBubbleProps {
  message: Message;
  isSent: boolean;
  showAvatar: boolean;
}

export default function MessageBubble({ message, isSent, showAvatar }: MessageBubbleProps) {
  const [showActions, setShowActions] = useState(false);

  const renderStatusIcon = () => {
    switch (message.status) {
      case 'sending':
        return <div className="w-3 h-3 border border-current border-t-transparent rounded-full animate-spin" />;
      case 'sent':
        return <Check className="w-3.5 h-3.5" />;
      case 'delivered':
        return <CheckCheck className="w-3.5 h-3.5" />;
      case 'read':
        return <CheckCheck className="w-3.5 h-3.5 text-primary-400" />;
      default:
        return null;
    }
  };

  const renderReactions = () => {
    if (!message.reactions || message.reactions.length === 0) return null;

    return (
      <div className="flex flex-wrap gap-1 mt-1">
        {message.reactions.map((reaction) => (
          <button
            key={reaction.emoji}
            className={cn(
              'px-2 py-0.5 rounded-full text-xs flex items-center gap-1 transition-colors',
              reaction.has_reacted
                ? 'bg-primary-500/20 border border-primary-500/30'
                : 'bg-dark-700/50 border border-dark-600 hover:border-dark-500'
            )}
          >
            <span>{reaction.emoji}</span>
            <span className="text-dark-300">{reaction.count}</span>
          </button>
        ))}
      </div>
    );
  };

  const renderAttachments = () => {
    if (!message.attachments || message.attachments.length === 0) return null;

    return (
      <div className="space-y-2 mb-2">
        {message.attachments.map((attachment) => {
          if (attachment.file_type.startsWith('image/')) {
            return (
              <img
                key={attachment.id}
                src={attachment.file_url}
                alt={attachment.file_name}
                className="max-w-sm rounded-lg cursor-pointer hover:opacity-90 transition-opacity"
              />
            );
          }
          
          return (
            <a
              key={attachment.id}
              href={attachment.file_url}
              target="_blank"
              rel="noopener noreferrer"
              className="flex items-center gap-2 px-3 py-2 bg-dark-700/50 rounded-lg hover:bg-dark-700 transition-colors"
            >
              <div className="w-10 h-10 bg-dark-600 rounded-lg flex items-center justify-center">
                📄
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm text-white truncate">{attachment.file_name}</p>
                <p className="text-xs text-dark-400">
                  {(attachment.file_size / 1024).toFixed(1)} KB
                </p>
              </div>
            </a>
          );
        })}
      </div>
    );
  };

  if (message.is_deleted) {
    return (
      <div className={cn('flex', isSent ? 'justify-end' : 'justify-start')}>
        <div className="px-4 py-2 rounded-2xl bg-dark-800/30 border border-dark-700/50 text-dark-400 italic text-sm">
          Bu xabar o'chirilgan
        </div>
      </div>
    );
  }

  return (
    <motion.div
      initial={{ opacity: 0, y: 10 }}
      animate={{ opacity: 1, y: 0 }}
      className={cn('flex gap-2 group', isSent ? 'justify-end' : 'justify-start')}
      onMouseEnter={() => setShowActions(true)}
      onMouseLeave={() => setShowActions(false)}
    >
      {/* Avatar (for received messages) */}
      {!isSent && (
        <div className="flex-shrink-0 w-8">
          {showAvatar && message.sender ? (
            message.sender.avatar_url ? (
              <img
                src={message.sender.avatar_url}
                alt={message.sender.full_name}
                className="w-8 h-8 rounded-full object-cover"
              />
            ) : (
              <div
                className={cn(
                  'w-8 h-8 rounded-full flex items-center justify-center text-white text-xs font-medium',
                  getAvatarColor(message.sender.full_name)
                )}
              >
                {getInitials(message.sender.full_name)}
              </div>
            )
          ) : null}
        </div>
      )}

      <div className={cn('max-w-[70%] relative', isSent ? 'order-1' : 'order-2')}>
        {/* Reply preview */}
        {message.reply_to && (
          <div className={cn(
            'mb-1 px-3 py-1.5 rounded-lg border-l-2 text-xs',
            isSent
              ? 'bg-primary-900/30 border-primary-400'
              : 'bg-dark-700/50 border-dark-400'
          )}>
            <p className="font-medium text-dark-300">
              {message.reply_to.sender?.full_name || 'Foydalanuvchi'}
            </p>
            <p className="text-dark-400 truncate">
              {message.reply_to.content || `[${message.reply_to.message_type}]`}
            </p>
          </div>
        )}

        {/* Message bubble */}
        <div
          className={cn(
            'px-4 py-2.5 relative',
            isSent ? 'message-sent text-white' : 'message-received text-white'
          )}
        >
          {/* Sender name (in groups) */}
          {!isSent && showAvatar && message.sender && (
            <p className="text-xs font-medium text-primary-400 mb-1">
              {message.sender.full_name}
            </p>
          )}

          {/* Attachments */}
          {renderAttachments()}

          {/* Content */}
          {message.content && (
            <p className="whitespace-pre-wrap break-words">{message.content}</p>
          )}

          {/* Time and status */}
          <div className={cn(
            'flex items-center gap-1 mt-1',
            isSent ? 'justify-end' : 'justify-start'
          )}>
            {message.is_edited && (
              <span className="text-xs text-dark-400/70">tahrirlangan</span>
            )}
            <span className={cn(
              'text-xs',
              isSent ? 'text-white/60' : 'text-dark-400'
            )}>
              {formatMessageTime(message.created_at)}
            </span>
            {isSent && (
              <span className={cn('ml-1', message.status === 'read' ? 'text-primary-400' : 'text-white/60')}>
                {renderStatusIcon()}
              </span>
            )}
          </div>
        </div>

        {/* Reactions */}
        {renderReactions()}

        {/* Actions menu */}
        {showActions && (
          <motion.div
            initial={{ opacity: 0, scale: 0.9 }}
            animate={{ opacity: 1, scale: 1 }}
            className={cn(
              'absolute top-0 flex items-center gap-0.5 glass-dark rounded-lg p-1',
              isSent ? 'right-full mr-2' : 'left-full ml-2'
            )}
          >
            <button className="p-1.5 hover:bg-dark-600 rounded text-dark-300 hover:text-white transition-colors">
              <Reply className="w-4 h-4" />
            </button>
            <button className="p-1.5 hover:bg-dark-600 rounded text-dark-300 hover:text-white transition-colors">
              <Smile className="w-4 h-4" />
            </button>
            <button className="p-1.5 hover:bg-dark-600 rounded text-dark-300 hover:text-white transition-colors">
              <Copy className="w-4 h-4" />
            </button>
            {isSent && (
              <>
                <button className="p-1.5 hover:bg-dark-600 rounded text-dark-300 hover:text-white transition-colors">
                  <Edit className="w-4 h-4" />
                </button>
                <button className="p-1.5 hover:bg-red-500/20 rounded text-dark-300 hover:text-red-400 transition-colors">
                  <Trash className="w-4 h-4" />
                </button>
              </>
            )}
          </motion.div>
        )}
      </div>
    </motion.div>
  );
}

