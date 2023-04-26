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



const gameStatus = document.getElementById('game-status');
const car1 = document.getElementById('car-1');
const car2 = document.getElementById('car-2');
const roadWidth = document.getElementById('road').clientWidth;
const carWidth = car1.clientWidth;

// Set goal here!!
const limitBlink = 3

const player1 = 'P1';
const player2 = 'P2';

// let end_or_not = true;

const startGame = () => {
  console.log('start clicked');
  socket.emit('start-game');
  const startBtn = document.getElementById('start-btn');
  startBtn.style.display = 'none';

  gameStatus.innerText = 'Calculating... - Please keep your eyes open.';

  car1.style.display = 'block';
  car2.style.display = 'block';
};

socket.on('blinkathon', (game) => {
  console.log(game);
  serverLive.src = game.frame;

  const startBtn = document.getElementById('start-btn');
  if (!!game.playable) {
    startBtn.disabled = false;
  } else {
    startBtn.disabled = true;
  }
  const gameStatus = document.getElementById('game-status');
  if (!!game.counting_blink) {
    gameStatus.innerText = 'Blink!';
  }
  
  const player1BlinkCount = document.getElementById('player1-blink-count');
  player1BlinkCount.innerText = Math.min(game.players[0].blinkCount, limitBlink);
  const player2BlinkCount = document.getElementById('player2-blink-count');
  player2BlinkCount.innerText = Math.min(game.players[1].blinkCount, limitBlink);

  moveCars(game.players[0].blinkCount, game.players[1].blinkCount)
});

const moveCars = (blinkCount1, blinkCount2) => {
  const car1pos = Math.min(blinkCount1 / limitBlink, 1) *100
  car1.style.left = `${car1pos}%`
  const car2pos = Math.min(blinkCount2 / limitBlink, 1) *100
  car2.style.left = `${car2pos}%`
}

// function myFunction(pos1, pos2, end_or_not) {
//   car1.style.left = Math.min(pos1 * speed, 80) + '%';
//   car2.style.left = Math.min(pos2 * speed, 80) + '%';

//   if (pos1 >= 10 || pos2 >= 10) {
//     // check if either player has reached 10
//     // document.removeEventListener("keydown", handleKeyDown);

//     if (end_or_not) {
//       end_or_not = false;
//       const winner = document.createElement('p');
//       winner.setAttribute('id', 'win');
//       winSound.play();
//       bgMusic.pause();
//       if (pos1 > pos2) {
//         // check which player has moved farther
//         winner.textContent = `${player1} wins!`;
//       } else {
//         winner.textContent = `${player2} wins!`;
//       }
//       document.body.appendChild(winner);
//       winner.addEventListener('animationend', () => {
//         winSound.pause();
//       });
//     }
//   }
// }


// socket.on('game', function (game) {
//   console.log('game:', game);
//   const startBtn = document.getElementById('start-btn');
//   const container = document.getElementById('container');
//   if (!!game.playable) {
//     startBtn.disabled = false;
//     container.disabled = true;
//   } else {
//     startBtn.disabled = true;
//     container.disabled = false;
//   }
//   const gameStatus = document.getElementById('game-status');
//   if (!!game.detecting) {
//     gameStatus.innerText = 'Blink!';
//   }

//   const player1BlinkCount = document.getElementById('player1-blink-count');
//   player1BlinkCount.innerText = Math.min(game.players[0].blinkCount, 10);
//   const player2BlinkCount = document.getElementById('player2-blink-count');
//   player2BlinkCount.innerText = Math.min(game.players[1].blinkCount, 10);

//   myFunction(
//     game.players[0].blinkCount,
//     game.players[1].blinkCount,
//     end_or_not
//   );
//   // endgame(game.players[0].blinkCount, game.players[1].blinkCount, end_or_not)
//   // end_or_not = true;
// });



// let winSound = new Audio('../static/sound/win.wav');
// let bgMusic = new Audio('../static/sound/background.mp3');
// // bgMusic.volume = 0.2; // set the volume to 20%
// // winSound.volume = 0.3; // set the volume to 30%
// bgMusic.loop = true;
// bgMusic.play();