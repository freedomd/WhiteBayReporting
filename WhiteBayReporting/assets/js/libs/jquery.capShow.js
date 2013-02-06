(function($) {
	$.fn.capshow = function(options) {
		var opts = $.extend({}, $.fn.capshow.defaults, options);
		return this.each(function() {
			$this = $(this);
			var o = $.meta ? $.extend({}, opts, $this.data()) : opts;
			
			if(!o.showcaption)	$this.find('.sh_caption').css('display','none');
			else $this.find('.sh_text').css('display','none');
				
			var _img = $this.find('.sh_img');
			var w = _img.css('width');
			var h = _img.css('height');
			$('.sh_caption',$this).css({'color':o.caption_color,'background-color':o.caption_bgcolor,'bottom':'0px','width':w});
			$('.overlay',$this).css('background-color',o.overlay_bgcolor);
			$this.hover(
				function () {
					if((navigator.appVersion).indexOf('MSIE 7.0') > 0)
						$('.overlay',$(this)).show();
					else
						$('.overlay',$(this)).fadeIn();
					if(!o.showcaption)
						$(this).find('.sh_caption').slideDown(0);
					else
						$('.sh_text',$(this)).slideDown(0);	
				},
				function () {
					if((navigator.appVersion).indexOf('MSIE 7.0') > 0)
						$('.overlay',$(this)).hide();
					else
						$('.overlay',$(this)).fadeOut();
					if(!o.showcaption)
						$(this).find('.sh_caption').slideUp(0);
					else
						$('.sh_text',$(this)).slideUp(0);
				}
			);
		});
	};
	$.fn.capshow.defaults = {
		caption_color	: 'white',
		caption_bgcolor	: 'black',
		overlay_bgcolor : 'blue',
		border			: '1px solid #fff',
		showcaption	    : true
	};
})(jQuery);
