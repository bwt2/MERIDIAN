import { useEffect, useRef } from "react";
import { useParams, useNavigate } from "react-router";
import { isNumeric } from "../utils";

export default function Client() {
  const navigate = useNavigate();
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const pcRef = useRef<RTCPeerConnection | null>(null);

  // Use env fallback to window.location.hostname
  const mediamtxHost = import.meta.env.VITE_MEDIAMTX_HOST || window.location.hostname;
  const url = `http://${mediamtxHost}:8889/client_cam/whep`;

  const { clientId } = useParams(); // for auth later ?
  useEffect(() => {
    if (!clientId || !isNumeric(clientId)) {
      navigate("/", { replace: true });
    }
  }, [clientId, navigate]);

  useEffect(() => {
    const init = async () => {
      try {
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
        };

        pc.oniceconnectionstatechange = () => {
          console.log("ICE connection state:", pc.iceConnectionState);
        };

        pc.addTransceiver("video", { direction: "recvonly" });
        pc.addTransceiver("audio", { direction: "recvonly" });

        pc.ontrack = (e) => {
          console.log("Received track:", e.track.kind);
          if (!videoRef.current) return;
          videoRef.current.srcObject = e.streams[0];
        };

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

        console.log("Sending offer to", url);
        const resp = await fetch(url, {
          method: "POST",
          headers: { "Content-Type": "application/sdp" },
          body: pc.localDescription?.sdp,
        });

        if (!resp.ok) {
          console.error("WHEP request failed:", resp.status, resp.statusText);
          const errorText = await resp.text();
          console.error("Error response:", errorText);
          return;
        }

        const answerSdp = await resp.text();
        console.log("Received answer, setting remote description");
        await pc.setRemoteDescription({ type: "answer", sdp: answerSdp });
        console.log("WebRTC connection established");
      } catch (error) {
        console.error("Error initialising WebRTC:", error);
      }
    };
    init();

    return () => {
      if (pcRef.current) {
        pcRef.current.close();
      }
    };
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
