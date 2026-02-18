
const ctx = canvas.getContext("2d");
const ws = new WebSocket(`ws://localhost:8000/ws/bboxes`);
let bboxes;

function fetchBBoxes() {
  fetch("/latest-bboxes")
      .then(res => res.json())
      .then(data => {

          bboxes = data;
      })
      .catch(err => console.error("Failed to fetch bboxes:", err));
}

setInterval(() => {
  fetchBBoxes();
  if (bboxes) drawBoxes(bboxes);
}, 70);
console.log("We're in drawing.js");

ws.onmessage = (event) => {
    try {
        const data = JSON.parse(event.data);
        console.log(`Received bboxes: ${data.bboxes}`)
        bboxes = data.bboxes;  // store latest bounding boxes
        drawBoxes(bboxes);
    } catch (err) {
        console.error("Failed to parse WS message:", err);
    }
};

ws.onopen = () => console.log("WebSocket connected");
ws.onclose = () => console.log("WebSocket disconnected");

function drawBoxes(bboxes) {
  ctx.clearRect(0, 0, canvas.width, canvas.height);

  ctx.lineWidth = 2;
  ctx.font = "14px sans-serif";

  //console.log("Trying to draw boxes");
  all_bboxes = bboxes.bboxes;
  artifact_bboxes = all_bboxes.artifact_tracks;
  robot_bboxes = all_bboxes.robot_tracks;
  red_goal = all_bboxes.red_goal;
  blue_goal = all_bboxes.blue_goal;

  {
    console.log("Trying to draw the freaking red goal");
    const x = red_goal.x1 * canvas.width;
    const y = red_goal.y1 * canvas.height;
    const w = (red_goal.x2 - red_goal.x1) * canvas.width;
    const h = (red_goal.y2 - red_goal.y1) * canvas.height;
    ctx.strokeStyle = "red";
    ctx.strokeRect(x, y, w, h);
  }
  {
    console.log("Trying to draw the freaking blue goal");
    const x = blue_goal.x1 * canvas.width;
    const y = blue_goal.y1 * canvas.height;
    const w = (blue_goal.x2 - blue_goal.x1) * canvas.width;
    const h = (blue_goal.y2 - blue_goal.y1) * canvas.height;
    ctx.strokeStyle = "blue";
    ctx.strokeRect(x, y, w, h);
  }

  for (const b of artifact_bboxes) {
    console.log("Yippee kai yay artifact");
    const x = b.x1 * canvas.width;
    const y = b.y1 * canvas.height;
    const w = (b.x2 - b.x1) * canvas.width;
    const h = (b.y2 - b.y1) * canvas.height;

    ctx.strokeStyle = "lime";
    ctx.strokeRect(x, y, w, h);

    if (b.label) {
      ctx.fillStyle = "lime";
      ctx.fillText(b.id, x + 4, y - 4);
    }
  }
  
  for (const b of robot_bboxes) {
    console.log("Yippee kai yay robot");
    const x = b.x1 * canvas.width;
    const y = b.y1 * canvas.height;
    const w = (b.x2 - b.x1) * canvas.width;
    const h = (b.y2 - b.y1) * canvas.height;

    ctx.strokeStyle = "purple";
    ctx.strokeRect(x, y, w, h);

    if (b.label) {
      ctx.fillStyle = "purple";
      ctx.fillText(b.id, x + 4, y - 4);
    }
  }
}
