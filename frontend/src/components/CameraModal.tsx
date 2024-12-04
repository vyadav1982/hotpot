import * as React from 'react';
import { Button } from '@/components/ui/button';
import {
  Dialog,
  DialogContent,
  DialogHeader,
  DialogTitle,
} from '@/components/ui/dialog';

interface CameraModalProps {
  isOpen: boolean;
  onClose: () => void;
  onCapture: (imageSrc: string) => void;
}

export function CameraModal({ isOpen, onClose, onCapture }: CameraModalProps) {
  const videoRef = React.useRef<HTMLVideoElement>(null);
  const canvasRef = React.useRef<HTMLCanvasElement>(null);
  const [error, setError] = React.useState<string | null>(null);
  const [isLoading, setIsLoading] = React.useState(false);
  const [isCameraInitialized, setCameraInitialized] = React.useState(false);

  const initializeCamera = async () => {
    setIsLoading(true);
    setError(null);
    try {
      const constraints = {
        video: {
          facingMode: 'environment',
          width: { ideal: 1920 },
          height: { ideal: 1080 },
        },
      };

      const stream = await navigator.mediaDevices.getUserMedia(constraints);
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
        setCameraInitialized(true);
      }
    } catch (err) {
      console.error('Error accessing the camera:', err);
      setError(
        'Unable to access camera. Please ensure you have granted camera permissions.',
      );
    } finally {
      setIsLoading(false);
    }
  };

  React.useEffect(() => {
    if (!isOpen) {
      if (videoRef.current && videoRef.current.srcObject) {
        const tracks = (videoRef.current.srcObject as MediaStream).getTracks();
        tracks.forEach((track) => track.stop());
      }
      setCameraInitialized(false);
      setError(null);
    }
  }, [isOpen]);

  const handleCapture = () => {
    if (videoRef.current && canvasRef.current) {
      const context = canvasRef.current.getContext('2d');
      if (context) {
        canvasRef.current.width = videoRef.current.videoWidth;
        canvasRef.current.height = videoRef.current.videoHeight;
        context.drawImage(
          videoRef.current,
          0,
          0,
          canvasRef.current.width,
          canvasRef.current.height,
        );
        const imageSrc = canvasRef.current.toDataURL('image/jpeg');
        onCapture(imageSrc);
        onClose();
      }
    }
  };

  return (
    <Dialog open={isOpen} onOpenChange={onClose}>
      <DialogContent className="sm:max-w-[425px]">
        <DialogHeader>
          <DialogTitle>Capture Image</DialogTitle>
        </DialogHeader>
        <div className="mt-2">
          {error && <div className="mb-4 text-red-500">{error}</div>}
          {!isCameraInitialized && !error && (
            <Button
              onClick={initializeCamera}
              disabled={isLoading}
              className="mb-4 w-full"
            >
              {isLoading ? 'Initializing Camera...' : 'Start Camera'}
            </Button>
          )}
          <video
            ref={videoRef}
            autoPlay
            playsInline
            className={`w-full ${!isCameraInitialized ? 'hidden' : ''}`}
          />
          <canvas ref={canvasRef} style={{ display: 'none' }} />
        </div>
        {isCameraInitialized && (
          <div className="mt-4 flex justify-end">
            <Button onClick={handleCapture}>Capture</Button>
          </div>
        )}
      </DialogContent>
    </Dialog>
  );
}
