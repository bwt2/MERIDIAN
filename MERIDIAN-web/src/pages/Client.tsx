import { useEffect, useRef } from "react";
import { useParams, useNavigate } from "react-router";
import { isNumeric } from "../utils";

export default function Client() {
  const navigate = useNavigate();
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const pcRef = useRef<RTCPeerConnection | null>(null);
  const url = `http://${window.location.hostname}:8889/meridian_cam/whep`;

  const { clientId } = useParams(); // for auth later ?
  useEffect(() => {
    if (!clientId || !isNumeric(clientId)) {
      navigate("/", { replace: true });
    }
  }, [clientId, navigate]);

  useEffect(() => {
    const init = async () => {
      const pc = new RTCPeerConnection();
      pcRef.current = pc;
      pc.addTransceiver("video", { direction: "recvonly" });
      pc.addTransceiver("audio", { direction: "recvonly" });
      pc.ontrack = (e) => {
        if (!videoRef.current) return;
        videoRef.current.srcObject = e.streams[0];
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
    };
    init();
  }, [url]);

  return (
    <main className="bg-black">
      <video
        ref={videoRef}
        playsInline
        autoPlay
        className="w-screen h-screen"
      />
    </main>
  );
}
