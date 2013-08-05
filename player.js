// Google Cloud radio player

(function() {

function Player() {
    this._mediaPlayer = document.getElementById('media');
    this._elapsedTime = document.getElementById('elapsedTime');
    this._totalTime = document.getElementById('totalTime');
    this._progress = document.getElementById('progress');
    this._stage = document.getElementById('stage');
    this._storyId = 0;
    var playPause = document.getElementById('playPause');
    var thumbsUp = document.getElementById('thumbsUp');
    var thumbsDown = document.getElementById('thumbsDown');
    var next = document.getElementById('next');
    // Hook up the media events
    this._mediaPlayer.addEventListener('timeupdate', this._onProgress.bind(this));
    this._mediaPlayer.addEventListener('playing', this._onStateChange.bind(this));
    this._mediaPlayer.addEventListener('pause', this._onStateChange.bind(this));
    // Hook up the buttons
    var media = this._mediaPlayer;
    playPause.addEventListener('click', function() { if (media.paused) media.play(); else media.pause(); }, true);
    thumbsUp.addEventListener('click', this._thumbsUp.bind(this), true);
    thumbsDown.addEventListener('click', this._thumbsDown.bind(this), true);
    next.addEventListener('click', this._requestNext.bind(this), true);
    // Animation listener to remove old tracks.
    this._stage.addEventListener('webkitAnimationEnd', this._animationEnd.bind(this), true);
    // Go!
    this._requestNext();
}
Player.prototype._onProgress = function() {
    var hasData = this._mediaPlayer.readyState != 0;
    var currentTime = hasData ? this._mediaPlayer.currentTime : 0;
    var duration = hasData ? this._mediaPlayer.duration : 0;
    var progress = hasData ? (currentTime / duration) : 0;

    function formatTime(t) {
        var rounded = Math.round(t);
        var minutes = Math.floor(t / 60);
        var seconds = rounded % 60;
        if (seconds < 10) seconds = "0" + seconds;
        return minutes + ":" + seconds;
    }

    this._totalTime.innerText = formatTime(duration);
    this._elapsedTime.innerText = formatTime(currentTime);
    this._progress.style.width = '-webkit-calc(' + (progress * 100) + '% - 8px)';
}
Player.prototype._onStateChange = function() {
    var playing = !this._mediaPlayer.paused;
    if (playing) document.body.classList.add('playing');
    else document.body.classList.remove('playing');
}
Player.prototype._onNextTrack = function(trackInfo) {
    this._storyId = trackInfo.story_id;
    var track = document.createElement('div');
    track.className = 'track';
    var programName = document.createElement('div');
    programName.className = 'programName';
    var storyName = document.createElement('div');
    storyName.className = 'storyName';
    var image = document.createElement('div');
    image.className = 'image';
    track.appendChild(image);
    track.appendChild(programName);
    track.appendChild(storyName);

    if (trackInfo.image_url) image.style.backgroundImage = 'url(' + trackInfo.image_url + ')';
    if (trackInfo.program_name) programName.innerText = trackInfo.program_name;
    if (trackInfo.story_title) storyName.innerText = trackInfo.story_title;

    if (this._lastTrack) this._lastTrack.style.webkitAnimationName = 'outgoing';
    this._lastTrack = track;

    this._stage.appendChild(track);

    this._mediaPlayer.src = trackInfo.audio_url;
    this._mediaPlayer.play();
}
Player.prototype._animationEnd = function(e) {
    if (e.target.style.webkitAnimationName == 'outgoing') {
        this._stage.removeChild(e.target);
    }
}
Player.prototype._requestNext = function() {
    this._apiCall("GET", "/next", this._onNextTrack.bind(this));
}
Player.prototype._thumbsUp = function() {
    this._apiCall("GET", "/thumbs-up?storyId=" + this._storyId);
}
Player.prototype._thumbsDown = function() {
    var that = this;
    this._apiCall("GET", "/thumbs-down?storyId=" + this._storyId,
        function() { that._requestNext(); });
}
Player.prototype._apiCall = function(method, url, callback) {
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function APICallResponse() {
        if (xhr.readyState != 4) return;
        if (xhr.status == 200) {
            if (callback) callback(JSON.parse(xhr.responseText));
            return;
        }
        console.log('failed call to ' + url, xhr);
    }
    xhr.open(method, url, true);
    xhr.send();
}

new Player();
})();
