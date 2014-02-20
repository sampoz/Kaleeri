function getDataFromRuoska() {
    var image = $('#update').find('img')[0];
    "xywh".split("").forEach(function (dir) {
        $('#crop_' + dir).val(image["crop_" + dir]);
    });
}

function flickr() {
    var urlStart = "http://api.flickr.com/services/rest/?method=flickr.photos.search&api_key=acdcbe64b4866c6697d07831ecf14842&tags=";
    var urlEnd = "&safe_search=1&per_page=20&format=json&jsoncallback=?";

    $('#flickr_output').on('click', 'img', function () {
        $('#url').val($(this).attr('src'));
        var singleImage = "<img id='crop_image' src='" + $(this).attr('src').replace("_s.jpg","_z.jpg") + "'>";
        $out.empty().append(singleImage);
        $('#crop_image').ruoska();
    });

    $('#search').keyup(function () {
        var searchField = $('#search').val();
        $.getJSON(urlStart + searchField + urlEnd, function (data) {
            var output = "";

            $.each(data.photos.photo, function (key, val) {
                var url = "http://farm" + val.farm + ".staticflickr.com/" + val.server + "/" + val.id + "_" + val.secret + "_s.jpg";
                output = "<img height='75' width='75' src='" + url + "'>";
            });

            $out = $('#flickr_output');
            $out.append(output);
        });
    });
}