const canvas = document.getElementById('canvas');
const ctx = canvas.getContext('2d');
canvas.width = window.innerWidth;
canvas.height = window.innerHeight;

let particles = [];
const properties = {
    bgColor: 'rgba(255, 255, 255, 1)',
    particleColor: 'rgba(107, 91, 149, 0.5)',
    particleRadius: 3,
    particleCount: 60,
    particleMaxVelocity: 0.5,
    lineLength: 150,
    particleLife: 6
};

class Particle {
    constructor() {
        this.x = Math.random() * canvas.width;
        this.y = Math.random() * canvas.height;
        this.velocityX = Math.random() * (properties.particleMaxVelocity * 2) - properties.particleMaxVelocity;
        this.velocityY = Math.random() * (properties.particleMaxVelocity * 2) - properties.particleMaxVelocity;
        //this.life = 900;
    }

    position() {
        this.x + this.velocityX > canvas.width && this.velocityX > 0 || this.x + this.velocityX < 0 && this.velocityX < 0 ? this.velocityX *= -1 : this.velocityX;
        this.y + this.velocityY > canvas.height && this.velocityY > 0 || this.y + this.velocityY < 0 && this.velocityY < 0 ? this.velocityY *= -1 : this.velocityY;
        this.x += this.velocityX;
        this.y += this.velocityY;
    }

    reDraw() {
        ctx.beginPath();
        ctx.arc(this.x, this.y, properties.particleRadius, 0, Math.PI * 2);
        ctx.closePath();
        ctx.fillStyle = properties.particleColor;
        ctx.fill();
    }

    reCalculateLife() {
        if (this.life < 1) {
            this.x = Math.random() * canvas.width;
            this.y = Math.random() * canvas.height;
            this.velocityX = Math.random() * (properties.particleMaxVelocity * 2) - properties.particleMaxVelocity;
            this.velocityY = Math.random() * (properties.particleMaxVelocity * 2) - properties.particleMaxVelocity;
            this.life = Math.random() * properties.particleLife * 60;
        }
        this.life--;
    }
}

function reDrawBackground() {
    ctx.fillStyle = properties.bgColor;
    ctx.fillRect(0, 0, canvas.width, canvas.height);
}

function drawLines() {
    let x1, y1, x2, y2, length, opacity;
    for (let i in particles) {
        for (let j in particles) {
            x1 = particles[i].x;
            y1 = particles[i].y;
            x2 = particles[j].x;
            y2 = particles[j].y;
            length = Math.sqrt(Math.pow(x2 - x1, 2) + Math.pow(y2 - y1, 2));
            if (length < properties.lineLength) {
                opacity = 1 - length / properties.lineLength;
                ctx.lineWidth = '0.5';
                ctx.strokeStyle = 'rgba(107, 91, 149, '+ opacity +')';
                ctx.beginPath();
                ctx.moveTo(x1, y1);
                ctx.lineTo(x2, y2);
                ctx.closePath();
                ctx.stroke();
            }
        }
    }
}

function reDrawParticles() {
    for (let i in particles) {
        particles[i].reCalculateLife();
        particles[i].position();
        particles[i].reDraw();
    }
}

function loop() {
    reDrawBackground();
    reDrawParticles();
    drawLines();
    requestAnimationFrame(loop);
}

function init() {
    for (let i = 0; i < properties.particleCount; i++) {
        particles.push(new Particle);
    }
    loop();
}

init();

window.onresize = function() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
}

canvas.addEventListener('mousemove', function(e) {
    let mouseX = e.clientX;
    let mouseY = e.clientY;

    properties.particleColor = 'rgba(107, 91, 149, 1)';
    for (let i in particles) {
        if (Math.abs(mouseX - particles[i].x) < 30 && Math.abs(mouseY - particles[i].y) < 30) {
            particles[i].velocityX = (particles[i].x - mouseX) / 10;
            particles[i].velocityY = (particles[i].y - mouseY) / 10;
        }
    }
});

canvas.addEventListener('mouseout', function() {
    properties.particleColor = 'rgba(107, 91, 149, 0.5)';
    for (let i in particles) {
        particles[i].velocityX = Math.random() * (properties.particleMaxVelocity * 2) - properties.particleMaxVelocity;
        particles[i].velocityY = Math.random() * (properties.particleMaxVelocity * 2) - properties.particleMaxVelocity;
    }
});
