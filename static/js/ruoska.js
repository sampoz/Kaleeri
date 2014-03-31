/* global HTMLImageElement, jQuery */
(function ($) {
    'use strict';
    function ruoska(elem) {
        var overlay, wrapper;

        if (!(elem instanceof HTMLImageElement)) {
            throw "ruoska can only be used on image elements";
        }

        elem.crop_x = 10;
        elem.crop_y = 10;
        elem.crop_w = elem.width - 20;
        elem.crop_h = elem.height - 20;

        wrapper = $(document.createElement("div")).addClass("ruoska-wrapper");
        $(elem).addClass('ruoska-img')
               .wrap(wrapper);

        // Weird-looking additions or subtractions by one or two are explained by the fact that
        // by default, HTML does not include borders in the actual element size, but users are
        // most probably used to the crop border being included in the crop area.
        overlay = $(document.createElement("div")).addClass("ruoska-overlay");
        overlay.css({
            left: elem.crop_x + 1 + "px",
            top: elem.crop_y + 1 + "px",
            width: elem.crop_w - 2 + "px",
            height: elem.crop_h - 2 + "px"
        });
        overlay.state = null;
        overlay.corner = null;
        overlay.origin_x = 0;
        overlay.origin_y = 0;
        overlay.insertAfter(elem);

        function in_corner(event, margin) {
            var width = overlay.width(),
                height = overlay.height(),
                offset = overlay.offset(),
                x = Math.abs(event.pageX - offset.left),
                y = Math.abs(event.pageY - offset.top);
            margin = margin || 15;
            if (x < margin) {
                if (y < margin) {
                    // Top left
                    return 1;
                }

                if (Math.abs(y - height) < margin) {
                    // Bottom left
                    return 4;
                }
            }

            if (x > width - margin) {
                if (y < margin) {
                    // Top right
                    return 2;
                }

                if (Math.abs(y - height) < margin) {
                    // Bottom right
                    return 3;
                }
            }
            return 0;
        }

        function is_over(event) {
            var offset = overlay.offset(),
                x = event.pageX - offset.left,
                y = event.pageY - offset.top;

            return x >= 0 && x < overlay.width() && y >= 0 && y < overlay.height();
        }

        $(elem).mousemove(
            function (e) {
                var new_x, new_y, new_w, new_h;

                // Dragging
                if (overlay.state === "drag") {
                    // Moving a corner
                    if (overlay.corner) {
                        new_x = overlay.old_x;
                        new_y = overlay.old_y;

                        if (overlay.corner === 1) {
                            // Top left
                            new_x = overlay.old_x + e.pageX - overlay.origin_x;
                            new_y = overlay.old_y + e.pageY - overlay.origin_y;
                            new_w = overlay.old_w - e.pageX + overlay.origin_x;
                            new_h = overlay.old_h - e.pageY + overlay.origin_y;
                        } else if (overlay.corner === 2) {
                            // Top right
                            new_y = overlay.old_y + e.pageY - overlay.origin_y;
                            new_w = overlay.old_w + e.pageX - overlay.origin_x;
                            new_h = overlay.old_h - e.pageY + overlay.origin_y;
                        } else if (overlay.corner === 3) {
                            // Bottom right
                            new_w = overlay.old_w + e.pageX - overlay.origin_x;
                            new_h = overlay.old_h + e.pageY - overlay.origin_y;
                        } else {
                            // Bottom left
                            new_x = overlay.old_x + e.pageX - overlay.origin_x;
                            new_w = overlay.old_w - e.pageX + overlay.origin_x;
                            new_h = overlay.old_h + e.pageY - overlay.origin_y;
                        }

                        overlay.css('left', new_x + 'px')
                               .css('top', new_y + 'px')
                               .css('width', new_w + 'px')
                               .css('height', new_h + 'px');
                        this.crop_x = new_x - 1;
                        this.crop_y = new_y - 1;
                        this.crop_w = new_w + 2;
                        this.crop_y = new_h + 2;
                    } else {
                        // Moving the whole overlay
                        // Clamp the overlay to [1, img.width - overlay.width - 2] and similarly for height,
                        // -2 comes from the borders as we want the borders to be included
                        new_x = overlay.old_x + e.pageX - overlay.origin_x;
                        new_x = Math.min(Math.max(1, new_x), this.width - overlay.width() - 2);
                        new_y = overlay.old_y + e.pageY - overlay.origin_y;
                        new_y = Math.min(Math.max(1, new_y), this.height - overlay.height() - 2);
                        $(overlay).css('left', new_x + 'px')
                                  .css('top', new_y + 'px');

                        this.crop_x = new_x - 1;
                        this.crop_y = new_y - 1;
                    }
                } else {
                    // Hovering
                    overlay.corner = in_corner(e);

                    if (overlay.corner) {
                        // Near a corner
                        overlay.removeClass('ruoska-drag');
                        if (overlay.corner % 2) {
                            $(elem).addClass('ruoska-resize-nw');
                            overlay.addClass('ruoska-resize-nw');
                        } else {
                            $(elem).addClass('ruoska-resize-ne');
                            overlay.addClass('ruoska-resize-ne');
                        }
                    } else {
                        // In the middle
                        overlay.corner = null;
                        $(elem).removeClass('ruoska-resize-nw')
                               .removeClass('ruoska-resize-ne');
                        overlay.removeClass('ruoska-resize-nw')
                               .removeClass('ruoska-resize-ne')
                               .addClass('ruoska-drag');
                    }
                }

                // Block dragging
                e.preventDefault();
            }
        );

        $(elem).mousedown(
            function (e) {
                if (is_over(e) || in_corner(e)) {
                    overlay.state = "drag";
                    overlay.origin_x = e.pageX;
                    overlay.origin_y = e.pageY;
                    overlay.old_x = parseInt(overlay.css('left').substring(0, overlay.css('left').length - 2), 10);
                    overlay.old_y = parseInt(overlay.css('top').substring(0, overlay.css('top').length - 2), 10);
                    overlay.old_w = overlay.width();
                    overlay.old_h = overlay.height();
                }
                e.preventDefault();
            }
        );

        $(elem).mouseup(
            function () {
                overlay.state = null;
            }
        );

        // Delegate the overlay's functions to the image element's ones
        overlay.mousemove(function (e) { $(elem).trigger(e); });
        overlay.mousedown(function (e) { $(elem).trigger(e); });
        overlay.mouseup(function (e) { $(elem).trigger(e); });

        // Block dragging images
        wrapper.on('dragstart', 'img', function (event) { event.preventDefault(); });
        $(elem).attr('draggable', "false");

        elem.ruoska_overlay = overlay[0];
        return elem;
    }

    $.fn.ruoska = function () {
        return this.each(
            function (_i, e) {
                ruoska(e);
            }
        );
    };
}(jQuery));