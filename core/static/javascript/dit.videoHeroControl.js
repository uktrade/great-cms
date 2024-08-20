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
        // Prevent autoplay on mobile, code duplicated as toggleVideoPlayPause sees video as 'paused' on init even though it autoplays
        const screenWidth = $(window).width();
        if (screenWidth < 800){
            this.video.removeAttribute('autoplay')
            this.updateButton(this.playClass, 'Play video', 'Play');
            this.controlBtn.setAttribute('aria-pressed', 'false');
            document.getElementById('js-video-status').textContent = 'Video paused';
        }  
    }

    toggleVideoPlayPause() {
        if (this.video.paused) {
            this.video.play();
            this.updateButton(this.pauseClass, 'Pause video', 'Pause');
            this.controlBtn.setAttribute('aria-pressed', 'true');
            document.getElementById('js-video-status').textContent = 'Video playing';
        } else {
            this.video.pause();
            this.updateButton(this.playClass, 'Play video', 'Play');
            this.controlBtn.setAttribute('aria-pressed', 'false');
            document.getElementById('js-video-status').textContent = 'Video paused';
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
    const video = document.getElementById('video-test');
    const controlBtn = document.getElementById('js-video-control');

    if (video) {
        new VideoPlayerController(video, controlBtn);
    }
});
