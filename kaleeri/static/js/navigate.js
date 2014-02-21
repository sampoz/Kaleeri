window.Kaleeri = {
    "templates": {},
    "urls": {
        create_album: "/",
        add_picture: ""
    },
    "currentAlbum": null,
    "parseAlbumId": function () {
        var $add_button = $("#add-button");
        if ($add_button.length) {
            var add_photo_url = $add_button.attr("href");
            var albumNumber = /album\/(\d+)\//.exec(location.href);
            $add_button.attr("href", add_photo_url + albumNumber);
        }
    }
};

Handlebars.registerHelper('plural', function(num) {
    if (num == 1) { return ""; }
    return "s";
});

window.addEventListener("hashchange", loadHash);

function loadHash() {
    var state = location.hash.substr(1).split("/");
    var ret;

    if (state[0] == "" || state[0] == "main") {
        ret = {"view": "main", "parameter": {}};
    }

    else if (state[0] == "album") {
        if (state.length == 7) {
            ret = {
                view: "addPhoto",
                parameter: {
                    albumId: parseInt(state[1], 10),
                    pageNumber: parseInt(state[3], 10),
                    photoNumber: parseInt(state[5], 10)
                }
            };
        } else if (state.length == 4 || state.length == 5) {
            ret = {
                view: "albumPhotos",
                parameter: {
                    albumId: parseInt(state[1], 10),
                    pageNumber: parseInt(state[3], 10),
                    shareId: (state.length > 4 ? state[4] : null)
                }
            };
        } else if (state.length == 2 || state.length == 3) {
            // TODO: Separate album front page and single page views
            ret = {
                view: "albumPhotos",
                parameter: {
                    albumId: parseInt(state[1], 10),
                    pageNumber: 1,
                    shareId: (state.length > 2 ? state[2] : null)
                }
            };
        }
    }

    loadState(ret);
}

function loadState(state) {
    switch (state.view) {
        case "main":
            Kaleeri.loadFrontPage();
            break;

        case "album":
            Kaleeri.loadAlbums();
            break;

        case "albumPhotos":
            Kaleeri.loadAlbumPage(state.parameter.albumId, state.parameter.pageNumber, state.parameter.shareId);
            break;

        case "addPhoto":
            Kaleeri.loadAddPhoto(state.parameter.albumId, state.parameter.pageNumber, state.parameter.photoNumber);
            break;
    }
}

Kaleeri.nextPage = function () {
    if (Kaleeri.currentAlbum === null) { return; }

    var state = location.hash.substr(1).split("/");
    var page = parseInt(state[3] || 1);

    if (page == Kaleeri.currentAlbum.pages) { return; }
    state[3] = page + 1;
    location.hash = "#" + state.join("/");
};

Kaleeri.previousPage = function () {
    if (Kaleeri.currentAlbum === null) { return; }

    var state = location.hash.substr(1).split("/");
    var page = parseInt(state[3] || 1);

    if (page == 1) { return; }
    state[3] = page - 1;
    location.hash = "#" + state.join("/");
};

Kaleeri.loadFrontPage = function () {
    // TODO: Actual front page for logged-in users
    Kaleeri.loadAlbums();
};

Kaleeri.loadAlbums = function () {
    $(document).ready(function () {
        $.getJSON(window.location.origin + "/album/list", function (data) {
            var source = Kaleeri.templates.album_front;
            var template = Handlebars.compile(source);
            var html = template(data);
            $("#content-placeholder").html(html);
        })
    });
};

Kaleeri.fadeOutAlbums = function (albumId, pageNumber) {
    Kaleeri.parseAlbumId();
    $("#content-placeholder").fadeOut(300, function () {
        Kaleeri.loadAlbumPage(albumId, pageNumber);
    });
};

Kaleeri.addPhoto = function () {
    $(document).ready(function () {
        var source = Kaleeri.templates.add_photo;
        var template = Handlebars.compile(source);
        var html = template();
        $("#content-placeholder").html(html);
    })
};

