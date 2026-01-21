"use client";

import { useState, useRef, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { Send, Mic, Paperclip, Bot, User, Sparkles } from "lucide-react";
import { Message } from "@/hooks/useAgent";

interface ChatWindowProps {
  messages: Message[];
  isProcessing: boolean;
  onSendMessage: (message: string) => void;
  onFileUpload: (file: File, query: string) => void;
}

export default function ChatWindow({
  messages,
  isProcessing,
  onSendMessage,
  onFileUpload
}: ChatWindowProps) {
  const [input, setInput] = useState("");
  const [isRecording, setIsRecording] = useState(false);
  const messagesEndRef = useRef<HTMLDivElement>(null);
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const fileInputRef = useRef<HTMLInputElement>(null);

  useEffect(() => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  }, [messages]);

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (!input.trim() || isProcessing) return;
    onSendMessage(input.trim());
    setInput("");
  };

  const handleKeyDown = (e: React.KeyboardEvent) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSubmit(e);
    }
  };

  const handleFileSelect = (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (file) {
      onFileUpload(file, input || "Analyze this file");
      setInput("");
    }
  };

  const toggleRecording = () => {
    setIsRecording(!isRecording);
    // Voice recording would be implemented here
  };

  return (
    <>
      {/* Messages Container */}
      <div className="flex-1 overflow-y-auto p-4 lg:p-6 space-y-4">
        {messages.length === 0 ? (
          <WelcomeScreen />
        ) : (
          <AnimatePresence initial={false}>
            {messages.map((message) => (
              <MessageBubble key={message.id} message={message} />
            ))}
          </AnimatePresence>
        )}
        
        {/* Thinking Skeleton */}
        {isProcessing && (
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="flex items-start gap-3"
          >
            <div className="w-10 h-10 rounded-2xl bg-gradient-to-br from-violet-600 to-blue-600 flex items-center justify-center flex-shrink-0">
              <Bot className="w-5 h-5 text-white" />
            </div>
            <div className="flex-1 max-w-2xl">
              <div className="bg-slate-800/50 backdrop-blur-sm rounded-2xl rounded-tl-md p-4 border border-white/5">
                <div className="flex items-center gap-2">
                  <div className="flex gap-1">
                    <motion.div
                      animate={{ scale: [1, 1.2, 1] }}
                      transition={{ duration: 0.6, repeat: Infinity, delay: 0 }}
                      className="w-2 h-2 rounded-full bg-violet-500"
                    />
                    <motion.div
                      animate={{ scale: [1, 1.2, 1] }}
                      transition={{ duration: 0.6, repeat: Infinity, delay: 0.2 }}
                      className="w-2 h-2 rounded-full bg-blue-500"
                    />
                    <motion.div
                      animate={{ scale: [1, 1.2, 1] }}
                      transition={{ duration: 0.6, repeat: Infinity, delay: 0.4 }}
                      className="w-2 h-2 rounded-full bg-cyan-500"
                    />
                  </div>
                  <span className="text-sm text-slate-400">SentinAI is thinking...</span>
                </div>
              </div>
            </div>
          </motion.div>
        )}
        
        <div ref={messagesEndRef} />
      </div>

      {/* Input Area */}
      <div className="p-4 border-t border-white/10">
        <form onSubmit={handleSubmit} className="relative">
          <div className="flex items-end gap-2 p-2 rounded-2xl bg-slate-800/50 border border-white/10 focus-within:border-violet-500/50 transition-colors">
            {/* File Attach */}
            <input
              type="file"
              ref={fileInputRef}
              onChange={handleFileSelect}
              accept=".pdf,.jpg,.jpeg,.png,.mp3,.wav,.m4a"
              className="hidden"
            />
            <motion.button
              type="button"
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              onClick={() => fileInputRef.current?.click()}
              className="p-2 rounded-xl hover:bg-white/5 text-slate-400 hover:text-violet-400 transition-colors"
            >
              <Paperclip className="w-5 h-5" />
            </motion.button>

            {/* Text Input */}
            <textarea
              ref={inputRef}
              value={input}
              onChange={(e) => setInput(e.target.value)}
              onKeyDown={handleKeyDown}
              placeholder="Ask SentinAI anything..."
              disabled={isProcessing}
              rows={1}
              className="flex-1 bg-transparent text-white placeholder-slate-500 resize-none outline-none py-2 px-2 max-h-32"
              style={{ minHeight: "40px" }}
            />

            {/* Voice Record */}
            <motion.button
              type="button"
              whileHover={{ scale: 1.1 }}
              whileTap={{ scale: 0.9 }}
              onClick={toggleRecording}
              className={`p-2 rounded-xl transition-colors ${
                isRecording 
                  ? "bg-red-500/20 text-red-400" 
                  : "hover:bg-white/5 text-slate-400 hover:text-violet-400"
              }`}
            >
              <Mic className="w-5 h-5" />
            </motion.button>

            {/* Send Button */}
            <motion.button
              type="submit"
              disabled={!input.trim() || isProcessing}
              whileHover={{ scale: 1.05 }}
              whileTap={{ scale: 0.95 }}
              className="p-2.5 rounded-xl bg-gradient-to-r from-violet-600 to-blue-600 text-white disabled:opacity-50 disabled:cursor-not-allowed transition-opacity"
            >
              <Send className="w-5 h-5" />
            </motion.button>
          </div>
        </form>
      </div>
    </>
  );
}

