let car1 = document.querySelector('.car1');
let car2 = document.querySelector('.car2');
let moveBy = 50;
let countLeft = 0;
let countRight = 0;
let gameEnded = false;


let message = document.createElement('p');
message.style.fontSize = '48px';
message.style.fontWeight = 'bold';
message.style.textAlign = 'center';
message.style.position = 'absolute';
message.style.top = '40%';
message.style.left = '50%';
message.style.transform = 'translate(-50%, -50%)';
message.style.opacity = 0;
document.body.appendChild(message);

let winSound = new Audio('smiley.wav');

window.addEventListener('load', () => {
    setCarPosition();
});

window.addEventListener('resize', () => {
    setCarPosition();
});

function setCarPosition() {
    const screenWidth = window.innerWidth;
    const screenHeight = window.innerHeight;
    const carWidth = car1.offsetWidth;
    const carHeight = car1.offsetHeight;

    // car1.style.position = 'absolute';
    car1.style.left = (screenWidth - carWidth)/ 3  + 'px';
    car1.style.bottom = (screenHeight - carHeight)* 3 / 4 + 'px';

    // car2.style.position = 'absolute';
    car2.style.left = (screenWidth - carWidth) / 3 + 'px';
    car2.style.bottom = (screenHeight - carHeight) * 3 / 4 + 'px';
}

window.addEventListener('keydown', (e) => {
    switch (e.key) {
        case 'ArrowLeft':
            if (!gameEnded && countLeft < 10) {
                car1.style.left = parseInt(car1.style.left) + moveBy + 'px';
                countLeft++;
                if (countLeft === 10) {
                    message.textContent = 'Player 1 wins!';
                    message.style.color = '#e74c3c';
                    message.style.opacity = 1;
                    gameEnded = true;
                    winSound.play();
                    car1.classList.add('winner');
                    setTimeout(() => {
                        car1.classList.remove('winner');
                    }, 5000);
                }
            }
            break;

        case 'ArrowRight':
            if (!gameEnded && countRight < 10) {
                car2.style.left = parseInt(car2.style.left) + moveBy + 'px';
                countRight++;
                if (countRight === 10) {
                    message.textContent = 'Player 2 wins!';
                    message.style.color = '#3498db';
                    message.style.opacity = 1;
                    gameEnded = true;
                    winSound.play();
                    car2.classList.add('winner');
                    setTimeout(() => {
                        car2.classList.remove('winner');
                    }, 5000);
                }
            }
            break;
    }
});
