/*!
  Pinto jQuery Plugin
  @name pinto.js
  @description Lightweight and customizable jQuery plugin for creating pinterest like responsive grid layout
  @author Max Lawrence 
  @version 1.0.0
  @date 08.05.2015
  @category jQuery plugin
  @copyright (c) 2015 Max Lawrence (http://www.topbits.net)
  @license Licensed under the MIT (http://www.opensource.org/licenses/mit-license.php) license.
*/
(function($){
	'use strict';
	var defaultOptions = {
		itemSelector: '> div',		// block identificator;
		itemWidth: 220,				// width of one grid block in pixels;
		marginX: 10,				// width spacing between blocks in pixels;
        marginY: 10, 				// height spacing between blocks in pixels;
		align: 'left',			    // blocks alignment - 'left', 'right' or 'center';
		fitWidth: true,			    // adjusts block width to create optimal layout based on container size;
		animate: true,				// CSS animation when updating layout; 
		autoResize: true,			// updates layout after browser is resized;
		resizeDelay: 50				// time in milliseconds between browser resize and layout update;
	};
	
	$.fn.pinto = function(options) {
		var $this = $(this),
			settings = $.extend(defaultOptions, options);
		
		$this.css('position', 'relative');
		
		var getSmallestIndex = function (a) {
			var index = 0;
            for (var i = 1, len = a.length; i < len; i++) {
				if (a[i] < a[index]) index = i;
            }
            return index;
		};
				
		var doLayout = function (){
			if (!$this.is(":visible")) { return; }
						
			var trans = (settings.animate ? 'top 0.5s, left 0.5s': 'none'),
			items = $this.find(settings.itemSelector),
			width = $this.innerWidth(),
			marginX = parseInt(settings.marginX || 0),
			marginY = parseInt(settings.marginY || 0),
			itemWidth = settings.itemWidth,
			colsCount = Math.max(Math.floor(width/(itemWidth + marginX)),1),
			cols = [];
			
			var i = colsCount;
			while(i--) cols.push(0);
			
			var offset = 0;
			if(settings.fitWidth) {
				itemWidth += Math.floor(0.5 + (width - (colsCount * (itemWidth + marginX)))/colsCount);
			} else {
				// calculate the offset based on the alignment of columns to the parent container
				if (settings.align === 'center') {
					offset += Math.floor(0.5 + (width - (colsCount * (itemWidth + marginX))) >> 1);
				} else if (settings.align === 'right') {
					offset += Math.floor(0.5 + width - (colsCount * (itemWidth + marginX)));
				};
			};
			
			items.each(function(index, item) {
				var $item = $(item),
					i = getSmallestIndex(cols);
					
				$item.css({
					position: 'absolute',
					top: cols[i] + marginY/2 + 'px',
                    left: (itemWidth + marginX) * i + offset + 'px',
					width: itemWidth,
                    margin: marginY/2 + 'px ' + marginX/2 + 'px',             
					transition: trans
				});
				
				cols[i] += $item.innerHeight() + marginY;
            });
			
			var height=0;
			i = colsCount;
			while(i--) if(cols[i]>height) height = cols[i];
			$this.css({height:height});
		};
		
		var onResizeTimer = null;
		var onResize = function() {
			clearTimeout(onResizeTimer);
			onResizeTimer = setTimeout(doLayout, settings.resizeDelay);
		};
		
		doLayout();
		
		if (settings.autoResize) {
			var resize =  $(window).on("resize", onResize);
			$this.on('remove', resize.unbind);
        };
	};
})(window.jQuery);