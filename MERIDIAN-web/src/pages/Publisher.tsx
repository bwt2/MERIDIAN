import { useEffect, useRef, useState } from "react";
import { useParams, useNavigate } from "react-router";
import { isNumeric } from "../utils";

export default function Publisher() {
  const navigate = useNavigate();
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const pcRef = useRef<RTCPeerConnection | null>(null);
  const streamRef = useRef<MediaStream | null>(null);
  const [isPublishing, setIsPublishing] = useState(false);
  const [error, setError] = useState<string | null>(null);

  // Use env fallback to window.location.hostname
  const mediamtxHost = import.meta.env.VITE_MEDIAMTX_HOST || window.location.hostname;
  const url = `http://${mediamtxHost}:8889/client_cam/whip`;

  const { clientId } = useParams();
  useEffect(() => {
    if (!clientId || !isNumeric(clientId)) {
      navigate("/", { replace: true });
    }
  }, [clientId, navigate]);

  useEffect(() => {
    const init = async () => {
      try {
        setIsPublishing(true);

        // Get user media (camera and microphone)
        console.log("Requesting camera and microphone access...");
        const stream = await navigator.mediaDevices.getUserMedia({
          video: {
            width: { ideal: 1280 },
            height: { ideal: 720 },
            frameRate: { ideal: 30 },
          },
          audio: true,
        });
        streamRef.current = stream;

        // Display local preview
        if (videoRef.current) {
          videoRef.current.srcObject = stream;
        }

        console.log("Creating peer connection...");
        const pc = new RTCPeerConnection({
          iceServers: [
            { urls: "stun:stun.l.google.com:19302" },
            {
              urls: `turn:${mediamtxHost}:8189`,
              username: "meridian",
              credential: "meridian123",
            },
          ],
        });
        pcRef.current = pc;

        // Log connection state changes
        pc.onconnectionstatechange = () => {
          console.log("Connection state:", pc.connectionState);
          if (pc.connectionState === "failed") {
            setError("Connection failed. Please check your network.");
          }
        };

        pc.oniceconnectionstatechange = () => {
          console.log("ICE connection state:", pc.iceConnectionState);
        };

        // Add local stream tracks to peer connection
        stream.getTracks().forEach((track) => {
          console.log("Adding track:", track.kind);
          pc.addTrack(track, stream);
        });

        // Create offer
        const offer = await pc.createOffer();
        await pc.setLocalDescription(offer);

        console.log("Waiting for ICE gathering...");
        await new Promise<void>((resolve) => {
          if (pc.iceGatheringState === "complete") return resolve();
          const onState = () => {
            if (pc.iceGatheringState === "complete") {
              pc.removeEventListener("icegatheringstatechange", onState);
              resolve();
            }
          };
          pc.addEventListener("icegatheringstatechange", onState);
        });
        console.log("ICE gathering complete");

        // Send offer to WHIP endpoint
        console.log("Sending offer to", url);
        const resp = await fetch(url, {
          method: "POST",
          headers: { "Content-Type": "application/sdp" },
          body: pc.localDescription?.sdp,
        });

        if (!resp.ok) {
          console.error("WHIP request failed:", resp.status, resp.statusText);
          const errorText = await resp.text();
          console.error("Error response:", errorText);
          setError(`Failed to publish: ${resp.status} ${resp.statusText}`);
          return;
        }

        const answerSdp = await resp.text();
        console.log("Received answer, setting remote description");
        await pc.setRemoteDescription({ type: "answer", sdp: answerSdp });
        console.log("Publishing stream successfully!");
      } catch (error) {
        console.error("Error publishing stream:", error);
        if (error instanceof Error) {
          setError(error.message);
        }
      }
    };

    init();

    return () => {
      // Cleanup
      if (pcRef.current) {
        pcRef.current.close();
      }
      if (streamRef.current) {
        streamRef.current.getTracks().forEach((track) => track.stop());
      }
    };
  }, [url, mediamtxHost]);

  return (
    <main className="min-h-screen bg-black flex flex-col items-center justify-center p-4">
      <div className="w-full max-w-4xl">
        <div className="mb-4 text-center">
          <h1 className="text-2xl font-bold text-white mb-2">
            Publishing Stream
          </h1>
          <p className="text-gray-400">
            {isPublishing
              ? "Your camera is being streamed to the server"
              : "Initializing..."}
          </p>
          {error && (
            <p className="text-red-500 mt-2 text-sm">{error}</p>
          )}
        </div>
        <div className="relative bg-gray-900 rounded-lg overflow-hidden">
          <video
            ref={videoRef}
            autoPlay
            playsInline
            muted
            className="w-full h-auto"
          />
          <div className="absolute top-4 right-4 bg-red-600 text-white px-3 py-1 rounded-full text-sm font-semibold flex items-center gap-2">
            <span className="w-2 h-2 bg-white rounded-full animate-pulse"></span>
            LIVE
          </div>
        </div>
        <div className="mt-4 text-center text-gray-400 text-sm">
          Others can view this stream at: <span className="text-white font-mono">/client/{clientId}</span>
        </div>
      </div>
    </main>
  );
}
