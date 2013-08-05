// Google Cloud radio player

(function() {

function Player() {
    this._mediaPlayer = document.getElementById('media');
    this._programName = document.getElementById('programName');
    this._storyName = document.getElementById('storyName');
    this._elapsedTime = document.getElementById('elapsedTime');
    this._totalTime = document.getElementById('totalTime');
    this._progress = document.getElementById('progress');
    this._storyId = 0;
    var playPause = document.getElementById('playPause');
    var thumbsUp = document.getElementById('thumbsUp');
    var thumbsDown = document.getElementById('thumbsDown');
    // Hook up the media events
    this._mediaPlayer.addEventListener('timeupdate', this._onProgress.bind(this));
    // Go!
    this._requestNext();
}
Player.prototype._onProgress = function() {
    var hasData = this._mediaPlayer.readyState != 0;
    var currentTime = hasData ? this._mediaPlayer.currentTime : 0;
    var duration = hasData ? this._mediaPlayer.duration : 0;
    var progress = hasData ? (currentTime / duration) : 0;
    this._totalTime.innerText = duration;
    this._elapsedTime.innerText = currentTime;
    this._progress.style.width = '-webkit-calc(' + (progress * 100) + '% - 8px)';
}
Player.prototype._onNextTrack = function(trackInfo) {
    this._storyId = trackInfo.storyId;
    this._programName.innerText = trackInfo.programName;
    this._storyName.innerText = trackInfo.storyName;
    //this._mediaPlayer.src = trackInfo.mediaPath;
    this._mediaPlayer.src = "http://pd.npr.org/anon.npr-mp3/wbur/media/2013/08/20130805_hereandnow_africa-st-louis.mp3";
    this._mediaPlayer.play();
}
Player.prototype._requestNext = function() {
    this._apiCall("GET", "/next", this._onNextTrack.bind(this));
}
Player.prototype._thumbsUp = function() {
    this._apiCall("POST", "/thumbs-up");
}
Player.prototype._thumbsDown = function() {
    var that = this;
    this._apiCall("POST", "/thumbs-down",
        function() { that._onNextTrack(); });
}
Player.prototype._apiCall = function(method, url, callback) {
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = function APICallResponse() {
        console.log('ready state changed', xhr);
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