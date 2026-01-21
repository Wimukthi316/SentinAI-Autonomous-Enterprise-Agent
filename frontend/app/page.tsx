"use client";

import { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  Menu, 
  X, 
  History, 
  Activity, 
  Settings, 
  ShieldCheck,
  Cpu,
  HardDrive,
  Wifi
} from "lucide-react";
import ChatWindow from "@/components/ChatWindow";
import FileUpload from "@/components/FileUpload";
import ThinkingLog from "@/components/ThinkingLog";
import { useAgent, AgentStatus } from "@/hooks/useAgent";

export default function Home() {
  const [sidebarOpen, setSidebarOpen] = useState(true);
  const [activeTab, setActiveTab] = useState<"chat" | "history" | "settings">("chat");
  
  const {
    messages,
    isProcessing,
    agentStatus,
    thinkingSteps,
    sendMessage,
    uploadFile
  } = useAgent();

  const statusColors: Record<AgentStatus, string> = {
    ready: "bg-emerald-500",
    thinking: "bg-violet-500 animate-pulse",
    executing: "bg-blue-500 animate-pulse",
    error: "bg-red-500"
  };

  const statusText: Record<AgentStatus, string> = {
    ready: "Ready",
    thinking: "Thinking...",
    executing: "Executing Tool",
    error: "Error"
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-950 via-slate-900 to-slate-950 text-white overflow-hidden">
      {/* Mesh Gradient Background */}
      <div className="fixed inset-0 pointer-events-none">
        <div className="absolute top-0 left-1/4 w-96 h-96 bg-violet-600/20 rounded-full blur-3xl" />
        <div className="absolute bottom-0 right-1/4 w-96 h-96 bg-blue-600/20 rounded-full blur-3xl" />
        <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[800px] h-[800px] bg-cyan-600/10 rounded-full blur-3xl" />
      </div>

      <div className="relative flex h-screen">
        {/* Sidebar */}
        <AnimatePresence>
          {sidebarOpen && (
            <motion.aside
              initial={{ x: -280, opacity: 0 }}
              animate={{ x: 0, opacity: 1 }}
              exit={{ x: -280, opacity: 0 }}
              transition={{ type: "spring", damping: 25, stiffness: 200 }}
              className="w-72 h-full flex-shrink-0 border-r border-white/10"
            >
              <div className="h-full backdrop-blur-xl bg-slate-900/60 p-4 flex flex-col">
                {/* Logo */}
                <div className="flex items-center gap-3 mb-8 px-2">
                  <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-500 to-blue-500 flex items-center justify-center">
                    <ShieldCheck className="w-6 h-6 text-white" />
                  </div>
                  <div>
                    <h1 className="font-bold text-lg bg-gradient-to-r from-violet-400 to-blue-400 bg-clip-text text-transparent">
                      SentinAI
                    </h1>
                    <p className="text-xs text-slate-400">Enterprise Agent</p>
                  </div>
                </div>

                {/* Navigation */}
                <nav className="flex-1 space-y-2">
                  <SidebarItem 
                    icon={<Activity className="w-5 h-5" />}
                    label="Dashboard"
                    active={activeTab === "chat"}
                    onClick={() => setActiveTab("chat")}
                  />
                  <SidebarItem 
                    icon={<History className="w-5 h-5" />}
                    label="History"
                    active={activeTab === "history"}
                    onClick={() => setActiveTab("history")}
                  />
                  <SidebarItem 
                    icon={<Settings className="w-5 h-5" />}
                    label="API Settings"
                    active={activeTab === "settings"}
                    onClick={() => setActiveTab("settings")}
                  />
                </nav>

                {/* System Health Widget */}
                <div className="mt-auto">
                  <div className="p-4 rounded-2xl bg-slate-800/50 border border-white/5">
                    <h3 className="text-sm font-medium text-slate-300 mb-3 flex items-center gap-2">
                      <Cpu className="w-4 h-4 text-violet-400" />
                      System Health
                    </h3>
                    <div className="space-y-3">
                      <HealthBar label="CPU" value={45} icon={<Cpu className="w-3 h-3" />} />
                      <HealthBar label="GPU" value={72} icon={<HardDrive className="w-3 h-3" />} />
                      <HealthBar label="API" value={100} icon={<Wifi className="w-3 h-3" />} />
                    </div>
                  </div>
                </div>
              </div>
            </motion.aside>
          )}
        </AnimatePresence>

        {/* Main Content */}
        <div className="flex-1 flex flex-col min-w-0">
          {/* Header */}
          <header className="h-16 border-b border-white/10 backdrop-blur-xl bg-slate-900/40 flex items-center justify-between px-4 lg:px-6 flex-shrink-0">
            <div className="flex items-center gap-4">
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setSidebarOpen(!sidebarOpen)}
                className="p-2 rounded-xl hover:bg-white/5 transition-colors"
              >
                {sidebarOpen ? <X className="w-5 h-5" /> : <Menu className="w-5 h-5" />}
              </motion.button>
              <div className="hidden sm:block">
                <h2 className="font-semibold">Autonomous Workspace</h2>
                <p className="text-xs text-slate-400">Multi-modal AI Processing</p>
              </div>
            </div>

            {/* Agent Status */}
            <div className="flex items-center gap-3">
              <div className="flex items-center gap-2 px-4 py-2 rounded-full bg-slate-800/50 border border-white/10">
                <div className={`w-2 h-2 rounded-full ${statusColors[agentStatus]}`} />
                <span className="text-sm font-medium">{statusText[agentStatus]}</span>
              </div>
            </div>
          </header>

          {/* Main Workspace */}
          <main className="flex-1 overflow-hidden p-4 lg:p-6">
            <div className="h-full max-w-6xl mx-auto flex flex-col lg:flex-row gap-4 lg:gap-6">
              {/* Chat Section */}
              <div className="flex-1 flex flex-col min-h-0">
                <div className="flex-1 min-h-0 rounded-3xl backdrop-blur-xl bg-slate-900/40 border border-white/10 overflow-hidden flex flex-col">
                  <ChatWindow 
                    messages={messages}
                    isProcessing={isProcessing}
                    onSendMessage={sendMessage}
                    onFileUpload={uploadFile}
                  />
                </div>
              </div>

              {/* Right Panel - Thinking Log & File Upload */}
              <div className="w-full lg:w-80 flex flex-col gap-4 lg:gap-6 flex-shrink-0">
                {/* File Upload */}
                <FileUpload onUpload={uploadFile} isProcessing={isProcessing} />
                
                {/* Thinking Log */}
                <div className="flex-1 min-h-[200px] lg:min-h-0">
                  <ThinkingLog steps={thinkingSteps} isThinking={isProcessing} />
                </div>
              </div>
            </div>
          </main>
        </div>
      </div>
    </div>
  );
}

