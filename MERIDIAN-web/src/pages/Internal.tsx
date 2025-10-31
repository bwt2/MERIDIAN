import { useEffect, useRef, useState } from "react";
import {
  startVideoPlaybackWithStream,
  cleanupPcRef,
  postWHIPWHEP,
} from "../utils";

export default function Internal() {
  const videoRef = useRef<HTMLVideoElement | null>(null);
  const subPcRef = useRef<RTCPeerConnection | null>(null);
  const pubPcRef = useRef<RTCPeerConnection | null>(null);
  const [connecting, setConnecting] = useState<boolean>(true);

  const localDeviceConstraints: MediaStreamConstraints = {
    video: true, // for debugging
    audio: true,
  };

  const subUrl = `http://${window.location.hostname}:8889/external_cam/whep`;
  const pubUrl = `http://${window.location.hostname}:8889/internal_cam/whip`;

  useEffect(() => {
    /* ---------- SUBSCRIBE (WHEP) ---------- */
    const initSub = async () => {
      /* Set up RTC peer connection */
      const pc = new RTCPeerConnection();
      subPcRef.current = pc;
      pc.addTransceiver("video", { direction: "recvonly" });
      pc.addTransceiver("audio", { direction: "recvonly" });

      // Set up callback when RTC peer connection receives audio / video stream (i.e. "track")
      pc.ontrack = (e) => {
        startVideoPlaybackWithStream(videoRef, e.streams[0]);
      };

      /* Make local SDP (posting what we expect) offer for ICE gathering */
      const offer = await pc.createOffer();
      pc.setLocalDescription(offer);

      /* Wait for ICE (i.e. network paths to rempte peers) gathering to complete */
      if (pc.iceGatheringState === "complete") {
        postWHIPWHEP(pc, subUrl, setConnecting);
      } else {
        const onState = () => {
          if (pc.iceGatheringState === "complete") {
            pc.removeEventListener("icegatheringstatechange", onState);
            postWHIPWHEP(pc, subUrl, setConnecting);
          }
        };
        pc.addEventListener("icegatheringstatechange", onState);
      }
    };

    /* ---------- PUBLISH (WHIP) ---------- */
    const initPub = async () => {
      const stream = await navigator.mediaDevices.getUserMedia(
        localDeviceConstraints,
      );

      const pc = new RTCPeerConnection();
      pubPcRef.current = pc;
      stream.getTracks().forEach((t) => pc.addTrack(t, stream));

      const offer = await pc.createOffer({
        offerToReceiveAudio: false,
        offerToReceiveVideo: false,
      });
      await pc.setLocalDescription(offer);

      await new Promise<void>((resolve) => {
        if (pc.iceGatheringState === "complete") return resolve();
        const onState = () => {
          if (pc.iceGatheringState === "complete") {
            pc.removeEventListener("icegatheringstatechange", onState);
            resolve();
          }
        };
        pc.addEventListener("icegatheringstatechange", onState, { once: true });
      });

      postWHIPWHEP(pc, pubUrl, setConnecting);
    };

    /* ---------- INIT ---------- */
    initPub();
    initSub();

    return () => {
      cleanupPcRef(subPcRef);
      cleanupPcRef(pubPcRef);
    };
  });

  return (
    <main className="bg-black flex items-center justify-center w-screen h-screen relative">
      <video
        ref={videoRef}
        playsInline
        autoPlay
        disablePictureInPicture
        muted
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
