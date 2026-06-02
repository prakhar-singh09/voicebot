import { useEffect, useRef, useState } from 'react'
import { connectRoom, RoomEvent } from './services/livekit'
import './App.css'

function App() {
  const [name, setName] = useState(`user-${Math.floor(Math.random() * 1000)}`)
  const [status, setStatus] = useState('idle')
  const [roomName, setRoomName] = useState('')
  const [error, setError] = useState('')
  const [micEnabled, setMicEnabled] = useState(false)
  const roomRef = useRef(null)
  const audioRef = useRef(null)

  useEffect(() => {
    return () => {
      roomRef.current?.disconnect()
    }
  }, [])

  async function joinRoom() {
    setError('')
    setStatus('connecting')

    try {
      const { room, roomName } = await connectRoom(name)
      roomRef.current = room
      setRoomName(roomName)

      room.on(RoomEvent.TrackSubscribed, (track) => {
        if (track.kind === 'audio' && audioRef.current) {
          track.attach(audioRef.current)
          audioRef.current.play().catch(() => {})
        }
      })

      room.on(RoomEvent.Disconnected, () => {
        setStatus('idle')
        setMicEnabled(false)
      })

      await room.localParticipant.setMicrophoneEnabled(true)
      setMicEnabled(true)
      setStatus('connected')
    } catch (err) {
      setStatus('idle')
      setError(err.message || 'Connection failed')
    }
  }

  async function toggleMic() {
    if (!roomRef.current) return
    const next = !micEnabled
    await roomRef.current.localParticipant.setMicrophoneEnabled(next)
    setMicEnabled(next)
  }

  function leaveRoom() {
    roomRef.current?.disconnect()
    roomRef.current = null
    setStatus('idle')
    setMicEnabled(false)
    setRoomName('')
  }

  return (
    <main className="app-shell">
      <section className="voice-panel">
        <div className="orb" aria-hidden="true">
          <span className={status === 'connected' ? 'pulse active' : 'pulse'} />
        </div>

        <div className="copy">
          <p className="eyebrow">LiveKit voice room</p>
          <h1>Low latency voicebot</h1>
          <p>
            A simple voicebot built with LiveKit. Join the room and start talking! The bot will repeat what you say with a short delay. You can also mute your mic or leave the room when you're done.
          </p>
        </div>

        <div className="controls">
          <label>
            Display name
            <input
              value={name}
              onChange={(event) => setName(event.target.value)}
              disabled={status !== 'idle'}
            />
          </label>

          {status === 'connected' ? (
            <div className="button-row">
              <button type="button" onClick={toggleMic}>
                {micEnabled ? 'Mute mic' : 'Unmute mic'}
              </button>
              <button type="button" className="secondary" onClick={leaveRoom}>
                Leave
              </button>
            </div>
          ) : (
            <button
              type="button"
              onClick={joinRoom}
              disabled={status === 'connecting' || !name.trim()}
            >
              {status === 'connecting' ? 'Connecting...' : 'Start talking'}
            </button>
          )}
        </div>

        <div className="status-line" data-state={status}>
          <span>{status}</span>
          {roomName ? <strong>{roomName}</strong> : <strong>not connected</strong>}
        </div>

        {error ? <p className="error">{error}</p> : null}
        <audio ref={audioRef} autoPlay />
      </section>
    </main>
  )
}

export default App