function SidebarItem({ 
  icon, 
  label, 
  active, 
  onClick 
}: { 
  icon: React.ReactNode; 
  label: string; 
  active: boolean;
  onClick: () => void;
}) {
  return (
    <motion.button
      whileHover={{ x: 4 }}
      whileTap={{ scale: 0.98 }}
      onClick={onClick}
      className={`w-full flex items-center gap-3 px-4 py-3 rounded-xl transition-all ${
        active 
          ? "bg-gradient-to-r from-violet-600/20 to-blue-600/20 border border-violet-500/30 text-white" 
          : "hover:bg-white/5 text-slate-400 hover:text-white"
      }`}
    >
      {icon}
      <span className="font-medium">{label}</span>
    </motion.button>
  );
}

function HealthBar({ 
  label, 
  value, 
  icon 
}: { 
  label: string; 
  value: number; 
  icon: React.ReactNode;
}) {
  const getColor = (val: number) => {
    if (val >= 80) return "from-emerald-500 to-emerald-400";
    if (val >= 50) return "from-violet-500 to-blue-500";
    return "from-amber-500 to-orange-500";
  };

  return (
    <div className="space-y-1">
      <div className="flex items-center justify-between text-xs">
        <span className="text-slate-400 flex items-center gap-1">
          {icon}
          {label}
        </span>
        <span className="text-slate-300">{value}%</span>
      </div>
      <div className="h-1.5 bg-slate-700/50 rounded-full overflow-hidden">
        <motion.div
          initial={{ width: 0 }}
          animate={{ width: `${value}%` }}
          transition={{ duration: 1, ease: "easeOut" }}
          className={`h-full rounded-full bg-gradient-to-r ${getColor(value)}`}
        />
      </div>
    </div>
  );
}
