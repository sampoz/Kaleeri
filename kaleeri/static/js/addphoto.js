(function ($) {
    'use strict';
    function addUrl(url) {
        $('#url').val(url);
    }

    function getDataFromRuoska() {
        var image = $('#update').find('img')[0];
        "xywh".split("").forEach(function (dir) {
            $('#crop_' + dir).val(image["crop_" + dir]);
        });
    }

    function flickr() {

    var urlStart = "http://api.flickr.com/services/rest/?method=flickr.photos.search&api_key=acdcbe64b4866c6697d07831ecf14842&tags=";
    var urlEnd = "&safe_search=1&per_page=20&format=json&jsoncallback=?";

    $(document).ready(function () {
        $('#search').keyup(function () {
            var searchField = $('#search').val();
            $.getJSON(urlStart + searchField + urlEnd, function (data) {
                var output = "";
                $.each(data, function (key, val) {
                    var images = data;
                    var url = "http://farm" + data.photos.photo[0].farm + ".staticflickr.com/" + data.photos.photo[0].server + "/" + data.photos.photo[0].id + "_" + data.photos.photo[0].secret + "_s.jpg";
                    output = "<img height='75' width='75' src='" + url + "'>";
                });
                $('#update').append(output);
                $('img').click(function () {
                    var ruoskaThis = $(this).attr('src');
                    addUrl(ruoskaThis);
                    var $update = $('#update');
                    $update.empty();
                    var singleImage=  "<img height='650' width='650' src='" + ruoskaThis.replace("_s.jpg","_z.jpg")+"' >";
                    $update.append(singleImage);
                    $update.find('img').ruoska();
                });
            });
        });
    });
    }
})