import { useEffect, useRef, useState } from "react"
import { motion, AnimatePresence } from "framer-motion"

export default function ChatUI() {
  const [messages, setMessages] = useState([])
  const [input, setInput] = useState("")
  const [loading, setLoading] = useState(false)
  const [isOnline, setIsOnline] = useState(false)
  const bottomRef = useRef(null)


// const RASA_URL = window.location.origin.replace("4173", "5005")
// const RASA_URL = "http://localhost:5005"
  const RASA_URL = "http://13.48.85.237:5005"

  // Test Rasa connection on mount
  useEffect(() => {
    const testConnection = async () => {
      try {
       const res = await fetch(`${RASA_URL}/status`)
        setIsOnline(res.ok)
      } catch {
        setIsOnline(false)
      }
    }
    testConnection()
    const interval = setInterval(testConnection, 10000) // Check every 10s
    return () => clearInterval(interval)
  }, [])

  useEffect(() => {
    const saved = localStorage.getItem("chat")
    if (saved) setMessages(JSON.parse(saved))
  }, [])

  useEffect(() => {
    localStorage.setItem("chat", JSON.stringify(messages))
    bottomRef.current?.scrollIntoView({ behavior: "smooth" })
  }, [messages])

  function now() {
    return new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" })
  }

  async function sendMessage() {
    if (!input.trim()) return

    const userMessage = {
      role: "user",
      text: input,
      time: now(),
    }

    setMessages(prev => [...prev, userMessage])
    setInput("")
    setLoading(true)

    try {
      // Fixed: Use localhost instead of rasa for browser access
      const res = await fetch(`${RASA_URL}/webhooks/rest/webhook`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ sender: "user", message: input }),
      })

      if (!res.ok) throw new Error("Network error")

      const data = await res.json()

      for (let msg of data) {
        await new Promise(r => setTimeout(r, 600))
        setMessages(prev => [
          ...prev,
          { role: "bot", text: msg.text || "...", time: now() },
        ])
      }
      setIsOnline(true)
    } catch (error) {
      setIsOnline(false)
      setMessages(prev => [
        ...prev,
        { 
          role: "bot", 
          text: "⚠️ Connection error. Please ensure Rasa is running on port 5005.", 
          time: now() 
        },
      ])
    }

    setLoading(false)
  }

  function grouped(index) {
    if (index === 0) return false
    return messages[index].role === messages[index - 1].role
  }

  function clearChat() {
    setMessages([])
    localStorage.removeItem("chat")
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-slate-900 via-red-950 to-slate-900 flex justify-center items-center p-6 relative overflow-hidden">
      
      {/* Animated background elements */}
      <div className="absolute inset-0 overflow-hidden pointer-events-none">
        <div className="absolute w-96 h-96 bg-red-500/10 rounded-full blur-3xl -top-48 -left-48 animate-pulse" />
        <div className="absolute w-96 h-96 bg-orange-500/10 rounded-full blur-3xl -bottom-48 -right-48 animate-pulse delay-1000" />
      </div>

      <div className="w-full max-w-md h-[700px] bg-white/5 backdrop-blur-2xl rounded-3xl border border-white/20 shadow-2xl flex flex-col overflow-hidden relative z-10">

        {/* Header */}
        <div className="p-5 border-b border-white/10 bg-gradient-to-r from-red-600/20 to-orange-600/20">
          <div className="flex justify-between items-center">
            <div>
              <h1 className="text-white font-bold text-lg flex items-center gap-2">
                <span className="text-2xl">🚨</span>
                Mansi – Crisis Assistant
              </h1>
              <p className="text-white/60 text-xs mt-1">Emergency Response System</p>
            </div>
            <div className="flex flex-col items-end gap-1">
              <span className={`text-xs flex items-center gap-2 px-3 py-1 rounded-full ${
                isOnline 
                  ? 'bg-green-500/20 text-green-400' 
                  : 'bg-red-500/20 text-red-400'
              }`}>
                <span className={`w-2 h-2 rounded-full ${isOnline ? 'bg-green-400' : 'bg-red-400'} animate-pulse`} />
                {isOnline ? 'Online' : 'Offline'}
              </span>
              <button 
                onClick={clearChat}
                className="text-white/40 hover:text-white/80 text-xs transition"
              >
                Clear Chat
              </button>
            </div>
          </div>
        </div>

        {/* Messages */}
        <div className="flex-1 overflow-y-auto p-5 space-y-3 custom-scroll">
          {messages.length === 0 && (
            <motion.div 
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              className="text-center text-white/60 mt-20 space-y-4"
            >
              <div className="text-5xl mb-4">🆘</div>
              <p className="text-lg font-semibold text-white">Emergency Assistance Available 24/7</p>
              <div className="space-y-2 text-sm">
                <p className="text-white/40">I can help with:</p>
                <div className="flex flex-wrap gap-2 justify-center">
                  <span className="px-3 py-1 bg-red-500/20 rounded-full text-red-300 text-xs">🔥 Fire</span>
                  <span className="px-3 py-1 bg-blue-500/20 rounded-full text-blue-300 text-xs">🌊 Flood</span>
                  <span className="px-3 py-1 bg-orange-500/20 rounded-full text-orange-300 text-xs">⚡ Earthquake</span>
                  <span className="px-3 py-1 bg-purple-500/20 rounded-full text-purple-300 text-xs">🏥 Medical</span>
                </div>
              </div>
            </motion.div>
          )}

          <AnimatePresence>
            {messages.map((msg, i) => (
              <motion.div
                key={i}
                initial={{ opacity: 0, x: msg.role === "user" ? 20 : -20, scale: 0.95 }}
                animate={{ opacity: 1, x: 0, scale: 1 }}
                exit={{ opacity: 0, scale: 0.9 }}
                transition={{ duration: 0.3, type: "spring", stiffness: 200 }}
                className={`flex ${msg.role === "user" ? "justify-end" : "justify-start"}`}
              >
                <div className="flex items-end gap-2 max-w-[85%]">
                  {msg.role === "bot" && (
                    <div className="w-8 h-8 rounded-full bg-gradient-to-br from-red-500 to-orange-500 flex items-center justify-center text-white text-sm font-bold mb-1 flex-shrink-0">
                      M
                    </div>
                  )}
                  <div
                    className={`px-4 py-3 rounded-2xl leading-relaxed shadow-lg
                    ${msg.role === "user"
                        ? "bg-gradient-to-br from-indigo-600 to-indigo-700 text-white rounded-br-sm"
                        : "bg-white/10 backdrop-blur-sm text-white border border-white/10 rounded-bl-sm"}
                    ${grouped(i) ? (msg.role === "user" ? "rounded-tr-sm" : "rounded-tl-sm") : ""}
                  `}
                  >
                    <div className="whitespace-pre-wrap break-words">{msg.text}</div>
                    <div className="text-[10px] opacity-50 mt-2 text-right">
                      {msg.time}
                    </div>
                  </div>
                </div>
              </motion.div>
            ))}
          </AnimatePresence>

          {/* Enhanced typing indicator */}
          {loading && (
            <motion.div 
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              className="flex items-center gap-3 ml-2"
            >
              <div className="w-8 h-8 rounded-full bg-gradient-to-br from-red-500 to-orange-500 flex items-center justify-center text-white text-sm font-bold">
                M
              </div>
              <div className="flex items-center gap-1 bg-white/10 backdrop-blur-sm px-4 py-3 rounded-2xl rounded-bl-sm">
                <span className="typing-dot" />
                <span className="typing-dot" />
                <span className="typing-dot" />
              </div>
            </motion.div>
          )}

          <div ref={bottomRef} />
        </div>

        {/* Input area */}
        <div className="p-5 border-t border-white/10 bg-black/20 backdrop-blur-sm">
          <div className="flex gap-3 items-end">
            <div className="flex-1 relative">
              <textarea
                value={input}
                onChange={e => setInput(e.target.value)}
                onKeyDown={e => {
                  if (e.key === "Enter" && !e.shiftKey) {
                    e.preventDefault()
                    sendMessage()
                  }
                }}
                placeholder="Describe your emergency..."
                rows={1}
                className="w-full bg-white/5 text-white px-4 py-3 rounded-2xl outline-none border border-white/20 focus:border-red-500/50 focus:bg-white/10 transition resize-none placeholder:text-white/40"
                style={{ minHeight: "48px", maxHeight: "120px" }}
                onInput={(e) => {
                  e.target.style.height = "48px"
                  e.target.style.height = e.target.scrollHeight + "px"
                }}
              />
            </div>
            <button
              onClick={sendMessage}
              disabled={!input.trim() || loading}
              className="bg-gradient-to-r from-red-600 to-orange-600 hover:from-red-500 hover:to-orange-500 disabled:from-gray-600 disabled:to-gray-700 disabled:cursor-not-allowed transition-all px-6 py-3 rounded-2xl text-white font-semibold shadow-lg hover:shadow-red-500/50 active:scale-95 flex items-center gap-2 h-12"
            >
              <span>Send</span>
              <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M14 5l7 7m0 0l-7 7m7-7H3" />
              </svg>
            </button>
          </div>
        </div>
      </div>
    </div>
  )
}