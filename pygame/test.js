const car1 = document.getElementById("car_1");
const car2 = document.getElementById("car_2");
const roadWidth = document.getElementById("road").clientWidth;
const speed = 8;

let bgMusic = new Audio('/static/sound/background.mp3');
// bgMusic.volume = 0.2; // set the volume to 50%
// winSound.volume = 0.3; // set the volume to 50%
bgMusic.loop = true;
bgMusic.play();

function myFunction(pos1, pos2) {
    car1.style.left = pos1 * speed + "%";
    car2.style.left = pos2 * speed + "%";
}

for (let i = 0; i <= 10; i++) {
    setTimeout(() => {
        myFunction(2, i)
        console.log(i)
    }, 1000 * i)
}