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

window.addEventListener("hashchange", loadHash);

function loadHash() {
    var state = location.hash.substr(1).split("/");
    var ret;

    if (state[0] == "" || state[0] == "main") {
        ret = {"view": "main", "parameter": {}};
    }

    else if (state[0] == "album") {
        if (state.length > 2) {
            ret = {
                "view": "albumPhotos",
                "parameter": {
                    "albumId": parseInt(state[1], 10),
                    "pageNumber": parseInt(state[3], 10)
                }
            };
        } else {
            // TODO: Album front page
            ret = {
                "view": "albumPhotos",
                "parameter": {
                    "albumId": parseInt(state[1], 10),
                    "pageNumber": 1
                }
            };
        }
    }

    loadState(ret);
}

function loadState(stateToLoad) {
    switch (stateToLoad.view) {
        case "main":
            Kaleeri.loadFrontPage();
            break;

        case "album":
            Kaleeri.loadAlbums();
            break;

        case "albumPhotos":
            Kaleeri.loadAlbumPhotos(stateToLoad.parameter.albumId, stateToLoad.parameter.pageNumber);
            break;
    }
}

$(function () {
    $(document.createElement("div")).load(
        "/static/handlebar-templates.html",
        function () {
            $(this).find("script").each(function (i, e) {
                Kaleeri.templates[e.id] = e.innerHTML;
            });
        }
    );

    if (location.hash) {
        loadHash();
    } else {
        loadState({"view": "main"});
    }
});

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

Kaleeri.fadeInAlbums = function () {
    $("#content-placeholder").fadeIn();
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
        Kaleeri.loadAlbumPhotos(albumId, pageNumber);
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

Kaleeri.photoToAlbum = function () {

};

Kaleeri.loadAlbumPhotos = function (albumId, pageNumber) {
    $(document).ready(function () {
        $.getJSON("album/" + albumId + "/", function (data) {
            Kaleeri.currentAlbum = data;
            var source = Kaleeri.templates.album_details;
            var template = Handlebars.compile(source);
            var html = template(data);
            $("#content-placeholder").html(html);
        });

        $.getJSON("album/" + albumId + "/page/" + pageNumber, function (data) {
            var source = Kaleeri.templates.album_view;
            var template = Handlebars.compile(source);
            var html = template(data);
            $("#content-placeholder").append(html);
            Kaleeri.fadeInAlbums();
        });
    });
};