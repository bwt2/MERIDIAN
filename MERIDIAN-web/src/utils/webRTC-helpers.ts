export function startVideoPlaybackWithStream(
  videoRef: React.RefObject<HTMLVideoElement | null>,
  stream: MediaProvider,
) {
  const v = videoRef.current;
  if (!v) return null;
  v.srcObject = stream;
  v.play();
}

export function cleanupPcRef(pcRef: React.RefObject<RTCPeerConnection | null>) {
  try {
    pcRef.current?.getSenders().forEach((s) => s.track?.stop());
    pcRef.current?.getReceivers().forEach((r) => r.track?.stop());
  } catch {
    console.error("Something went wrong cleaning up the peer connection.");
  }
  pcRef.current?.close();
  pcRef.current = null;
}

/* Send offer to WHEP endpoint. After confirming response via setRemoteDescription, pc.ontrack should fire */
export async function postWHIPWHEP(
  pc: RTCPeerConnection,
  url: string,
  setConnecting?: React.Dispatch<React.SetStateAction<boolean>>,
) {
  const resp = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/sdp" },
    body: pc.localDescription?.sdp ?? "",
  });
  const answerSdp = await resp.text();
  await pc.setRemoteDescription({ type: "answer", sdp: answerSdp });
  if (setConnecting) setConnecting(false);
}
