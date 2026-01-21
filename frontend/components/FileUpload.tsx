"use client";

import { useState, useCallback } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { useDropzone } from "react-dropzone";
import { 
  Upload, 
  FileAudio, 
  FileText, 
  Image as ImageIcon,
  X,
  CheckCircle,
  Loader2
} from "lucide-react";

interface FileUploadProps {
  onUpload: (file: File, query: string) => void;
  isProcessing: boolean;
}

type FileType = "audio" | "document" | "image" | "unknown";

interface UploadedFile {
  file: File;
  type: FileType;
  progress: number;
}

export default function FileUpload({ onUpload, isProcessing }: FileUploadProps) {
  const [uploadedFile, setUploadedFile] = useState<UploadedFile | null>(null);
  const [query, setQuery] = useState("");

  const getFileType = (file: File): FileType => {
    const ext = file.name.split(".").pop()?.toLowerCase() || "";
    if (["mp3", "wav", "m4a", "flac", "ogg", "webm"].includes(ext)) return "audio";
    if (["pdf"].includes(ext)) return "document";
    if (["jpg", "jpeg", "png", "bmp", "tiff", "webp"].includes(ext)) return "image";
    return "unknown";
  };

  const getFileIcon = (type: FileType) => {
    switch (type) {
      case "audio": return <FileAudio className="w-6 h-6" />;
      case "document": return <FileText className="w-6 h-6" />;
      case "image": return <ImageIcon className="w-6 h-6" />;
      default: return <FileText className="w-6 h-6" />;
    }
  };

  const getFileColor = (type: FileType) => {
    switch (type) {
      case "audio": return "from-violet-500 to-purple-500";
      case "document": return "from-blue-500 to-cyan-500";
      case "image": return "from-emerald-500 to-teal-500";
      default: return "from-slate-500 to-slate-600";
    }
  };

  const onDrop = useCallback((acceptedFiles: File[]) => {
    const file = acceptedFiles[0];
    if (!file) return;

    const fileType = getFileType(file);
    setUploadedFile({ file, type: fileType, progress: 0 });

    // Simulate upload progress
    let progress = 0;
    const interval = setInterval(() => {
      progress += Math.random() * 30;
      if (progress >= 100) {
        progress = 100;
        clearInterval(interval);
      }
      setUploadedFile(prev => prev ? { ...prev, progress } : null);
    }, 200);
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      "audio/*": [".mp3", ".wav", ".m4a", ".flac", ".ogg", ".webm"],
      "application/pdf": [".pdf"],
      "image/*": [".jpg", ".jpeg", ".png", ".bmp", ".tiff", ".webp"]
    },
    multiple: false,
    disabled: isProcessing
  });

  const handleSubmit = () => {
    if (!uploadedFile || isProcessing) return;
    onUpload(uploadedFile.file, query || "Analyze this file");
    setUploadedFile(null);
    setQuery("");
  };

  const handleRemove = () => {
    setUploadedFile(null);
    setQuery("");
  };

  return (
    <div className="rounded-3xl backdrop-blur-xl bg-slate-900/40 border border-white/10 p-4">
      <h3 className="text-sm font-medium text-slate-300 mb-3 flex items-center gap-2">
        <Upload className="w-4 h-4 text-violet-400" />
        File Upload
      </h3>

      <AnimatePresence mode="wait">
        {!uploadedFile ? (
          <motion.div
            key="dropzone"
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            {...(({ onAnimationStart, onDragStart, onDrag, onDragEnd, ...rest }) => rest)(getRootProps())}
            className={`relative border-2 border-dashed rounded-2xl p-6 text-center cursor-pointer transition-all ${
              isDragActive
                ? "border-violet-500 bg-violet-500/10"
                : "border-white/10 hover:border-violet-500/50 hover:bg-white/5"
            } ${isProcessing ? "opacity-50 cursor-not-allowed" : ""}`}
          >
            <input {...getInputProps()} />
            
            <motion.div
              animate={isDragActive ? { scale: 1.1 } : { scale: 1 }}
              className="w-12 h-12 mx-auto mb-3 rounded-2xl bg-gradient-to-br from-violet-600/20 to-blue-600/20 flex items-center justify-center"
            >
              <Upload className={`w-6 h-6 ${isDragActive ? "text-violet-400" : "text-slate-400"}`} />
            </motion.div>

            <p className="text-sm text-slate-300 mb-1">
              {isDragActive ? "Drop file here" : "Drag & drop a file"}
            </p>
            <p className="text-xs text-slate-500">
              Audio, PDF, or Images
            </p>

            {/* Supported formats */}
            <div className="flex justify-center gap-2 mt-4">
              <span className="px-2 py-1 rounded-full bg-violet-500/10 text-violet-400 text-xs">Audio</span>
              <span className="px-2 py-1 rounded-full bg-blue-500/10 text-blue-400 text-xs">PDF</span>
              <span className="px-2 py-1 rounded-full bg-emerald-500/10 text-emerald-400 text-xs">Image</span>
            </div>
          </motion.div>
        ) : (
          <motion.div
            key="uploaded"
            initial={{ opacity: 0, y: 10 }}
            animate={{ opacity: 1, y: 0 }}
            exit={{ opacity: 0, y: -10 }}
            className="space-y-3"
          >
            {/* File Preview */}
            <div className="flex items-center gap-3 p-3 rounded-xl bg-slate-800/50 border border-white/5">
              <div className={`w-10 h-10 rounded-xl bg-gradient-to-br ${getFileColor(uploadedFile.type)} flex items-center justify-center text-white`}>
                {getFileIcon(uploadedFile.type)}
              </div>
              <div className="flex-1 min-w-0">
                <p className="text-sm text-white truncate">{uploadedFile.file.name}</p>
                <p className="text-xs text-slate-400">
                  {(uploadedFile.file.size / 1024 / 1024).toFixed(2)} MB
                </p>
              </div>
              {uploadedFile.progress >= 100 ? (
                <CheckCircle className="w-5 h-5 text-emerald-500" />
              ) : (
                <Loader2 className="w-5 h-5 text-violet-500 animate-spin" />
              )}
              <motion.button
                whileHover={{ scale: 1.1 }}
                whileTap={{ scale: 0.9 }}
                onClick={handleRemove}
                className="p-1 rounded-lg hover:bg-white/10 text-slate-400 hover:text-white transition-colors"
              >
                <X className="w-4 h-4" />
              </motion.button>
            </div>

            {/* Progress Bar */}
            {uploadedFile.progress < 100 && (
              <div className="h-1 bg-slate-700/50 rounded-full overflow-hidden">
                <motion.div
                  initial={{ width: 0 }}
                  animate={{ width: `${uploadedFile.progress}%` }}
                  className="h-full bg-gradient-to-r from-violet-500 to-blue-500 rounded-full"
                />
              </div>
            )}

            {/* Query Input */}
            {uploadedFile.progress >= 100 && (
              <motion.div
                initial={{ opacity: 0, height: 0 }}
                animate={{ opacity: 1, height: "auto" }}
                className="space-y-3"
              >
                <input
                  type="text"
                  value={query}
                  onChange={(e) => setQuery(e.target.value)}
                  placeholder={
                    uploadedFile.type === "audio" 
                      ? "Transcribe this audio..." 
                      : "Ask a question about this file..."
                  }
                  className="w-full px-4 py-2 rounded-xl bg-slate-800/50 border border-white/10 text-white placeholder-slate-500 text-sm outline-none focus:border-violet-500/50 transition-colors"
                />
                <motion.button
                  whileHover={{ scale: 1.02 }}
                  whileTap={{ scale: 0.98 }}
                  onClick={handleSubmit}
                  disabled={isProcessing}
                  className="w-full py-2.5 rounded-xl bg-gradient-to-r from-violet-600 to-blue-600 text-white font-medium text-sm disabled:opacity-50 disabled:cursor-not-allowed transition-opacity"
                >
                  {isProcessing ? (
                    <span className="flex items-center justify-center gap-2">
                      <Loader2 className="w-4 h-4 animate-spin" />
                      Processing...
                    </span>
                  ) : (
                    "Process File"
                  )}
                </motion.button>
              </motion.div>
            )}
          </motion.div>
        )}
      </AnimatePresence>
    </div>
  );
}
