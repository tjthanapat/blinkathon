
const car1 = document.getElementById("car_1");
const car2 = document.getElementById("car_2");
const roadWidth = document.getElementById("road").clientWidth;
const carWidth = car1.clientWidth;

let car1Pos = 0;
let car2Pos = 0;
let counter1 = 0; // counter for player 1
let counter2 = 0; // counter for player 2
let speed = 8;
let winSound = new Audio('sound/win.wav');
let bgMusic = new Audio('sound/background.mp3');
bgMusic.volume = 0.0; // set the volume to 50%
winSound.volume = 0.5; // set the volume to 50%
bgMusic.loop = true;
bgMusic.play();

const player1 = "P1";
const player2 = "P2";



const handleKeyDown = (event) => {

    if (event.key === "ArrowLeft") {
        car1Pos = Math.max(car1Pos + speed, 0);
        car1.style.left = car1Pos + speed + "%";
        counter1++; // increment counter for player 1
    } else if (event.key === "ArrowRight") {
        car2Pos = Math.max(car2Pos + speed, 0);
        car2.style.left = car2Pos + speed + "%";
        counter2++; // increment counter for player 2
    }

    if (counter1 >= 10 || counter2 >= 10) { // check if either player has reached 10
        document.removeEventListener("keydown", handleKeyDown);
        const winner = document.createElement("p");
        winSound.play();
        bgMusic.pause();
        if (counter1 > counter2) { // check which player has moved farther
            winner.textContent = `${player1} wins!`;
        } else {
            winner.textContent = `${player2} wins!`;
        }
        document.body.appendChild(winner);
        winner.addEventListener('animationend', () => {
            winSound.pause();
        })
    }
};

document.addEventListener("keydown", handleKeyDown);




const countdownEl = document.getElementById("countdown");
const startBtn = document.getElementById("start-btn");
const gameContainer = document.getElementById("game-container");

// hide the game container initially
gameContainer.style.display = "none";

// function to start the countdown
const startCountdown = () => {
    let count = 3;
    countdownEl.textContent = count;
    const intervalId = setInterval(() => {
        count--;
        if (count === 0) {
            countdownEl.textContent = "Go!";
            clearInterval(intervalId);
            setTimeout(() => {
                countdownEl.style.display = "none";
                gameContainer.style.display = "block";
            }, 500);
        } else {
            countdownEl.textContent = count;
        }
    }, 1000);
};

startBtn.addEventListener("click", () => {
    startBtn.style.display = "none";
    countdownEl.style.display = "block";
    startCountdown();
});


