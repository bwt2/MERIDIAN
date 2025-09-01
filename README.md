# MERIDIAN
Monorepo for all relevant MERIDIAN source code. 

## Service Architecture

```mermaid
flowchart TD
subgraph MERIDIAN
    subgraph Raspberry Pi
        subgraph WebRTC Infra 
            MM["MediaMTX"]
            ct["Coturn STUN/TURN<br/>server"]
        end
        ym["Yolo Model"]
    end
    rpi0["Raspberry Pi Zero"]
    m["Stepper Motor"]
    sm["Smartphone"]
end
ed["External device"]

MM <-- "Misc" --> ct
ym -- "Commands" --> m
rpi0 -- "RTSP Camera Stream" --> ym
rpi0 -- "RTSP Camera Stream" --> MM
MM <-- "WebRTC" --> ed
MM <-- "WebRTC" --> sm
```

## WebRTC Network Architecture
### Case 1: MERIDIAN broadcasts video
**STUN**:

```mermaid
sequenceDiagram
    autonumber
    participant PiZ as RPi Zero (camera / RTSP exporter)
    participant MM as MediaMTX
    participant S as STUN server
    participant View as External Device (viewer)

    Note over PiZ,MM: RTSP ingest (no WebRTC yet)
    PiZ->>MM: RTSP SETUP/PLAY (H.264) → stream ready on /cam

    Note over View: RTCPeerConnection(iceServers includes STUN)
    View->>S: STUN Binding (discover srflx)
    S-->>View: Binding Success (XOR-MAPPED-ADDRESS)

    View->>MM: HTTP POST /whep/cam (SDP offer, recvonly)
    MM-->>View: 201 Created + SDP answer + Location

    Note over View,MM: ICE connectivity checks (direct)
    View->>MM: STUN Binding checks (host/srflx)
    MM-->>View: Binding Success

    View<<->>MM: DTLS handshake
    MM-->>View: SRTP media (playback from RTSP source)

    Note over View,MM: Optional teardown
    View-->>MM: HTTP DELETE Location (end session)
```

**TURN**:
```mermaid
sequenceDiagram
    autonumber
    participant PiZ as RPi Zero (camera / RTSP exporter)
    participant MM as MediaMTX
    participant T as TURN server
    participant View as External Device (viewer)

    Note over PiZ,MM: RTSP ingest (no WebRTC yet)
    PiZ->>MM: RTSP SETUP/PLAY (H.264) → stream ready on /cam

    Note over View: RTCPeerConnection(iceServers includes TURN)
    View->>T: TURN Allocate / CreatePermission / ChannelBind
    T-->>View: Relayed candidate (allocation OK)

    View->>MM: HTTP POST /whep/cam (SDP offer, recvonly)
    MM-->>View: 201 Created + SDP answer + Location

    Note over View,MM: ICE connectivity checks (relayed)
    View->>T: STUN Binding to MM’s selected candidate (via TURN)
    T->>MM: Forwards Binding
    MM-->>T: Binding Success
    T-->>View: Forwards Success

    View<<->>MM: DTLS handshake (over TURN)
    MM-->>T: SRTP
    T-->>View: SRTP (playback from RTSP source)

    Note over View,MM: Optional teardown
    View-->>MM: HTTP DELETE Location (end session)
```

### Case 2: MERIDIAN receives video
**STUN**:
```mermaid
sequenceDiagram
    autonumber
    participant Pub as External Device (publisher)
    participant View as Smartphone (viewer)
    participant MM as MediaMTX
    participant S as STUN server

    rect rgb(50,50,50)
    Note over Pub,MM: Phase A — WHIP publish (Pub → MediaMTX)
    Note over Pub: RTCPeerConnection(iceServers includes STUN)
    Pub->>S: STUN Binding (discover srflx)
    S-->>Pub: Binding Success (XOR-MAPPED-ADDRESS)
    Pub->>MM: HTTP POST /whip/<path> (SDP offer, sendonly)
    MM-->>Pub: 201 Created + SDP answer + Location
    Note over Pub,MM: ICE checks (direct)
    Pub->>MM: STUN Binding checks (host/srflx)
    MM-->>Pub: Binding Success
    Pub<<->>MM: DTLS handshake
    Pub-->>MM: SRTP media (publish stream)
    Pub-->>MM: HTTP DELETE Location (end session)  %% optional, when stopping
    end

    rect rgb(50,50,50)
    Note over View,MM: Phase B — WHEP play (MediaMTX → View)
    Note over View: RTCPeerConnection(iceServers includes STUN)
    View->>S: STUN Binding (discover srflx)
    S-->>View: Binding Success (XOR-MAPPED-ADDRESS)
    View->>MM: HTTP POST /whep/<path> (SDP offer, recvonly)
    MM-->>View: 201 Created + SDP answer + Location
    Note over View,MM: ICE checks (direct)
    View->>MM: STUN Binding checks (host/srflx)
    MM-->>View: Binding Success
    View<<->>MM: DTLS handshake
    MM-->>View: SRTP media (play stream)
    View-->>MM: HTTP DELETE Location (end session)  %% optional, when stopping
    end
```
**TURN**:
```mermaid
sequenceDiagram
    autonumber
    participant Pub as External Device (publisher)
    participant View as Smartphone (viewer)
    participant MM as MediaMTX
    participant T as TURN server

    rect rgb(50,50,50)
    Note over Pub,MM: Phase A — WHIP publish over TURN (Pub → MediaMTX)
    Note over Pub: RTCPeerConnection(iceServers includes TURN)
    Pub->>T: TURN Allocate / CreatePermission / ChannelBind
    T-->>Pub: Relayed candidate (allocation OK)
    Pub->>MM: HTTP POST /whip/<path> (SDP offer, sendonly)
    MM-->>Pub: 201 Created + SDP answer + Location
    Note over Pub,MM: ICE checks (relayed)
    Pub->>T: STUN Binding to MM’s selected candidate (via TURN)
    T->>MM: Forwards Binding
    MM-->>T: Binding Success
    T-->>Pub: Forwards Success
    Pub<<->>MM: DTLS handshake (over TURN)
    Pub-->>T: SRTP
    T-->>MM: SRTP (publish stream)
    Pub-->>MM: HTTP DELETE Location (end session)  %% optional, when stopping
    end

    rect rgb(50,50,50)
    Note over View,MM: Phase B — WHEP play over TURN (MediaMTX → View)
    Note over View: RTCPeerConnection(iceServers includes TURN)
    View->>T: TURN Allocate / CreatePermission / ChannelBind
    T-->>View: Relayed candidate (allocation OK)
    View->>MM: HTTP POST /whep/<path> (SDP offer, recvonly)
    MM-->>View: 201 Created + SDP answer + Location
    Note over View,MM: ICE checks (relayed)
    View->>T: STUN Binding to MM’s selected candidate (via TURN)
    T->>MM: Forwards Binding
    MM-->>T: Binding Success
    T-->>View: Forwards Success
    View<<->>MM: DTLS handshake (over TURN)
    MM-->>T: SRTP
    T-->>View: SRTP (play stream)
    View-->>MM: HTTP DELETE Location (end session)  %% optional, when stopping
    end

```