Kaleeri.loadAddPhoto = function (albumId, pageNumber, photoNumber) {
    $(document).ready(function () {
        var template = Handlebars.compile(Kaleeri.templates.add_photo);

        function done (data) {
            $("#spinner").hide();
            $("#content-placeholder").html(template({
                albumId: albumId,
                albumName: data.name,
                pageNumber: pageNumber,
                photoNumber: photoNumber
            }));
            flickr();
        }

        if (!Kaleeri.currentAlbum) {
            $("#spinner").show();
            Kaleeri.populateAlbumData(albumId, null, done);
        } else {
            done(Kaleeri.currentAlbum);
        }
    });
};

Kaleeri.populateAlbumData = function (albumId, shareId, callback) {
    if (!!shareId) { shareId = shareId + "/"; }
    else { shareId = ""; }

    $.getJSON("/album/" + albumId + "/" + shareId, function (data) {
        Kaleeri.currentAlbum = data;
        if (callback) { callback(data); }
    });
};

Kaleeri.loadAlbumPage = function (albumId, pageNumber, shareId) {
    $(document).ready(function () {
        $content = $("#content-placeholder");
        $content.empty().hide();
        $spinner = $("#spinner");
        $spinner.show();
        if (!!shareId) {
            shareId = shareId + "/";
        } else {
            shareId = "";
        }

        Kaleeri.populateAlbumData(albumId, shareId, function (data) {
            var source = Kaleeri.templates.album_details;
            var template = Handlebars.compile(source);
            var html = template(data);
            if ($content.html().length > 0) {
                $content.prepend(html);
                $spinner.hide();
                $content.fadeIn();
            } else {
                $content.append(html);
            }
        });

        $.getJSON("album/" + albumId + "/page/" + pageNumber + "/" + shareId, function (data) {
            var source = Kaleeri.templates.album_view;
            var template = Handlebars.compile(source);
            var html = template(data);
            if ($content.html().length > 0) {
                $content.append(html);
                $spinner.hide();
                $content.fadeIn();
            } else {
                $content.append(html);
            }

            var share_url = document.URL.split("#")[0] + "#album/" + albumId + "/" + data.share_id;
            $("#share_url").val(share_url);
            $("#fb_share")[0].href += encodeURIComponent(share_url);
            $("#tw_share")[0].href += encodeURIComponent(share_url);
            $("#g_plus")[0].href += encodeURIComponent(share_url);

            var photo_template = Handlebars.compile(Kaleeri.templates.photo_block);
            var photo_map = {};

            var i;
            for (i = 1; i <= data.max_photos; ++i) {
                photo_map[i] = {
                    "url": null,
                    "caption": null,
                    "num": i,
                    "crop_x": 0,
                    "crop_y": 0,
                    "crop_w": 0,
                    "crop_h": 0,
                    "logged_in": ($(".logged-in").length > 0)
                };
            }

            for (i = 0; i < data.photos.length; ++i) {
                var ref = photo_map[data.photos[i].num] = data.photos[i];
                ref.crop_x = ref.crop[0];
                ref.crop_y = ref.crop[1];
                ref.crop_w = ref.crop[2];
                ref.crop_h = ref.crop[3];
            }


            $album_content = $('#album_content').empty();
            for (i = 1; i <= data.max_photos; ++i) {
                photo_map[i].album = albumId;
                photo_map[i].page = pageNumber;
                $album_content.append(photo_template(photo_map[i]));
            }
        });
    });
};

$(function () {
    $(document.createElement("div")).load(
        "/static/handlebar-templates.html",
        function () {
            $(this).find("script").each(function (i, e) {
                Kaleeri.templates[e.id] = e.innerHTML;
            });

            if (location.hash) {
                loadHash();
            } else {
                if ($(".logged-in").length > 0) {
                    loadState({"view": "main"});
                }
            }
        }
    );
});