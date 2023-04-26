const video = document.getElementById('live-camera');
const canvas = document.getElementById('live-camera-preview');
const context = canvas.getContext('2d');

canvas.width = 400;
canvas.height = 300;

context.width = canvas.width;
context.height = canvas.height;

navigator.mediaDevices
  .getUserMedia({ video: true })
  .then((stream) => {
    video.srcObject = stream;
  })
  .catch((err) => {
    alert('Cannot access webcam.');
    console.error(err);
  });

const socket = io();
socket.on('connect', () => {
  console.log('connected!');
});

// draw video on canvas and convert to data url
// then send to server every n ms.
setInterval(() => {
  context.drawImage(video, 0, 0, context.width, context.height);
  const frameData = canvas.toDataURL('image/jpeg');
  socket.emit('stream', frameData);
  console.log('sent frame!');
}, 500);

const serverLive = document.getElementById('server-live');

socket.on('blinkathon', (game) => {
  console.log(game);
  serverLive.src = game.frame;

  const startBtn = document.getElementById('start-btn');
  if (!!game.playable) {
    startBtn.disabled = false;
  } else {
    startBtn.disabled = true;
  }
});


const startGame = () => {
  console.log('start clicked')
  socket.emit('start-game');
}
