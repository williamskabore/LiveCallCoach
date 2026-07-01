import React, { useReducer, createContext, useContext, useEffect, useRef, useCallback } from 'react'

// Types
interface TranscriptEntry {
  id: string
  text: string
  speaker: string
  timestamp: number
  confidence: number
}

interface Suggestion {
  id: string
  text: string
  priority: 'high' | 'medium' | 'low'
  category: string
  timestamp: number
  expiresAt: number
}

interface KBEntry {
  title: string
  content: string
  category: string
  tags: string[]
}

interface CallMetrics {
  aht: number
  sentimentScore: number
  complianceFlag: boolean
  callDuration: number
  activeSuggestions: number
}

interface AppState {
  isConnected: boolean
  isRecording: boolean
  transcripts: TranscriptEntry[]
  suggestions: Suggestion[]
  kbResults: KBEntry[]
  metrics: CallMetrics
  error: string | null
  kbSearchQuery: string
}

type AppAction =
  | { type: 'SET_CONNECTED'; payload: boolean }
  | { type: 'SET_RECORDING'; payload: boolean }
  | { type: 'ADD_TRANSCRIPT'; payload: TranscriptEntry }
  | { type: 'ADD_SUGGESTION'; payload: Suggestion }
  | { type: 'REMOVE_SUGGESTION'; payload: string }
  | { type: 'SET_KB_RESULTS'; payload: KBEntry[] }
  | { type: 'SET_METRICS'; payload: Partial<CallMetrics> }
  | { type: 'SET_ERROR'; payload: string | null }
  | { type: 'SET_KB_QUERY'; payload: string }

// Context
interface AppContextType {
  state: AppState
  dispatch: React.Dispatch<AppAction>
  startRecording: () => void
  stopRecording: () => void
  searchKB: (query: string) => void
  wsStatus: string
}

const AppContext = createContext<AppContextType | null>(null)

// Reducer
const initialState: AppState = {
  isConnected: false,
  isRecording: false,
  transcripts: [],
  suggestions: [],
  kbResults: [],
  metrics: {
    aht: 0,
    sentimentScore: 0,
    complianceFlag: false,
    callDuration: 0,
    activeSuggestions: 0
  },
  error: null,
  kbSearchQuery: ''
}

function appReducer(state: AppState, action: AppAction): AppState {
  switch (action.type) {
    case 'SET_CONNECTED':
      return { ...state, isConnected: action.payload }
    
    case 'SET_RECORDING':
      return { ...state, isRecording: action.payload }
    
    case 'ADD_TRANSCRIPT':
      return {
        ...state,
        transcripts: [...state.transcripts, action.payload].slice(-50) // Keep last 50 entries
      }
    
    case 'ADD_SUGGESTION':
      return {
        ...state,
        suggestions: [...state.suggestions, action.payload].slice(-10) // Keep last 10 suggestions
      }
    
    case 'REMOVE_SUGGESTION':
      return {
        ...state,
        suggestions: state.suggestions.filter(s => s.id !== action.payload)
      }
    
    case 'SET_KB_RESULTS':
      return { ...state, kbResults: action.payload }
    
    case 'SET_METRICS':
      return {
        ...state,
        metrics: { ...state.metrics, ...action.payload }
      }
    
    case 'SET_ERROR':
      return { ...state, error: action.payload }
    
    case 'SET_KB_QUERY':
      return { ...state, kbSearchQuery: action.payload }
    
    default:
      return state
  }
}

// Custom hooks
function useWebSocket(url: string) {
  const wsRef = useRef<WebSocket | null>(null)
  const reconnectTimeoutRef = useRef<number>()
  const { dispatch } = useContext(AppContext)!

  const connect = useCallback(() => {
    if (wsRef.current?.readyState === WebSocket.OPEN) return

    const ws = new WebSocket(url)
    wsRef.current = ws

    ws.onopen = () => {
      console.log('WebSocket connected')
      dispatch({ type: 'SET_CONNECTED', payload: true })
    }

    ws.onmessage = (event) => {
      try {
        const message = JSON
