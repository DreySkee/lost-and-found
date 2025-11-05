import React, { useState, useEffect, useRef } from 'react'
import './Detector.css'

interface CameraDevice extends MediaDeviceInfo {}

interface Detection {
  label: string
  confidence: number
  bbox: [number, number, number, number]
}

interface StatusState {
  message: string
  type: 'info' | 'success'
  show: boolean
}

interface ErrorState {
  message: string
  show: boolean
}

interface DetectionResponse {
  success: boolean
  detections: Detection[]
  primary?: {
    label: string
    confidence: number
    bbox: [number, number, number, number]
  }
  metadata?: {
    description?: string
  }
  message?: string
}

const Detector: React.FC = () => {
  const [stream, setStream] = useState<MediaStream | null>(null)
  const [availableCameras, setAvailableCameras] = useState<CameraDevice[]>([])
  const [selectedCameraId, setSelectedCameraId] = useState<string>('')
  const [isCameraActive, setIsCameraActive] = useState<boolean>(false)
  const [status, setStatus] = useState<StatusState>({ message: '', type: 'info', show: false })
  const [error, setError] = useState<ErrorState>({ message: '', show: false })
  const [previewImage, setPreviewImage] = useState<string | null>(null)

  const videoRef = useRef<HTMLVideoElement>(null)
  const canvasRef = useRef<HTMLCanvasElement>(null)
  const overlayCanvasRef = useRef<HTMLCanvasElement>(null)
  const detectionIntervalRef = useRef<NodeJS.Timeout | null>(null)

  // Load cameras on mount
  useEffect(() => {
    refreshCameraList()
  }, [])

  // Cleanup on unmount
  useEffect(() => {
    return () => {
      stopCamera()
    }
  }, [])

  const refreshCameraList = async (): Promise<void> => {
    try {
      // Request camera permission first to get device labels
      try {
        const tempStream = await navigator.mediaDevices.getUserMedia({ video: true })
        tempStream.getTracks().forEach(track => track.stop())
      } catch (e) {
        // Permission might be denied, that's okay
      }

      // Enumerate all devices
      const devices = await navigator.mediaDevices.enumerateDevices()

      // Filter video input devices
      const cameras = devices.filter(device => device.kind === 'videoinput') as CameraDevice[]
      setAvailableCameras(cameras)

      // Auto-select if only one camera
      if (cameras.length === 1) {
        setSelectedCameraId(cameras[0].deviceId)
      }
    } catch (err) {
      console.error('Error loading cameras:', err)
      showError('Error loading cameras')
    }
  }

  const showStatus = (message: string, type: 'info' | 'success' = 'info'): void => {
    setStatus({ message, type, show: true })
    setError({ message: '', show: false })
  }

  const showError = (message: string): void => {
    setError({ message, show: true })
    setStatus({ message: '', type: 'info', show: false })
  }

  const startCamera = async (): Promise<void> => {
    try {
      if (!selectedCameraId) {
        showError('Please select a camera first')
        return
      }

      showStatus('Requesting camera access...')

      const constraints: MediaStreamConstraints = {
        video: {
          deviceId: { exact: selectedCameraId },
          width: { ideal: 1280 },
          height: { ideal: 720 }
        }
      }

      const newStream = await navigator.mediaDevices.getUserMedia(constraints)
      setStream(newStream)

      if (videoRef.current) {
        videoRef.current.srcObject = newStream
        videoRef.current.play()
      }

      // Wait for video metadata
      if (videoRef.current) {
        videoRef.current.addEventListener('loadedmetadata', () => {
          if (overlayCanvasRef.current && videoRef.current) {
            overlayCanvasRef.current.width = videoRef.current.videoWidth
            overlayCanvasRef.current.height = videoRef.current.videoHeight
          }
        }, { once: true })
      }

      setIsCameraActive(true)
      const selectedCamera = availableCameras.find(cam => cam.deviceId === selectedCameraId)
      const cameraName = selectedCamera ? selectedCamera.label : 'Camera'
      showStatus(`Camera ready! Using: ${cameraName}. Real-time detection active.`, 'success')

      // Start real-time detection
      startRealtimeDetection()
    } catch (err) {
      const error = err as Error
      showError(`Error accessing camera: ${error.message}`)
      console.error('Camera error:', err)
    }
  }

  const startRealtimeDetection = (): void => {
    // Run detection every 500ms
    detectionIntervalRef.current = setInterval(async () => {
      if (videoRef.current && videoRef.current.readyState === videoRef.current.HAVE_ENOUGH_DATA) {
        await detectFrame()
      }
    }, 500)
  }

  const stopRealtimeDetection = (): void => {
    if (detectionIntervalRef.current) {
      clearInterval(detectionIntervalRef.current)
      detectionIntervalRef.current = null
    }
    drawOverlay([])
  }

  const detectFrame = async (): Promise<void> => {
    try {
      if (!videoRef.current || !canvasRef.current) return

      const canvas = canvasRef.current
      const ctx = canvas.getContext('2d')
      if (!ctx) return

      canvas.width = videoRef.current.videoWidth
      canvas.height = videoRef.current.videoHeight
      ctx.drawImage(videoRef.current, 0, 0)

      // Convert to base64
      const imageData = canvas.toDataURL('image/jpeg', 0.7)

      // Send to server
      const formData = new FormData()
      formData.append('imageData', imageData)

      const response = await fetch('/detector/detect-realtime', {
        method: 'POST',
        body: formData
      })

      if (response.ok) {
        const data: DetectionResponse = await response.json()
        if (data.success && data.detections) {
          drawOverlay(data.detections)
        }
      }
    } catch (err) {
      console.error('Detection error:', err)
    }
  }

  const drawOverlay = (detections: Detection[]): void => {
    const overlay = overlayCanvasRef.current
    if (!overlay || overlay.width === 0 || overlay.height === 0) return

    const ctx = overlay.getContext('2d')
    if (!ctx) return

    ctx.clearRect(0, 0, overlay.width, overlay.height)

    detections.forEach(det => {
      const [x1, y1, x2, y2] = det.bbox
      const conf = (det.confidence * 100).toFixed(1)
      const label = `${det.label} ${conf}%`

      // Draw bounding box
      ctx.strokeStyle = '#00ff00'
      ctx.lineWidth = 3
      ctx.strokeRect(x1, y1, x2 - x1, y2 - y1)

      // Draw label background
      ctx.font = 'bold 16px Arial'
      ctx.fillStyle = 'rgba(0, 255, 0, 0.8)'
      const textWidth = ctx.measureText(label).width
      const textHeight = 22
      const padding = 6
      ctx.fillRect(x1, Math.max(0, y1 - textHeight), textWidth + padding * 2, textHeight)

      // Draw label text
      ctx.fillStyle = '#000'
      ctx.fillText(label, x1 + padding, Math.max(textHeight - 5, y1 - 5))
    })
  }

  const stopCamera = (): void => {
    stopRealtimeDetection()

    if (stream) {
      stream.getTracks().forEach(track => track.stop())
      setStream(null)
    }

    if (videoRef.current) {
      videoRef.current.srcObject = null
    }

    setIsCameraActive(false)
    setPreviewImage(null)
    showStatus('Camera stopped.')
  }

  const captureImage = async (): Promise<void> => {
    try {
      showStatus('Capturing image...', 'info')

      if (!videoRef.current || !canvasRef.current) return

      const canvas = canvasRef.current
      const ctx = canvas.getContext('2d')
      if (!ctx) return

      canvas.width = videoRef.current.videoWidth
      canvas.height = videoRef.current.videoHeight
      ctx.drawImage(videoRef.current, 0, 0)

      const imageData = canvas.toDataURL('image/jpeg', 0.9)
      setPreviewImage(imageData)

      showStatus('Processing with AI detector...', 'info')

      const formData = new FormData()
      formData.append('imageData', imageData)
      const response = await fetch('/detector/detect', {
        method: 'POST',
        body: formData
      })

      const data: DetectionResponse = await response.json()

      if (!response.ok) {
        throw new Error(data.message || 'Detection failed')
      }

      if (data.success && data.detections && data.detections.length > 0) {
        showStatus(`Found ${data.detections.length} object(s)!`, 'success')
      } else {
        const message = data.message || 'No target objects detected in the image.'
        showStatus(message, 'info')
      }
    } catch (err) {
      const error = err as Error
      showError(`Error: ${error.message}`)
      console.error('Capture error:', err)
    }
  }

  return (
    <div className="camera-section">
      <div className="camera-selector">
        <label htmlFor="cameraSelect">📹 Select Camera:</label>
        <select
          id="cameraSelect"
          value={selectedCameraId}
          onChange={(e) => setSelectedCameraId(e.target.value)}
          disabled={isCameraActive}
        >
          <option value="">Select a camera...</option>
          {availableCameras.map((camera, index) => (
            <option key={camera.deviceId} value={camera.deviceId}>
              {camera.label || `Camera ${index + 1}`}
            </option>
          ))}
        </select>
      </div>

      {previewImage ? (
        <div className="preview-section">
          <img src={previewImage} alt="Captured" className="preview-image" />
        </div>
      ) 
      :       
        <div className="video-wrapper">
          <video
            ref={videoRef}
            autoPlay
            playsInline
            style={{ display: isCameraActive ? 'block' : 'none' }}
          />
          <canvas
            ref={overlayCanvasRef}
            className="overlay-canvas"
            style={{ display: isCameraActive ? 'block' : 'none' }}
          />
        </div>
      }
      <canvas ref={canvasRef} style={{ display: 'none' }} />


      <div className="button-group">
        <button
          className="btn-primary"
          onClick={startCamera}
          disabled={isCameraActive || !selectedCameraId}
        >
          📷 Start Camera
        </button>
        <button
          className="btn-success"
          onClick={captureImage}
          disabled={!isCameraActive}
        >
          📸 Capture
        </button>
        <button
          className="btn-secondary"
          onClick={stopCamera}
          disabled={!isCameraActive}
        >
          ⏹ Stop
        </button>
      </div>

      {status.show && (
        <div className={`status ${status.type}`}>
          {status.message}
        </div>
      )}

      {error.show && (
        <div className="error">
          {error.message}
        </div>
      )}
    </div>
  )
}

export default Detector

