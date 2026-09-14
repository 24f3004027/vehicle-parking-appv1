/**
 * Interactive Watery Fluid Mesh Canvas Engine
 * Generates organic liquid wave particles, floating mesh nodes, and interactive cursor ripples.
 * Dynamically responds to Light and Dark mode themes.
 */

document.addEventListener("DOMContentLoaded", function () {
    const canvas = document.createElement("canvas");
    canvas.id = "water-canvas";
    canvas.style.position = "fixed";
    canvas.style.top = "0";
    canvas.style.left = "0";
    canvas.style.width = "100vw";
    canvas.style.height = "100vh";
    canvas.style.pointerEvents = "none";
    canvas.style.zIndex = "-1";
    document.body.prepend(canvas);

    const ctx = canvas.getContext("2d");
    let width, height;
    let particles = [];
    let ripples = [];
    let mouse = { x: null, y: null, radius: 180 };

    function resize() {
        width = canvas.width = window.innerWidth;
        height = canvas.height = window.innerHeight;
        initParticles();
    }

    window.addEventListener("resize", resize);
    window.addEventListener("mousemove", function (e) {
        mouse.x = e.clientX;
        mouse.y = e.clientY;
        if (Math.random() < 0.25) {
            ripples.push({
                x: e.clientX,
                y: e.clientY,
                radius: 5,
                maxRadius: 40 + Math.random() * 30,
                alpha: 0.6
            });
        }
    });

    window.addEventListener("mouseleave", function () {
        mouse.x = null;
        mouse.y = null;
    });

    class Particle {
        constructor() {
            this.x = Math.random() * width;
            this.y = Math.random() * height;
            this.vx = (Math.random() - 0.5) * 0.8;
            this.vy = (Math.random() - 0.5) * 0.8;
            this.radius = Math.random() * 3 + 1.5;
            this.baseAlpha = Math.random() * 0.4 + 0.2;
        }

        update() {
            this.x += this.vx;
            this.y += this.vy;

            if (this.x < 0 || this.x > width) this.vx *= -1;
            if (this.y < 0 || this.y > height) this.vy *= -1;

            // Mouse interaction push
            if (mouse.x !== null && mouse.y !== null) {
                let dx = mouse.x - this.x;
                let dy = mouse.y - this.y;
                let dist = Math.sqrt(dx * dx + dy * dy);
                if (dist < mouse.radius) {
                    let force = (mouse.radius - dist) / mouse.radius;
                    this.x -= (dx / dist) * force * 3;
                    this.y -= (dy / dist) * force * 3;
                }
            }
        }

        draw(theme) {
            ctx.beginPath();
            ctx.arc(this.x, this.y, this.radius, 0, Math.PI * 2);
            if (theme === 'dark') {
                ctx.fillStyle = `rgba(56, 189, 248, ${this.baseAlpha})`;
            } else {
                ctx.fillStyle = `rgba(2, 132, 199, ${this.baseAlpha * 0.8})`;
            }
            ctx.fill();
        }
    }

    function initParticles() {
        particles = [];
        const count = Math.floor((width * height) / 14000);
        for (let i = 0; i < count; i++) {
            particles.push(new Particle());
        }
    }

    function drawMesh(theme) {
        const strokeColor = theme === 'dark' ? 'rgba(56, 189, 248, ' : 'rgba(2, 132, 199, ';
        const maxDist = 130;

        for (let i = 0; i < particles.length; i++) {
            for (let j = i + 1; j < particles.length; j++) {
                let dx = particles[i].x - particles[j].x;
                let dy = particles[i].y - particles[j].y;
                let dist = Math.sqrt(dx * dx + dy * dy);

                if (dist < maxDist) {
                    let alpha = (1 - dist / maxDist) * 0.25;
                    ctx.beginPath();
                    ctx.moveTo(particles[i].x, particles[i].y);
                    ctx.lineTo(particles[j].x, particles[j].y);
                    ctx.strokeStyle = strokeColor + alpha + ')';
                    ctx.lineWidth = 1;
                    ctx.stroke();
                }
            }
        }
    }

    function drawRipples(theme) {
        const rippleColor = theme === 'dark' ? 'rgba(56, 189, 248, ' : 'rgba(14, 165, 233, ';
        for (let i = ripples.length - 1; i >= 0; i--) {
            let r = ripples[i];
            r.radius += 1.5;
            r.alpha -= 0.015;

            if (r.alpha <= 0 || r.radius >= r.maxRadius) {
                ripples.splice(i, 1);
                continue;
            }

            ctx.beginPath();
            ctx.arc(r.x, r.y, r.radius, 0, Math.PI * 2);
            ctx.strokeStyle = rippleColor + r.alpha + ')';
            ctx.lineWidth = 1.5;
            ctx.stroke();
        }
    }

    function animate() {
        ctx.clearRect(0, 0, width, height);

        const currentTheme = document.documentElement.getAttribute('data-bs-theme') || 'dark';

        // Draw ambient gradient wash
        let grad = ctx.createRadialGradient(width / 2, height / 2, 100, width / 2, height / 2, Math.max(width, height));
        if (currentTheme === 'dark') {
            grad.addColorStop(0, 'rgba(11, 24, 46, 0.4)');
            grad.addColorStop(1, 'rgba(7, 13, 26, 0.9)');
        } else {
            grad.addColorStop(0, 'rgba(224, 242, 254, 0.4)');
            grad.addColorStop(1, 'rgba(186, 230, 253, 0.7)');
        }
        ctx.fillStyle = grad;
        ctx.fillRect(0, 0, width, height);

        particles.forEach(p => {
            p.update();
            p.draw(currentTheme);
        });

        drawMesh(currentTheme);
        drawRipples(currentTheme);

        requestAnimationFrame(animate);
    }

    resize();
    animate();
});
