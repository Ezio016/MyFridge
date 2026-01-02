import { useState, useEffect, useRef } from 'react'
import { Mic, MicOff, Loader } from 'lucide-react'
import styles from './VoiceInput.module.css'

function VoiceInput({ onTranscript, onItemsParsed }) {
  const [isListening, setIsListening] = useState(false)
  const [transcript, setTranscript] = useState('')
  const [error, setError] = useState(null)
  const [isParsing, setIsParsing] = useState(false)
  const recognitionRef = useRef(null)

  useEffect(() => {
    // Check if browser supports speech recognition
    if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
      setError('Voice input not supported in this browser')
      return
    }

    // Initialize speech recognition
    const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition
    const recognition = new SpeechRecognition()
    
    recognition.continuous = false
    recognition.interimResults = true
    recognition.lang = 'en-US'

    recognition.onstart = () => {
      setIsListening(true)
      setError(null)
      setTranscript('')
    }

    recognition.onresult = (event) => {
      let interimTranscript = ''
      let finalTranscript = ''

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcriptPiece = event.results[i][0].transcript
        if (event.results[i].isFinal) {
          finalTranscript += transcriptPiece + ' '
        } else {
          interimTranscript += transcriptPiece
        }
      }

      const currentTranscript = finalTranscript || interimTranscript
      setTranscript(currentTranscript)
      if (onTranscript) onTranscript(currentTranscript)
    }

    recognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error)
      setError(`Error: ${event.error}`)
      setIsListening(false)
    }

    recognition.onend = () => {
      setIsListening(false)
      // If we have a transcript, parse it
      if (transcript.trim()) {
        parseVoiceInput(transcript)
      }
    }

    recognitionRef.current = recognition

    return () => {
      if (recognitionRef.current) {
        recognitionRef.current.abort()
      }
    }
  }, [transcript])

  const parseVoiceInput = async (text) => {
    setIsParsing(true)
    try {
      const response = await fetch('/api/inventory/parse-voice', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text })
      })

      if (!response.ok) throw new Error('Failed to parse voice input')

      const result = await response.json()
      if (onItemsParsed) onItemsParsed(result.items)
    } catch (err) {
      console.error('Parse error:', err)
      setError('Could not parse your input. Try again!')
    } finally {
      setIsParsing(false)
    }
  }

  const toggleListening = () => {
    if (!recognitionRef.current) return

    if (isListening) {
      recognitionRef.current.stop()
    } else {
      recognitionRef.current.start()
    }
  }

  if (error && !isListening) {
    return (
      <div className={styles.error}>
        <MicOff size={16} />
        <span>{error}</span>
      </div>
    )
  }

  return (
    <div className={styles.container}>
      <button
        type="button"
        className={`${styles.micBtn} ${isListening ? styles.listening : ''}`}
        onClick={toggleListening}
        disabled={isParsing}
      >
        {isParsing ? (
          <Loader size={20} className={styles.spinner} />
        ) : (
          <Mic size={20} />
        )}
      </button>
      
      <div className={styles.status}>
        {isParsing ? (
          <span className={styles.parsing}>🧠 Parsing...</span>
        ) : isListening ? (
          <span className={styles.active}>🎤 Listening... Speak now!</span>
        ) : (
          <span className={styles.idle}>Click mic to add items by voice</span>
        )}
      </div>

      {transcript && (
        <div className={styles.transcript}>
          <strong>You said:</strong> "{transcript}"
        </div>
      )}
    </div>
  )
}

export default VoiceInput

