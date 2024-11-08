class VideoPlayerController {
    constructor(video, controlBtn, options = {}) {
        this.video = video;
        this.controlBtn = controlBtn;
        this.playClass = options.playClass || 'great-hero__video-control-play';
        this.pauseClass = options.pauseClass || 'great-hero__video-control-pause';

        this.init();
    }

    init() {
        this.controlBtn.addEventListener('click', () => {
            this.toggleVideoPlayPause();
        });
    }

    toggleVideoPlayPause() {
        if (this.video.paused) {
            this.video.play();
            this.updateButton(this.pauseClass, 'Pause background video', 'Pause background video');
            this.controlBtn.setAttribute('aria-pressed', 'true');
            document.getElementById('js-video-status').textContent = 'Background video playing';
        } else {
            this.video.pause();
            this.updateButton(this.playClass, 'Play background video', 'Play background video');
            this.controlBtn.setAttribute('aria-pressed', 'false');
            document.getElementById('js-video-status').textContent = 'Background video paused';
        }
    }

    updateButton(btnClass, ariaLabel, buttonText) {
        this.controlBtn.classList.remove(this.playClass, this.pauseClass);
        this.controlBtn.classList.add(btnClass);
        this.controlBtn.setAttribute('aria-label', ariaLabel);
        this.controlBtn.querySelector('.great-hero__video-control-icon span').textContent = buttonText;
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const video = document.getElementById('hero-video');
    const controlBtn = document.getElementById('js-video-control');

    if (video) {
        new VideoPlayerController(video, controlBtn);
    }
});
