'use client';

import React, { useState, useRef, useEffect, useCallback } from 'react';
import styles from './RainmakerCloud.module.css';

// ── Types ──

interface CommlogEntry {
  channel?: string;
  direction?: string;
  content?: string;
  ts?: string | number;
  sender?: string;
}

interface ChatMessage {
  role: 'user' | 'assistant';
  content: string;
}

// ── Constants ──

const CHANNEL_LABELS: Record<string, string> = {
  whatsapp: 'WA',
  telegram: 'TG',
  voice: 'VOICE',
  email: 'EMAIL',
  system: 'SYS',
  discord: 'DC',
  widget: 'CHAT',
};

const CHANNEL_STYLE_MAP: Record<string, string> = {
  whatsapp: styles.chWhatsapp,
  telegram: styles.chTelegram,
  voice: styles.chVoice,
  email: styles.chEmail,
  system: styles.chSystem,
  discord: styles.chDiscord,
  widget: styles.chWidget,
};

const ELEVENLABS_AGENT_ID = 'agent_0701kgrw2hegeh3r9fyna0ct0eje';

// ── Helpers ──

function escHtml(str: string): string {
  const el = typeof document !== 'undefined' ? document.createElement('span') : null;
  if (el) {
    el.textContent = str;
    return el.innerHTML;
  }
  return str.replace(/&/g, '&amp;').replace(/</g, '&lt;').replace(/>/g, '&gt;');
}

function formatTime(ts?: string | number): string {
  if (!ts) return '';
  const d = new Date(typeof ts === 'number' ? ts * 1000 : ts);
  if (isNaN(d.getTime())) return '';
  const now = new Date();
  const hh = String(d.getHours()).padStart(2, '0');
  const mm = String(d.getMinutes()).padStart(2, '0');
  const time = `${hh}:${mm}`;
  if (d.toDateString() !== now.toDateString()) {
    const dd = String(d.getDate()).padStart(2, '0');
    const mo = String(d.getMonth() + 1).padStart(2, '0');
    return `${dd}/${mo} ${time}`;
  }
  return time;
}

// ── Lightning SVG (static, extracted for clarity) ──

function LightningSvg({ className }: { className: string }) {
  return (
    <svg viewBox="0 0 100 100" className={className}>
      <path d="M50,5 L44,22 L56,38 L40,55 L52,70 L35,95" fill="none" stroke="rgba(255,255,255,0.9)" strokeWidth="2" strokeLinejoin="miter" strokeLinecap="round" />
      <path d="M44,22 L30,28 L20,44" fill="none" stroke="rgba(255,255,255,0.7)" strokeWidth="1.2" strokeLinejoin="miter" strokeLinecap="round" />
      <path d="M30,28 L26,18" fill="none" stroke="rgba(255,255,255,0.5)" strokeWidth="0.8" strokeLinejoin="miter" strokeLinecap="round" />
      <path d="M56,38 L72,44 L80,60" fill="none" stroke="rgba(255,255,255,0.7)" strokeWidth="1.2" strokeLinejoin="miter" strokeLinecap="round" />
      <path d="M72,44 L82,36" fill="none" stroke="rgba(255,255,255,0.5)" strokeWidth="0.8" strokeLinejoin="miter" strokeLinecap="round" />
      <path d="M40,55 L28,62 L22,80" fill="none" stroke="rgba(255,255,255,0.6)" strokeWidth="1" strokeLinejoin="miter" strokeLinecap="round" />
      <path d="M52,70 L64,78 L62,95" fill="none" stroke="rgba(255,255,255,0.6)" strokeWidth="1" strokeLinejoin="miter" strokeLinecap="round" />
    </svg>
  );
}

// ── Message Bubble ──

interface MsgProps {
  entry: CommlogEntry;
  isTranscript?: boolean;
}

function MessageBubble({ entry, isTranscript }: MsgProps) {
  const isUser = entry.direction === 'in';
  const ch = (entry.channel || 'system').toLowerCase();
  const badge = CHANNEL_LABELS[ch] || ch.toUpperCase().substring(0, 4);
  const badgeClass = CHANNEL_STYLE_MAP[ch] || '';

  let msgClass = isUser ? styles.chatMsgUser : styles.chatMsgAgent;
  if (isTranscript) {
    msgClass += ' ' + (isUser ? styles.chatMsgTranscriptUser : styles.chatMsgTranscript);
  }

  return (
    <div className={msgClass}>
      <div className={`${styles.msgMeta} ${isUser ? styles.msgMetaUser : ''}`}>
        <span className={`${styles.chBadge} ${badgeClass}`}>{escHtml(badge)}</span>
        <span className={styles.msgTime}>{escHtml(formatTime(entry.ts))}</span>
      </div>
      <div className={styles.msgContent}>{entry.content || ''}</div>
    </div>
  );
}

