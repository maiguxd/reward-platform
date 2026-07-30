document.addEventListener('DOMContentLoaded', function() {
    const canvas = document.createElement('canvas');
    canvas.id = 'particles-canvas';
    document.body.prepend(canvas);

    const ctx = canvas.getContext('2d');
    let particles = [];
    let mouseX = 0;
    let mouseY = 0;

    function resize() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }
    resize();
    window.addEventListener('resize', resize);

    document.addEventListener('mousemove', function(e) {
        mouseX = e.clientX;
        mouseY = e.clientY;
    });

    class Particle {
        constructor() {
            this.reset();
        }

        reset() {
            this.x = Math.random() * canvas.width;
            this.y = Math.random() * canvas.height;
            this.size = Math.random() * 2.5 + 0.5;
            this.speedX = (Math.random() - 0.5) * 0.5;
            this.speedY = (Math.random() - 0.5) * 0.5;
            this.opacity = Math.random() * 0.5 + 0.15;
            this.hue = Math.random() > 0.5 ? 150 : 230;
            this.life = 0;
            this.maxLife = Math.random() * 300 + 200;
        }

        update() {
            this.x += this.speedX;
            this.y += this.speedY;

            const dx = mouseX - this.x;
            const dy = mouseY - this.y;
            const dist = Math.sqrt(dx * dx + dy * dy);
            if (dist < 150) {
                const force = (150 - dist) / 150;
                this.speedX -= (dx / dist) * force * 0.02;
                this.speedY -= (dy / dist) * force * 0.02;
            }

            this.speedX *= 0.99;
            this.speedY *= 0.99;

            this.life++;
            if (this.life > this.maxLife) {
                this.reset();
            }

            if (this.x < 0 || this.x > canvas.width ||
                this.y < 0 || this.y > canvas.height) {
                this.reset();
            }
        }

        draw() {
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.size, 0, Math.PI * 2);
            const color = this.hue === 150 ? '0, 255, 136' : '88, 101, 242';
            ctx.fillStyle = `rgba(${color}, ${this.opacity})`;
            ctx.fill();

            if (this.size > 1.5) {
                ctx.shadowBlur = 10;
                ctx.shadowColor = this.hue === 150 ? 'rgba(0, 255, 136, 0.3)' : 'rgba(88, 101, 242, 0.3)';
                ctx.fill();
                ctx.shadowBlur = 0;
            }
        }
    }

    for (let i = 0; i < 80; i++) {
        particles.push(new Particle());
    }

    let lastTime = 0;
    function animate(time) {
        const delta = time - lastTime;
        lastTime = time;

        ctx.clearRect(0, 0, canvas.width, canvas.height);

        for (let p of particles) {
            p.update();
            p.draw();
        }

        ctx.strokeStyle = 'rgba(0, 255, 136, 0.03)';
        ctx.lineWidth = 0.5;

        for (let i = 0; i < particles.length; i++) {
            for (let j = i + 1; j < particles.length; j++) {
                const dx = particles[i].x - particles[j].x;
                const dy = particles[i].y - particles[j].y;
                const dist = Math.sqrt(dx * dx + dy * dy);
                if (dist < 120) {
                    const alpha = (1 - dist / 120) * 0.15;
                    ctx.strokeStyle = `rgba(0, 255, 136, ${alpha})`;
                    ctx.beginPath();
                    ctx.moveTo(particles[i].x, particles[i].y);
                    ctx.lineTo(particles[j].x, particles[j].y);
                    ctx.stroke();
                }
            }
        }

        requestAnimationFrame(animate);
    }

    requestAnimationFrame(animate);
});
