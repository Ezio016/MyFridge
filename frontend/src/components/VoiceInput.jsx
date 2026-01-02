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
    
    recognition.continuous = true  // Keep listening
    recognition.interimResults = true
    recognition.lang = 'en-US'
    recognition.maxAlternatives = 1

    let finalTranscriptText = ''

    recognition.onstart = () => {
      setIsListening(true)
      setError(null)
      setTranscript('')
      finalTranscriptText = ''
    }

    recognition.onresult = (event) => {
      let interimTranscript = ''

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcriptPiece = event.results[i][0].transcript
        if (event.results[i].isFinal) {
          finalTranscriptText += transcriptPiece + ' '
        } else {
          interimTranscript += transcriptPiece
        }
      }

      const currentTranscript = finalTranscriptText + interimTranscript
      setTranscript(currentTranscript)
      if (onTranscript) onTranscript(currentTranscript)
    }

    recognition.onerror = (event) => {
      console.error('Speech recognition error:', event.error)
      if (event.error !== 'aborted') {
        setError(`Error: ${event.error}`)
      }
      setIsListening(false)
    }

    recognition.onend = () => {
      setIsListening(false)
      // If we have a transcript, parse it
      if (finalTranscriptText.trim()) {
        parseVoiceInput(finalTranscriptText)
      }
    }

    recognitionRef.current = recognition

    return () => {
      if (recognitionRef.current) {
        try {
          recognitionRef.current.abort()
        } catch (e) {
          // Ignore abort errors
        }
      }
    }
  }, [])

  const parseVoiceInput = async (text) => {
    setIsParsing(true)
    const startTime = Date.now()
    
    try {
      // Add timeout for slow responses
      const controller = new AbortController()
      const timeoutId = setTimeout(() => controller.abort(), 15000) // 15 sec timeout

      const response = await fetch('/api/inventory/parse-voice', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ text }),
        signal: controller.signal
      })

      clearTimeout(timeoutId)

      if (!response.ok) throw new Error('Failed to parse voice input')

      const result = await response.json()
      const elapsed = ((Date.now() - startTime) / 1000).toFixed(1)
      console.log(`✅ Parsed in ${elapsed}s`)
      
      if (onItemsParsed) onItemsParsed(result.items)
    } catch (err) {
      if (err.name === 'AbortError') {
        setError('⏱️ Parsing took too long. Server might be waking up. Try again!')
      } else {
        console.error('Parse error:', err)
        setError('Could not parse your input. Try again!')
      }
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
          <>
            <span className={styles.parsing}>🧠 AI is parsing your items...</span>
            <span className={styles.subtext}>(First time may take 10-15s as server wakes up)</span>
          </>
        ) : isListening ? (
          <span className={styles.active}>🎤 Listening... Speak clearly, then click mic again when done!</span>
        ) : (
          <span className={styles.idle}>Click mic and speak what items you have</span>
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

