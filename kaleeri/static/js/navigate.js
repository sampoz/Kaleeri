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

Kaleeri.modifyPhoto = function () {
    $(document).ready(function () {
        $.post($("add.html", "#url").serialize());
        var source = Kaleeri.templates.modify_photo;
        var template = Handlebars.compile(source);
        var html = template();
        $("#content-placeholder").html(html);
    })
};

Kaleeri.loadAddPhoto = function (albumId, pageNumber, photoNumber) {
    $(document).ready(function () {
        var template = Handlebars.compile(Kaleeri.templates.add_photo);
        $("#content-placeholder").html(template({
            albumId: albumId,
            albumName: Kaleeri.currentAlbum.name,
            pageNumber: pageNumber,
            photoNumber: photoNumber
        }));
    });
};

Kaleeri.photoToAlbum = function () {

};

Kaleeri.loadAlbumPage = function (albumId, pageNumber, shareId) {
    $(document).ready(function () {
        $("#content-placeholder").empty().addClass("spinner");
        if (!!shareId) {
            shareId = shareId + "/";
        } else {
            shareId = "";
        }

        $.getJSON("album/" + albumId + "/" + shareId, function (data) {
            Kaleeri.currentAlbum = data;
            var source = Kaleeri.templates.album_details;
            var template = Handlebars.compile(source);
            var html = template(data);
            $("#content-placeholder").removeClass("spinner").html(html);
        });

        $.getJSON("album/" + albumId + "/page/" + pageNumber + "/" + shareId, function (data) {
            var source = Kaleeri.templates.album_view;
            var template = Handlebars.compile(source);
            var html = template(data);
            $("#content-placeholder").append(html).fadeIn();

            var photo_template = Handlebars.compile(Kaleeri.templates.photo_block);
            var photo_map = {};

            var i;
            for (i = 1; i <= data.max_photos; ++i) {
                photo_map[i] = {
                    "url": null,
                    "caption": null,
                    "num": i
                };
            }

            for (i = 0; i < data.photos.length; ++i) {
                photo_map[data.photos[i].num] = data.photos[i];
            }

            $album_content = $('#album_content');
            $album_content.empty();
            for (i = 1; i <= data.max_photos; ++i) {
                photo_map[i].album = albumId;
                photo_map[i].page = pageNumber;
                $album_content.append(photo_template(photo_map[i]));
            }
        });
    });
};

$(function () {
    $("body").addClass('loading');
    $(document.createElement("div")).load(
        "/static/handlebar-templates.html",
        function () {
            if (location.hash) {

            }

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