// Video Component Functionality.
// Requires...
// dit.js
// dit.class.Modal.js

dit.components.video = (new function() {

  var VIDEO_COMPONENT = this;

  // Constants
  var CSS_CLASS_CONTAINER = "video-container";
  var VIDEO_CLOSE_BUTTON_ID = "campaign-section-videoplayer-close";
  var SELECTOR_ACTIVATOR = "[data-node='videoactivator']";
  var TYPE_VIDEO = "video";
  var TYPE_IFRAME = "iframe";
  var TRANSCRIPT = '#campaign-video-transcript';
  var TRANSCRIPT_TEXT = '#campaign-video-transcript-text';
  var $video = null;


  /* Contructor
   * Modal dialog enhancement specifically for video display.
   * @$dialog (jQuery node) Element containing video/iframe.
   * @options (Object) Configuration (see classes.Modal)
   **/
  function VideoDialog($dialog, options) {
    dit.classes.Modal.call(this, $dialog, options);
  }

  VideoDialog.loadWithVideo = function(src) {
    $video = $("<video controls autoplay></video>");
    var format = src.replace(/^.*\.([a-z0-9/]+)$/, "$1");
    var $source = $("<source src=\"" + src + "\" type=\"video/" + format  + "\">");
    $video.append($source);
    this.setContent([$video, $(TRANSCRIPT)]);
  }

  VideoDialog.loadWithIframe = function(src) {
    var $iframe = $("<iframe src=\"" + src + "\"></iframe>");
    this.setContent($iframe);
  }

  VideoDialog.activate = function() {
    var $activator = $(this.activator);
    var type = $activator.data("element");
    var url = $activator.attr("href") || $activator.data("src");

    $(TRANSCRIPT).css({
      display: 'block'
    });
    switch(type) {
      case TYPE_VIDEO:
        VideoDialog.loadWithVideo.call(this, url);
        break;
      case TYPE_IFRAME:
        VideoDialog.loadWithIframe.call(this, url);
        break;
      default:
        type = null;
    }

    if(type) {
      this.resize();
    }
  }

  VideoDialog.prototype = new dit.classes.Modal;


  VideoDialog.prototype.open = function() {
    $('body').addClass('modal-open');
    VideoDialog.activate.call(this);
    dit.classes.Modal.prototype.open.call(this);
    bindEvents();
    setTranscriptHeight();
    $('video',this.$container).focus();
  }

  VideoDialog.prototype.resize = function() {
    var width = $(window).width();
    var height = $(window).height();
    var $iframe = $("iframe", this.$container);
    var sizes = [
      [320, 240],
      [640, 360],
      [853, 480],
      [1280, 720],
      [1920, 1080]
    ];

    var i = 0;
    var size;

    do {
      size = sizes[i],
      i++;
    } while (i < sizes.length && sizes[i][0] <= width && sizes[i][1] <= height);

    $iframe.attr("width", size[0]);
    $iframe.attr("height", size[1]);
  }

  function createContainer() {
    var $container = $(document.createElement("div"));
    $container.addClass(CSS_CLASS_CONTAINER);
    return $container;
  }

  function setTranscriptHeight() {
    var videoHeight, transcript_height;
    if($video.length) {
      videoHeight = $video.height();
      transcript_height = (window.innerHeight - videoHeight) - 130;

      $(TRANSCRIPT_TEXT).css({
        height: transcript_height
      });
    }
  }

  function bindActivators($activators) {
    $activators.on("click keydown", function(e) {
  });


  }

  function onClose() {
    $('body').removeClass('modal-open');
    $(TRANSCRIPT).css({
        display: 'none'
    });
    this.$container.find('video').each(function(index, video) {
      video.pause();
    });
    unbindEvents();
  }
  function bindEvents() {
    $(window).on('resize orientationchange', function() {
      setTranscriptHeight();
    });
  }

  function unbindEvents() {
    $(window).off('resize orientationchange');
  }



  // Public
  this.init = function() {
    var $activators = $(SELECTOR_ACTIVATOR);
    var $container = createContainer();
    $video = $container.find('video');

    if($activators.length) {
      $(document.body).append($container);
      new VideoDialog($container, {
        $activators: $activators,
        closeButtonId: VIDEO_CLOSE_BUTTON_ID,
        onClose: onClose
      });
    }

    delete self.init; // Run once fuction.
  }
});
