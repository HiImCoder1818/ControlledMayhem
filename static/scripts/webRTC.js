const pc = new RTCPeerConnection();
const video = document.getElementById("game-video");
const canvas = document.getElementById("game-video-overlay");
let stream;

async function start() {
    stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
    stream.getTracks().forEach(track => pc.addTrack(track, stream));
    video.srcObject = stream;
    // const stream = await navigator.mediaDevices.getDisplayMedia({
    //     video: {
    //         frameRate: { ideal: 60, max: 60 },
    //         cursor: "always"
    //     },
    //     audio: false
    // });

    // stream.getTracks().forEach(track => pc.addTrack(track, stream));
    // video.srcObject = stream;
    pc.getTransceivers().forEach(t => {
        if (t.sender && t.sender.track?.kind === "video") {
            const codecs = RTCRtpSender.getCapabilities("video").codecs;
            t.setCodecPreferences(codecs.filter(c => c.mimeType === "video/H264"));
        }
    });


    const offer = await pc.createOffer();
    await pc.setLocalDescription(offer);

    const res = await fetch("http://localhost:8000/offer", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(pc.localDescription)
    });

    const answer = await res.json();
    await pc.setRemoteDescription(answer);
}

async function endRecording() {
    console.log("Trying to end recording")
    pc.close()
    pc = null;
    await fetch("http://localhost:8000/stop-recording", {
        headers: { "Content-Type": "application/json" },
        method: "POST"
    })
}

video.onloadedmetadata = () => {
    const vw = video.videoWidth;
    const vh = video.videoHeight;
    const aspect = vw / vh;

    const maxHeight = window.innerHeight;
    let width = sliderPos;
    let height = width / aspect;

    if (height > maxHeight) {
        height = maxHeight;
        width = height * aspect;
    }

    video.style.width = `${width}px`;
    video.style.height = `${height}px`;
    canvas.style.width = `${width}px`;
    canvas.style.height = `${height}px`;
    //video.style.opacity = 0;

    console.log(video.videoWidth)
    console.log(video.videoHeight)
    video.play();
};