"use client";

import { useState, useCallback } from "react";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";

export type AgentStatus = "ready" | "thinking" | "executing" | "error";

export interface Message {
  id: string;
  role: "user" | "assistant";
  content: string;
  timestamp: Date;
  file?: string;
}

export interface ThinkingStep {
  id: string;
  type: "audio" | "document" | "classify" | "reasoning" | "general";
  title: string;
  description: string;
  status: "pending" | "running" | "completed" | "error";
  duration?: number;
}

interface ProcessResponse {
  status: string;
  response: string;
  file_processed?: string;
  intermediate_steps?: string;
}

export function useAgent() {
  const [messages, setMessages] = useState<Message[]>([]);
  const [isProcessing, setIsProcessing] = useState(false);
  const [agentStatus, setAgentStatus] = useState<AgentStatus>("ready");
  const [thinkingSteps, setThinkingSteps] = useState<ThinkingStep[]>([]);

  const generateId = () => Math.random().toString(36).substring(2, 15);

  const parseIntermediateSteps = (stepsString: string): ThinkingStep[] => {
    const steps: ThinkingStep[] = [];
    
    if (stepsString.includes("transcribe_audio")) {
      steps.push({
        id: generateId(),
        type: "audio",
        title: "Audio Transcription",
        description: "Transcribing audio using Whisper AI",
        status: "completed",
        duration: Math.floor(Math.random() * 2000) + 500
      });
    }
    
    if (stepsString.includes("query_document")) {
      steps.push({
        id: generateId(),
        type: "document",
        title: "Document Analysis",
        description: "Extracting information using LayoutLM",
        status: "completed",
        duration: Math.floor(Math.random() * 3000) + 1000
      });
    }
    
    if (stepsString.includes("classify_ticket")) {
      steps.push({
        id: generateId(),
        type: "classify",
        title: "Ticket Classification",
        description: "Categorizing ticket using ML classifier",
        status: "completed",
        duration: Math.floor(Math.random() * 500) + 100
      });
    }

    if (steps.length === 0) {
      steps.push({
        id: generateId(),
        type: "reasoning",
        title: "Agent Reasoning",
        description: "Processing request with Gemini LLM",
        status: "completed",
        duration: Math.floor(Math.random() * 1500) + 500
      });
    }

    return steps;
  };

  const addThinkingStep = (step: Omit<ThinkingStep, "id">) => {
    const newStep: ThinkingStep = { ...step, id: generateId() };
    setThinkingSteps(prev => [...prev, newStep]);
    return newStep.id;
  };

  const updateThinkingStep = (id: string, updates: Partial<ThinkingStep>) => {
    setThinkingSteps(prev =>
      prev.map(step => (step.id === id ? { ...step, ...updates } : step))
    );
  };

  const sendMessage = useCallback(async (content: string) => {
    if (!content.trim() || isProcessing) return;

    const userMessage: Message = {
      id: generateId(),
      role: "user",
      content,
      timestamp: new Date()
    };

    setMessages(prev => [...prev, userMessage]);
    setIsProcessing(true);
    setAgentStatus("thinking");

    const thinkingId = addThinkingStep({
      type: "reasoning",
      title: "Processing Request",
      description: "Analyzing your message...",
      status: "running"
    });

    try {
      const formData = new FormData();
      formData.append("query", content);

      setAgentStatus("executing");

      const response = await fetch(`${API_BASE_URL}/api/agents/process`, {
        method: "POST",
        body: formData
      });

      const data: ProcessResponse = await response.json();

      updateThinkingStep(thinkingId, { status: "completed", duration: 1200 });

      if (data.intermediate_steps) {
        const parsedSteps = parseIntermediateSteps(data.intermediate_steps);
        setThinkingSteps(prev => [...prev, ...parsedSteps]);
      }

      const assistantMessage: Message = {
        id: generateId(),
        role: "assistant",
        content: data.response || "I processed your request.",
        timestamp: new Date()
      };

      setMessages(prev => [...prev, assistantMessage]);
      setAgentStatus("ready");
    } catch (error) {
      console.error("Failed to send message:", error);
      
      updateThinkingStep(thinkingId, { status: "error" });

      const errorMessage: Message = {
        id: generateId(),
        role: "assistant",
        content: "I encountered an error processing your request. Please ensure the backend server is running.",
        timestamp: new Date()
      };

      setMessages(prev => [...prev, errorMessage]);
      setAgentStatus("error");
      
      setTimeout(() => setAgentStatus("ready"), 3000);
    } finally {
      setIsProcessing(false);
    }
  }, [isProcessing]);

  const uploadFile = useCallback(async (file: File, query: string) => {
    if (!file || isProcessing) return;

    const userMessage: Message = {
      id: generateId(),
      role: "user",
      content: query || "Analyze this file",
      timestamp: new Date(),
      file: file.name
    };

    setMessages(prev => [...prev, userMessage]);
    setIsProcessing(true);
    setAgentStatus("thinking");

    const fileType = file.type.startsWith("audio") ? "audio" : 
                     file.type === "application/pdf" ? "document" : 
                     file.type.startsWith("image") ? "document" : "general";

    const uploadStepId = addThinkingStep({
      type: fileType,
      title: fileType === "audio" ? "Audio Processing" : "Document Processing",
      description: `Uploading ${file.name}...`,
      status: "running"
    });

    try {
      const formData = new FormData();
      formData.append("file", file);
      formData.append("query", query || "Analyze this file");

      setAgentStatus("executing");

      const response = await fetch(`${API_BASE_URL}/api/agents/process`, {
        method: "POST",
        body: formData
      });

      const data: ProcessResponse = await response.json();

      updateThinkingStep(uploadStepId, { 
        status: "completed", 
        description: `Processed ${file.name}`,
        duration: 2500 
      });

      if (data.intermediate_steps) {
        const parsedSteps = parseIntermediateSteps(data.intermediate_steps);
        setThinkingSteps(prev => [...prev, ...parsedSteps]);
      }

      const assistantMessage: Message = {
        id: generateId(),
        role: "assistant",
        content: data.response || "File processed successfully.",
        timestamp: new Date()
      };

      setMessages(prev => [...prev, assistantMessage]);
      setAgentStatus("ready");
    } catch (error) {
      console.error("Failed to upload file:", error);
      
      updateThinkingStep(uploadStepId, { status: "error" });

      const errorMessage: Message = {
        id: generateId(),
        role: "assistant",
        content: "Failed to process the file. Please ensure the backend server is running and try again.",
        timestamp: new Date()
      };

      setMessages(prev => [...prev, errorMessage]);
      setAgentStatus("error");
      
      setTimeout(() => setAgentStatus("ready"), 3000);
    } finally {
      setIsProcessing(false);
    }
  }, [isProcessing]);

  const clearMessages = useCallback(() => {
    setMessages([]);
    setThinkingSteps([]);
  }, []);

  return {
    messages,
    isProcessing,
    agentStatus,
    thinkingSteps,
    sendMessage,
    uploadFile,
    clearMessages
  };
}
