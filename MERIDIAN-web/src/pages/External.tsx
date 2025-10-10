import { useEffect, useRef, useState } from "react";

export default function External() {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const pcRef = useRef<RTCPeerConnection | null>(null);
  const streamRef = useRef<MediaStream | null>(null);

  const url = `http://${window.location.hostname}:8889/internal_cam/whep`;
  const [connecting, setConnecting] = useState<boolean>(true);

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

    return () => {
      try {
        pcRef.current?.getSenders().forEach((s) => s.track?.stop());
        pcRef.current?.getReceivers().forEach((r) => r.track?.stop());
      } catch {
        console.error("Something went wrong cleaning up the peer connection.");
      }
      pcRef.current?.close();
      pcRef.current = null;
      streamRef.current = null;
    };
  }, [url]);

  return (
    <main className="bg-black flex items-center justify-center w-screen h-screen relative">
      <video
        ref={videoRef}
        playsInline
        autoPlay
        disablePictureInPicture
        className="
          rotate-90 sm:rotate-0 origin-center
          w-auto h-auto
          max-w-[100svh] max-h-[100svw]
          sm:max-w-[100svw] sm:max-h-[100svh]
          object-contain
        "
      />
      {connecting && (
        <h1 className="animate-pulse text-white text-6xl sm:text-8xl absolute left-1/2 top-1/2 -translate-x-1/2 -translate-y-1/2">
          Connecting
        </h1>
      )}
    </main>
  );
}