function MessageBubble({ message }: { message: Message }) {
  const isUser = message.role === "user";

  return (
    <motion.div
      initial={{ opacity: 0, y: 20, scale: 0.95 }}
      animate={{ opacity: 1, y: 0, scale: 1 }}
      transition={{ type: "spring", damping: 25, stiffness: 300 }}
      className={`flex items-start gap-3 ${isUser ? "flex-row-reverse" : ""}`}
    >
      {/* Avatar */}
      <motion.div
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ delay: 0.1, type: "spring" }}
        className={`w-10 h-10 rounded-2xl flex items-center justify-center flex-shrink-0 ${
          isUser 
            ? "bg-gradient-to-br from-slate-600 to-slate-700" 
            : "bg-gradient-to-br from-violet-600 to-blue-600"
        }`}
      >
        {isUser ? (
          <User className="w-5 h-5 text-white" />
        ) : (
          <Bot className="w-5 h-5 text-white" />
        )}
      </motion.div>

      {/* Message Content */}
      <div className={`flex-1 max-w-2xl ${isUser ? "flex justify-end" : ""}`}>
        <div
          className={`p-4 rounded-2xl ${
            isUser
              ? "bg-gradient-to-r from-violet-600/80 to-blue-600/80 rounded-tr-md"
              : "bg-slate-800/50 backdrop-blur-sm border border-white/5 rounded-tl-md"
          }`}
        >
          <p className="text-white whitespace-pre-wrap leading-relaxed">
            {message.content}
          </p>
          
          {/* File Attachment */}
          {message.file && (
            <div className="mt-2 pt-2 border-t border-white/10">
              <span className="text-xs text-slate-400 flex items-center gap-1">
                <Paperclip className="w-3 h-3" />
                {message.file}
              </span>
            </div>
          )}
        </div>
        
        {/* Timestamp */}
        <p className={`text-xs text-slate-500 mt-1 ${isUser ? "text-right" : ""}`}>
          {new Date(message.timestamp).toLocaleTimeString([], { 
            hour: "2-digit", 
            minute: "2-digit" 
          })}
        </p>
      </div>
    </motion.div>
  );
}

function WelcomeScreen() {
  const suggestions = [
    "Transcribe an audio file",
    "Analyze a document",
    "Classify a support ticket",
    "Ask about system capabilities"
  ];

  return (
    <motion.div
      initial={{ opacity: 0, y: 20 }}
      animate={{ opacity: 1, y: 0 }}
      className="flex flex-col items-center justify-center h-full text-center px-4"
    >
      <motion.div
        initial={{ scale: 0 }}
        animate={{ scale: 1 }}
        transition={{ delay: 0.2, type: "spring" }}
        className="w-20 h-20 rounded-3xl bg-gradient-to-br from-violet-600 to-blue-600 flex items-center justify-center mb-6"
      >
        <Sparkles className="w-10 h-10 text-white" />
      </motion.div>
      
      <h2 className="text-2xl font-bold mb-2 bg-gradient-to-r from-violet-400 to-blue-400 bg-clip-text text-transparent">
        Welcome to SentinAI
      </h2>
      <p className="text-slate-400 mb-8 max-w-md">
        Your autonomous enterprise AI agent. Upload files, ask questions, 
        or let me handle complex workflows automatically.
      </p>

      <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 w-full max-w-md">
        {suggestions.map((suggestion, index) => (
          <motion.button
            key={suggestion}
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.3 + index * 0.1 }}
            whileHover={{ scale: 1.02, y: -2 }}
            whileTap={{ scale: 0.98 }}
            className="p-4 rounded-2xl bg-slate-800/30 border border-white/5 hover:border-violet-500/30 text-left text-sm text-slate-300 hover:text-white transition-all"
          >
            {suggestion}
          </motion.button>
        ))}
      </div>
    </motion.div>
  );
}