// ── Main Widget ──

export default function RainmakerCloud() {
  // State
  const [drawerOpen, setDrawerOpen] = useState(true);
  const [chatOpen, setChatOpen] = useState(true);
  const [callActive, setCallActive] = useState(false);
  const [callConnecting, setCallConnecting] = useState(false);
  const [messages, setMessages] = useState<CommlogEntry[]>([]);
  const [inputText, setInputText] = useState('');
  const [sending, setSending] = useState(false);

  // Refs
  const chatMessagesRef = useRef<HTMLDivElement>(null);
  const conversationRef = useRef<any>(null);
  const commlogLoadedRef = useRef(false);
  const sseRef = useRef<EventSource | null>(null);
  const recentEmitsRef = useRef<Array<{ key: string; ts: number }>>([]);
  const chatHistoryRef = useRef<ChatMessage[]>([]);

  // ── Auto-scroll on new messages ──
  useEffect(() => {
    if (chatMessagesRef.current) {
      chatMessagesRef.current.scrollTop = chatMessagesRef.current.scrollHeight;
    }
  }, [messages]);

  // ── SSE connection ──
  const connectSSE = useCallback(() => {
    if (sseRef.current) return;
    try {
      const es = new EventSource('/api/openclaw/ui-sync/stream');
      sseRef.current = es;

      es.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);
          if (payload.type === 'commlog' && payload.data) {
            const d = payload.data as CommlogEntry;
            // Dedup: skip if we recently emitted this message
            const dedupKey = `${d.channel || 'widget'}:${d.direction || 'in'}:${(d.content || '').substring(0, 80)}`;
            const now = Date.now();
            const isDuplicate = recentEmitsRef.current.some(
              (e) => e.key === dedupKey && now - e.ts < 10000
            );
            if (!isDuplicate) {
              setMessages((prev) => [...prev, d]);
            }
          }
        } catch {
          // Ignore malformed SSE data
        }
      };

      es.onerror = () => {
        es.close();
        sseRef.current = null;
        // Reconnect after 5s
        setTimeout(() => {
          connectSSE();
        }, 5000);
      };
    } catch {
      sseRef.current = null;
    }
  }, []);

  // ── Load COMMLOG history ──
  const loadCommlogHistory = useCallback(async () => {
    if (commlogLoadedRef.current) return;
    commlogLoadedRef.current = true;

    try {
      let res = await fetch('/api/openclaw/commlog/recent?count=50');
      if (!res.ok) throw new Error(`Status ${res.status}`);
      let data = await res.json();
      let entries: CommlogEntry[] = data.entries || [];

      // Ring buffer empty (after restart) — fall back to DB
      if (entries.length === 0) {
        res = await fetch('/api/openclaw/commlog/query?limit=50&hours=24');
        if (res.ok) {
          data = await res.json();
          entries = data.entries || [];
        }
      }

      // API returns newest-first; reverse for chronological
      entries.reverse();
      setMessages(entries);
    } catch (e) {
      console.error('[rainmaker] COMMLOG fetch error:', e);
      setMessages([]);
    }
  }, []);

  // ── Boot: load history + SSE on mount (widget starts open) ──
  useEffect(() => {
    loadCommlogHistory();
    connectSSE();
    return () => {
      sseRef.current?.close();
    };
  }, [loadCommlogHistory, connectSSE]);

  // ── COMMLOG emit ──
  const emitToCommlog = useCallback((direction: string, content: string, channel = 'widget', contentType = 'text') => {
    if (!content?.trim()) return;
    const trimmed = content.trim();

    // Track for dedup
    const dedupKey = `${channel}:${direction}:${trimmed.substring(0, 80)}`;
    recentEmitsRef.current.push({ key: dedupKey, ts: Date.now() });
    // Prune old entries
    const now = Date.now();
    recentEmitsRef.current = recentEmitsRef.current
      .filter((e) => now - e.ts < 10000)
      .slice(-20);

    fetch('/api/openclaw/commlog/emit', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        channel,
        direction,
        sender: direction === 'out' ? 'rainmaker' : 'user',
        recipient: direction === 'out' ? 'user' : 'rainmaker',
        content: trimmed,
        content_type: contentType,
      }),
    }).catch((e) => console.warn('[rainmaker] COMMLOG emit error:', e));
  }, []);

  // ── Toggle chat ──
  const toggleChat = useCallback(() => {
    setChatOpen((prev) => {
      const next = !prev;
      if (next) {
        loadCommlogHistory();
        connectSSE();
      }
      return next;
    });
  }, [loadCommlogHistory, connectSSE]);

  // ── Send chat message ──
  const sendChatMessage = useCallback(async () => {
    const text = inputText.trim();
    if (!text || sending) return;

    setInputText('');
    setSending(true);

    // Add user message
    const userEntry: CommlogEntry = {
      direction: 'in',
      channel: 'widget',
      content: text,
      ts: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, userEntry]);
    chatHistoryRef.current.push({ role: 'user', content: text });

    // Emit to COMMLOG
    emitToCommlog('in', text, 'widget');

    // Add typing indicator
    const typingEntry: CommlogEntry = {
      direction: 'out',
      channel: 'widget',
      content: 'Thinking...',
      ts: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, typingEntry]);

    try {
      const res = await fetch('/api/openclaw/llm/v1/chat/completions', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          model: 'auto',
          messages: chatHistoryRef.current.slice(-20),
        }),
      });

      if (!res.ok) throw new Error(`Error ${res.status}`);
      const data = await res.json();
      const reply = data.choices?.[0]?.message?.content || 'No response.';

      // Remove typing indicator, add real reply
      setMessages((prev) => {
        const filtered = prev.filter((m) => m !== typingEntry);
        return [
          ...filtered,
          {
            direction: 'out',
            channel: 'widget',
            content: reply,
            ts: new Date().toISOString(),
          },
        ];
      });

      chatHistoryRef.current.push({ role: 'assistant', content: reply });
      emitToCommlog('out', reply, 'widget');
    } catch (e: any) {
      // Remove typing, add error
      setMessages((prev) => {
        const filtered = prev.filter((m) => m !== typingEntry);
        return [
          ...filtered,
          {
            direction: 'out',
            channel: 'widget',
            content: `Error: ${e.message}`,
            ts: new Date().toISOString(),
          },
        ];
      });
    } finally {
      setSending(false);
    }
  }, [inputText, sending, emitToCommlog]);

  // ── Voice call ──
  // SDK onMessage: { message: string, source: 'user' | 'ai' }
  const handleTranscriptMessage = useCallback((props: { message: string; source: 'user' | 'ai' }) => {
    if (!props?.message?.trim()) return;

    const direction: 'in' | 'out' = props.source === 'user' ? 'in' : 'out';

    // Auto-open chat
    setChatOpen(true);
    if (!commlogLoadedRef.current) {
      loadCommlogHistory();
    }
    connectSSE();

    const entry: CommlogEntry = {
      direction,
      channel: 'voice',
      content: props.message.trim(),
      ts: new Date().toISOString(),
    };
    setMessages((prev) => [...prev, entry]);

    emitToCommlog(direction, props.message.trim(), 'voice', 'voice_transcript');
  }, [loadCommlogHistory, connectSSE, emitToCommlog]);

  const startCall = useCallback(async () => {
    setCallConnecting(true);

    // Auto-open chat
    if (!chatOpen) {
      setChatOpen(true);
      loadCommlogHistory();
      connectSSE();
    }

    try {
      // Dynamic import of ElevenLabs SDK
      const { Conversation } = await import('@11labs/client');

      setMessages((prev) => [
        ...prev,
        { direction: 'out', channel: 'voice', content: 'Call started...', ts: new Date().toISOString() },
      ]);

      const conv = await Conversation.startSession({
        agentId: ELEVENLABS_AGENT_ID,
        connectionType: 'websocket',
        onConnect: () => {
          setCallConnecting(false);
          setCallActive(true);
        },
        onDisconnect: () => {
          setMessages((prev) => [
            ...prev,
            { direction: 'out', channel: 'voice', content: 'Call ended.', ts: new Date().toISOString() },
          ]);
          setCallActive(false);
          setCallConnecting(false);
          conversationRef.current = null;
        },
        onMessage: (props) => {
          handleTranscriptMessage(props);
        },
        onError: (message, context) => {
          console.error('[rainmaker] ElevenLabs error:', message, context);
          setCallActive(false);
          setCallConnecting(false);
          conversationRef.current = null;
        },
      });

      conversationRef.current = conv;
    } catch (err: any) {
      console.error('[rainmaker] startSession error:', err);
      setCallConnecting(false);
    }
  }, [chatOpen, loadCommlogHistory, connectSSE, handleTranscriptMessage]);

  const endCall = useCallback(() => {
    if (conversationRef.current?.endSession) {
      conversationRef.current.endSession();
    }
    setCallActive(false);
    setCallConnecting(false);
    conversationRef.current = null;
  }, []);

  const toggleCall = useCallback(() => {
    if (!callActive && !callConnecting) {
      startCall();
    } else {
      endCall();
    }
  }, [callActive, callConnecting, startCall, endCall]);

  // ── Close chat on outside click ──
  const containerRef = useRef<HTMLDivElement>(null);
  const chatPopupRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(e: MouseEvent) {
      if (
        chatOpen &&
        chatPopupRef.current &&
        containerRef.current &&
        !chatPopupRef.current.contains(e.target as Node) &&
        !containerRef.current.contains(e.target as Node)
      ) {
        setChatOpen(false);
      }
    }
    document.addEventListener('click', handleClickOutside);
    return () => document.removeEventListener('click', handleClickOutside);
  }, [chatOpen]);

  // ── Build class names ──
  const containerClasses = [
    styles.container,
    drawerOpen && styles.containerActive,
    callActive && styles.containerCalling,
  ]
    .filter(Boolean)
    .join(' ');

  const chatPopupClasses = [
    styles.chatPopup,
    chatOpen && styles.chatPopupOpen,
  ]
    .filter(Boolean)
    .join(' ');

  // ── Render ──
  return (
    <>
      {/* Cloud + Drawer */}
      <div ref={containerRef} className={containerClasses}>
        {/* Drawer */}
        <div className={styles.drawer}>
          <button
            className={styles.drawerBtn}
            onClick={(e) => { e.stopPropagation(); window.location.href = '/rainmaker'; }}
          >
            Agent Page
          </button>
          <button
            className={styles.drawerBtnPrimary}
            disabled={callConnecting}
            onClick={(e) => { e.stopPropagation(); toggleCall(); }}
          >
            {callConnecting ? 'Connecting...' : callActive ? 'End Call' : 'Call'}
          </button>
          <button
            className={styles.drawerBtnChat}
            title="Chat"
            onClick={(e) => { e.stopPropagation(); toggleChat(); }}
          >
            {chatOpen ? '\u25BC' : '\u25B2'}
          </button>
        </div>

        {/* Cloud */}
        <div
          className={styles.cloud}
          onClick={() => setDrawerOpen((p) => !p)}
        >
          <div className={styles.cloudCore} />
          <div className={styles.lightningContainer}>
            <LightningSvg className={styles.lightningSvg} />
          </div>
          <div className={styles.rain}>
            {[0, 1, 2, 3, 4].map((i) => (
              <div key={i} className={styles.drop} />
            ))}
          </div>
        </div>
      </div>

      {/* Chat Popup */}
      <div ref={chatPopupRef} className={chatPopupClasses}>
        <div className={styles.chatHeader}>
          <span className={styles.chatTitle}>RAINMAKER</span>
          <button className={styles.chatClose} onClick={toggleChat}>
            &times;
          </button>
        </div>

        <div ref={chatMessagesRef} className={styles.chatMessages}>
          {messages.length === 0 ? (
            <div className={styles.chatEmpty}>No recent communications.</div>
          ) : (
            messages.map((entry, i) => (
              <MessageBubble
                key={`${entry.ts}-${i}`}
                entry={entry}
                isTranscript={entry.channel === 'voice'}
              />
            ))
          )}
        </div>

        <div className={styles.chatInputRow}>
          <input
            className={styles.chatInput}
            type="text"
            placeholder="Message..."
            autoComplete="off"
            value={inputText}
            onChange={(e) => setInputText(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendChatMessage();
              }
            }}
          />
          <button
            className={styles.chatSend}
            disabled={sending || !inputText.trim()}
            onClick={sendChatMessage}
          >
            Send
          </button>
        </div>
      </div>
    </>
  );
}
