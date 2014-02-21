var searchTimer = null;
var currentSearch = "";
var currentPage = 1;

function getDataFromRuoska() {
    var image = $('#crop_image')[0];
    "xywh".split("").forEach(function (dir) {
        $('#crop_' + dir).val(image["crop_" + dir]);
    });
}

function loadFlickr(query, page) {
    var urlStart = "http://api.flickr.com/services/rest/?method=flickr.photos.search&api_key=acdcbe64b4866c6697d07831ecf14842&tags=";
    var urlEnd = "&safe_search=1&per_page=5&format=json&jsoncallback=?&page=";
    currentSearch = query;
    currentPage = page;

    var i;
    for (i = 0; i < 5; i++) {
        $('#flickr_img' + i).addClass('loading').empty();
    }

    $('#flickr_output').show();

    $.getJSON(urlStart + encodeURIComponent(query) + urlEnd + page, function (data) {
        var output = "";

        i = 0;
        $.each(data.photos.photo, function (key, val) {
            var url = "http://farm" + val.farm + ".staticflickr.com/" + val.server + "/" + val.id + "_" + val.secret + "_s.jpg";
            output = "<img width=160 height=120 src='" + url + "'>";
            $('#flickr_img' + i).removeClass('loading').html(output);
            i++;
        });

        for (; i < 5; i++) { $('#flickr_img' + i).empty(); }
    });
}

function flickr() {
    $('#flickr_output').hide().on('click', 'img', function () {
        $('#url').val($(this).attr('src'));
        var img = "<img id='crop_image' src='" + $(this).attr('src').replace("_s.jpg","_z.jpg") + "'>";
        $("#crop_container").append(img).show();
        $("#flickr_output").hide();
        $('#crop_image').load(function () { $('#crop_image').ruoska(); });
    });

    $('#crop_container').hide();

    $('#album_submit').click(function () {
        getDataFromRuoska();
    });

    $('#flickr_previous').click(function () {
        if (page == 1) { return; }
        loadFlickr(currentSearch, currentPage - 1);
    });

    $('#flickr_next').click(function () {
        loadFlickr(currentSearch, currentPage + 1);
    });

    $('#search').keyup(function () {
        clearTimeout(searchTimer);
        searchTimer = setTimeout(function () { loadFlickr($('#search').val(), 1) }, 500);
    });
}