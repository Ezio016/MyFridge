import { useState, useEffect, useRef } from 'react'
import { Mic, MicOff, Loader, X } from 'lucide-react'
import { inventoryAPI } from '../api/client'
import styles from './VoiceInput.module.css'

function VoiceInput({ onItemsParsed }) {
  const [isListening, setIsListening] = useState(false)
  const [transcript, setTranscript] = useState('')
  const [error, setError] = useState(null)
  const [isParsing, setIsParsing] = useState(false)
  const [itemsList, setItemsList] = useState([])
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
    
    recognition.continuous = true
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
      console.log('🎤 Sending to backend:', text)
      const result = await inventoryAPI.parseVoice(text)
      
      const elapsed = ((Date.now() - startTime) / 1000).toFixed(1)
      console.log(`✅ Parsed in ${elapsed}s`, result)
      
      if (result.items && result.items.length > 0) {
        // Add to the list instead of submitting immediately
        setItemsList(prev => [...prev, ...result.items])
        setTranscript('') // Clear transcript after successful parse
      } else if (result.error) {
        setError(result.error)
      } else {
        setError('No items detected. Try again!')
      }
    } catch (err) {
      console.error('Parse error:', err)
      setError(`❌ ${err.message || 'Could not parse. Try again!'}`)
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

  const removeItem = (index) => {
    setItemsList(prev => prev.filter((_, i) => i !== index))
  }

  const clearAll = () => {
    setItemsList([])
  }

  const submitAllItems = () => {
    if (onItemsParsed && itemsList.length > 0) {
      onItemsParsed(itemsList)
      setItemsList([]) // Clear after submit
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
            <span className={styles.parsing}>🧠 AI is parsing...</span>
            <span className={styles.subtext}>(First time may take 10-15s)</span>
          </>
        ) : isListening ? (
          <span className={styles.active}>🎤 Say one item, then click mic</span>
        ) : (
          <span className={styles.idle}>Click mic → Say item → Click again → Repeat</span>
        )}
      </div>

      {transcript && (
        <div className={styles.transcript}>
          <strong>Listening:</strong> "{transcript}"
        </div>
      )}

      {/* Items List */}
      {itemsList.length > 0 && (
        <div className={styles.itemsList}>
          <div className={styles.itemsHeader}>
            <strong>Items to add ({itemsList.length}):</strong>
            <button className={styles.clearBtn} onClick={clearAll}>Clear All</button>
          </div>
          <div className={styles.items}>
            {itemsList.map((item, index) => (
              <div key={index} className={styles.item}>
                <span className={styles.itemText}>
                  {item.quantity} {item.unit} of {item.name}
                </span>
                <button 
                  className={styles.removeBtn} 
                  onClick={() => removeItem(index)}
                  title="Remove"
                >
                  <X size={16} />
                </button>
              </div>
            ))}
          </div>
          <button className={styles.submitBtn} onClick={submitAllItems}>
            ✅ Add All {itemsList.length} Items to Fridge
          </button>
        </div>
      )}
    </div>
  )
}

export default VoiceInput
