'use client';

import { useState, useRef, useEffect } from 'react';
import { Button } from '@/components/ui/button';
import { Input } from '@/components/ui/input';
import { Card, CardContent, CardHeader, CardTitle } from '@/components/ui/card';
import { ScrollArea } from '@/components/ui/scroll-area';
import { Avatar, AvatarFallback } from '@/components/ui/avatar';
import { X, Send, Bot, User, Loader2 } from 'lucide-react';
import { useStore } from '@/lib/store';
import { chatAPI } from '@/lib/api';
import {useChat} from "@ai-sdk/react"

interface Message {
  id: string;
  role: 'user' | 'assistant';
  content: string;
  timestamp: Date;
}

export function ChatWithArticle() {
  const { chatOpen, currentArticle, toggleChat } = useStore();
  const [inputValue, setInputValue] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  const scrollAreaRef = useRef<HTMLDivElement>(null);
  const { messages, sendMessage } = useChat();

  useEffect(() => {
    if (chatOpen && currentArticle) {
      const welcomeMessage = `this is the article: "${currentArticle.title}". answer any follow up question about this article and do not answer anuthing out of this context. if you understood just say exactly: ask anything about the article!`

      sendMessage({text: welcomeMessage, metadata: { role: 'system' } });
    }
  }, [chatOpen, currentArticle]);

  useEffect(() => {
    // Scroll to bottom when new message is added
    if (scrollAreaRef.current) {
      scrollAreaRef.current.scrollTop = scrollAreaRef.current.scrollHeight;
    }
  }, [messages]);

  if (!chatOpen || !currentArticle) return null;

  return (
    <div className="fixed inset-y-0 right-0 w-96 bg-background border-l shadow-lg z-50 flex flex-col">
      <CardHeader className="border-b">
        <div className="flex items-center justify-between">
          <CardTitle className="text-lg flex items-center space-x-2">
            <Bot className="w-5 h-5" />
            <span>Chat with Article</span>
          </CardTitle>
          <Button variant="ghost" size="icon" onClick={() => toggleChat()}>
            <X className="w-4 h-4" />
          </Button>
        </div>
        <p className="text-sm text-muted-foreground line-clamp-2">
          {currentArticle.title}
        </p>
      </CardHeader>

      <CardContent className="flex-1 p-0 flex flex-col">
        <ScrollArea className="flex-1 p-4 max-h-[75vh]" ref={scrollAreaRef}>
          <div className="space-y-4">
            {messages.map((message) => message.id != "system_prompt" && (
              <div
                key={message.id}
                className={`flex items-start space-x-3 ${
                  message.role === 'user' ? 'flex-row-reverse space-x-reverse' : ''
                }`}
              >
                <Avatar className="w-8 h-8 flex-shrink-0">
                  <AvatarFallback>
                    {message.role === 'user' ? (
                      <User className="w-4 h-4" />
                    ) : (
                      <Bot className="w-4 h-4" />
                    )}
                  </AvatarFallback>
                </Avatar>
                <div
                  className={`flex-1 rounded-lg px-3 py-2 text-sm ${
                    message.role === 'user'
                      ? 'bg-primary text-primary-foreground ml-12'
                      : 'bg-muted mr-12'
                  }`}
                >
                  <p className="whitespace-pre-wrap">
                  {message.parts.map((part, i) => {
                      switch (part.type) {
                        case 'text':
                          return <span key={`${message.id}-${i}`}>{part.text}</span>;
                      }
                    })}
                  </p>
                  {/* <p
                    className={`text-xs mt-1 opacity-70 ${
                      message.role === 'user' ? 'text-primary-foreground' : 'text-muted-foreground'
                    }`}
                  >
                    {message.timestamp.toLocaleTimeString()}
                  </p> */}
                </div>
              </div>
            ))}
            
            {isLoading && (
              <div className="flex items-start space-x-3">
                <Avatar className="w-8 h-8">
                  <AvatarFallback>
                    <Bot className="w-4 h-4" />
                  </AvatarFallback>
                </Avatar>
                <div className="bg-muted rounded-lg px-3 py-2 mr-12">
                  <div className="flex items-center space-x-2">
                    <Loader2 className="w-4 h-4 animate-spin" />
                    <span className="text-sm">Thinking...</span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </ScrollArea>

        <div className="border-t p-4">
          <form
            onSubmit={e => {
              e.preventDefault();
              sendMessage({ text: inputValue, metadata: { role: 'user' } });
              setInputValue('');
            }}
            className="flex space-x-2"
          >
            {/* <input
              className="fixed dark:bg-zinc-900 bottom-0 w-full max-w-md p-2 mb-8 border border-zinc-300 dark:border-zinc-800 rounded shadow-xl"
              value={input}
              placeholder="Say something..."
              onChange={e => setInput(e.currentTarget.value)}
            /> */}
            <Input
              value={inputValue}
              onChange={(e) => setInputValue(e.target.value)}
              placeholder="Ask about this article..."
              disabled={isLoading}
              className="flex-1"
            />
            <Button
              type='submit'
              disabled={!inputValue.trim() || isLoading}
              size="icon"
            >
              <Send className="w-4 h-4" />
            </Button>
          </form>
        </div>
      </CardContent>
    </div>
  );
}