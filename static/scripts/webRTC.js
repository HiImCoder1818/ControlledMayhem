const pc = new RTCPeerConnection();
const video = document.getElementById("game-video");
const canvas = document.getElementById("game-video-overlay");

async function start() {
    const stream = await navigator.mediaDevices.getUserMedia({ video: true, audio: false });
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

    const offer = await pc.createOffer();
    await pc.setLocalDescription(offer);

    const res = await fetch("/offer", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(pc.localDescription)
    });

    const answer = await res.json();
    await pc.setRemoteDescription(answer);
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