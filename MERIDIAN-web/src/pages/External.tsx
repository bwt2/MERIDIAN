import { useEffect, useRef, useState } from "react";

export default function External() {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const pcRef = useRef<RTCPeerConnection | null>(null);
  const streamRef = useRef<MediaStream | null>(null);

  const url = `http://${window.location.hostname}:8889/internal_cam/whep`;
  const [connecting, setConnecting] = useState<boolean>(true);

  // Attach stream to video whenever either ref is ready
  useEffect(() => {
    const v = videoRef.current;
    if (!v || !streamRef.current) return;
    v.srcObject = streamRef.current;

    // Try to autoplay
    v.play().catch(() => {});
  }, []);

  useEffect(() => {
    const init = async () => {
      const pc = new RTCPeerConnection();
      pcRef.current = pc;
      pc.addTransceiver("video", { direction: "recvonly" });
      pc.addTransceiver("audio", { direction: "recvonly" });
      pc.ontrack = (e) => {
        streamRef.current = e.streams[0];
        const v = videoRef.current;
        if (v) {
          v.srcObject = streamRef.current;
          v.play().catch(() => {});
        }
      };

      const offer = await pc.createOffer();
      await pc.setLocalDescription(offer);
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

      const resp = await fetch(url, {
        method: "POST",
        headers: { "Content-Type": "application/sdp" },
        body: pc.localDescription?.sdp,
      });

      if (!resp.ok) {
        return;
      }

      const answerSdp = await resp.text();
      await pc.setRemoteDescription({ type: "answer", sdp: answerSdp });
      setConnecting(false);
    };
    init();
  }, [url]);

  return (
    <main className="bg-black flex items-center justify-center w-screen h-screen relative">
      <video
        ref={videoRef}
        playsInline
        autoPlay
        disablePictureInPicture
        className="w-screen h-screen rotate-90"
      />
      {connecting && (
        <h1 className="animate-pulse text-white text-8xl absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2">
          Connecting
        </h1>
      )}
    </main>
  );
}
