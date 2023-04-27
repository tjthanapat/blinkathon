const BLINKLIMIT = 10; // blink goal
const VIDEOSTREAM = 100; // frequency of frame send to server

const video = document.getElementById('live-camera');
const canvas = document.getElementById('live-camera-preview');
const context = canvas.getContext('2d');
const serverLive = document.getElementById('server-live');

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
    alert('Cannot access your webcam.');
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
}, VIDEOSTREAM);

const startBtn = document.getElementById('start-btn');
const gameStatus = document.getElementById('game-status');
const car1 = document.getElementById('car-1');
const car2 = document.getElementById('car-2');


const startGame = () => {
  console.log('start clicked');
  socket.emit('start-game');
  startBtn.style.display = 'none';

  gameStatus.innerText = 'Calculating... - Please keep your eyes open.';

  car1.style.display = 'block';
  car1.style.left = '0%';
  car2.style.display = 'block';
  car2.style.left = '0%';
};

socket.on('blinkathon', (game) => {
  console.log(game);
  serverLive.src = game.frame;

  const startBtn = document.getElementById('start-btn');
  if (!!game.playable) {
    startBtn.disabled = false;
    if (!game.counting_blink & !game.detecting_blink) {
      gameStatus.innerText = 'Press a button to start.';
    }
  } else {
    startBtn.disabled = true;
    gameStatus.innerText = '2 players are required.';
  }
  if (!!game.counting_blink) {
    gameStatus.innerText = 'Blink!';
    const player1BlinkCount = game.players[0].blinkCount;
    const player1BlinkCountElem = document.getElementById(
      'player1-blink-count'
    );
    player1BlinkCountElem.innerText = Math.min(player1BlinkCount, BLINKLIMIT);
    const player2BlinkCount = game.players[1].blinkCount;
    const player2BlinkCountElem = document.getElementById(
      'player2-blink-count'
    );
    player2BlinkCountElem.innerText = Math.min(player2BlinkCount, BLINKLIMIT);
    moveCars(player1BlinkCount, player2BlinkCount);
    if (player1BlinkCount == BLINKLIMIT) {
      winGame('P1');
    } else if (player2BlinkCount == BLINKLIMIT) {
      winGame('P2');
      gameStatus.innerText = 'P2 wins';
    }
  } else if (!!game.detecting_blink) {
    gameStatus.innerText = 'Calculating... - Please keep your eyes open.';
  }
});

const winGame = (player) => {
  gameStatus.innerText = `${player} wins.`;
  socket.emit('end-game');
  startBtn.style.display = 'block';
  startBtn.innerText = 'Play again';
  let winSound = new Audio('/static/sound/win.wav');
  winSound.volume = 0.7;
  winSound.play();
};

const moveCars = (blinkCount1, blinkCount2) => {
  const car1pos = Math.min(blinkCount1 / BLINKLIMIT, 1) * 100;
  car1.style.left = `${car1pos}%`;
  const car2pos = Math.min(blinkCount2 / BLINKLIMIT, 1) * 100;
  car2.style.left = `${car2pos}%`;
};

window.onload = function () {
  const bgMusic = document.getElementById('background-music');
  bgMusic.volume = 0.3;
};
