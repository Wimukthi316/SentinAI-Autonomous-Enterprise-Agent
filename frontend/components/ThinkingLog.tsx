"use client";

import { motion, AnimatePresence } from "framer-motion";
import { 
  ChevronDown, 
  ChevronRight,
  Mic,
  FileSearch,
  Tag,
  CheckCircle,
  Loader2,
  Brain,
  Sparkles
} from "lucide-react";
import { useState } from "react";
import { ThinkingStep } from "@/hooks/useAgent";

interface ThinkingLogProps {
  steps: ThinkingStep[];
  isThinking: boolean;
}

export default function ThinkingLog({ steps, isThinking }: ThinkingLogProps) {
  const [isExpanded, setIsExpanded] = useState(true);

  const getStepIcon = (type: ThinkingStep["type"]) => {
    switch (type) {
      case "audio": return <Mic className="w-4 h-4" />;
      case "document": return <FileSearch className="w-4 h-4" />;
      case "classify": return <Tag className="w-4 h-4" />;
      case "reasoning": return <Brain className="w-4 h-4" />;
      default: return <Sparkles className="w-4 h-4" />;
    }
  };

  const getStepColor = (type: ThinkingStep["type"]) => {
    switch (type) {
      case "audio": return "text-violet-400 bg-violet-500/10";
      case "document": return "text-blue-400 bg-blue-500/10";
      case "classify": return "text-emerald-400 bg-emerald-500/10";
      case "reasoning": return "text-amber-400 bg-amber-500/10";
      default: return "text-slate-400 bg-slate-500/10";
    }
  };

  return (
    <div className="h-full rounded-3xl backdrop-blur-xl bg-slate-900/40 border border-white/10 flex flex-col">
      {/* Header */}
      <button
        onClick={() => setIsExpanded(!isExpanded)}
        className="flex items-center justify-between p-4 border-b border-white/5 hover:bg-white/5 transition-colors"
      >
        <div className="flex items-center gap-2">
          <Brain className="w-4 h-4 text-violet-400" />
          <span className="text-sm font-medium text-slate-300">Internal Steps</span>
          {steps.length > 0 && (
            <span className="px-2 py-0.5 rounded-full bg-violet-500/20 text-violet-400 text-xs">
              {steps.length}
            </span>
          )}
        </div>
        {isExpanded ? (
          <ChevronDown className="w-4 h-4 text-slate-400" />
        ) : (
          <ChevronRight className="w-4 h-4 text-slate-400" />
        )}
      </button>

      {/* Steps List */}
      <AnimatePresence>
        {isExpanded && (
          <motion.div
            initial={{ height: 0, opacity: 0 }}
            animate={{ height: "auto", opacity: 1 }}
            exit={{ height: 0, opacity: 0 }}
            className="flex-1 overflow-hidden"
          >
            <div className="p-4 space-y-3 max-h-[300px] lg:max-h-none overflow-y-auto">
              {steps.length === 0 && !isThinking ? (
                <div className="text-center py-8">
                  <div className="w-12 h-12 mx-auto mb-3 rounded-2xl bg-slate-800/50 flex items-center justify-center">
                    <Brain className="w-6 h-6 text-slate-600" />
                  </div>
                  <p className="text-sm text-slate-500">
                    No steps yet
                  </p>
                  <p className="text-xs text-slate-600 mt-1">
                    Processing steps will appear here
                  </p>
                </div>
              ) : (
                <AnimatePresence>
                  {steps.map((step, index) => (
                    <motion.div
                      key={step.id}
                      initial={{ opacity: 0, x: -20 }}
                      animate={{ opacity: 1, x: 0 }}
                      transition={{ delay: index * 0.1 }}
                      className="flex items-start gap-3"
                    >
                      {/* Timeline Connector */}
                      <div className="flex flex-col items-center">
                        <div className={`w-8 h-8 rounded-xl flex items-center justify-center ${getStepColor(step.type)}`}>
                          {step.status === "running" ? (
                            <Loader2 className="w-4 h-4 animate-spin" />
                          ) : step.status === "completed" ? (
                            getStepIcon(step.type)
                          ) : (
                            getStepIcon(step.type)
                          )}
                        </div>
                        {index < steps.length - 1 && (
                          <div className="w-0.5 h-full min-h-[20px] bg-slate-700/50 mt-2" />
                        )}
                      </div>

                      {/* Step Content */}
                      <div className="flex-1 pb-3">
                        <div className="flex items-center justify-between">
                          <p className="text-sm font-medium text-white">
                            {step.title}
                          </p>
                          {step.status === "completed" && (
                            <CheckCircle className="w-4 h-4 text-emerald-500" />
                          )}
                          {step.status === "running" && (
                            <span className="text-xs text-violet-400 animate-pulse">
                              Processing...
                            </span>
                          )}
                        </div>
                        <p className="text-xs text-slate-400 mt-0.5">
                          {step.description}
                        </p>
                        {step.duration && (
                          <p className="text-xs text-slate-500 mt-1">
                            Completed in {step.duration}ms
                          </p>
                        )}
                      </div>
                    </motion.div>
                  ))}

                  {/* Active Thinking Indicator */}
                  {isThinking && (
                    <motion.div
                      initial={{ opacity: 0 }}
                      animate={{ opacity: 1 }}
                      className="flex items-center gap-3 pt-2"
                    >
                      <div className="w-8 h-8 rounded-xl bg-violet-500/10 flex items-center justify-center">
                        <Loader2 className="w-4 h-4 text-violet-400 animate-spin" />
                      </div>
                      <div>
                        <p className="text-sm text-slate-300">Thinking...</p>
                        <p className="text-xs text-slate-500">Agent is processing</p>
                      </div>
                    </motion.div>
                  )}
                </AnimatePresence>
              )}
            </div>
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
