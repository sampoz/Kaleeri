
Kaleeri.parseAlbumId = function parseAlbumId () {
        console.log("parsing");
            if($("#add-button").length){
        var add_button = $("#add-button");
        var add_photo_url = add_button.attr("href");
        var albumNumber = location.href.match("/album/(\d+)");
        console.log("album id was " + albumNumber[1]);
        add_button.attr("href", add_photo_url + albumNumber[1]);
            }
}



window.Kaleeri = {
    "templates": {},
    "urls": {
        create_album: "/",
        add_picture: ""
    },
    "state": "main"
};
var state = {
    "view": "main",
    "parameter": ""
};

window.addEventListener("popstate", function (e) {
    parseAlbumId();
    console.log(location.hash);
    loadState(event.state);
});




function loadState(stateToLoad) {
    Kaleeri.parseAlbumId();
    console.log("loading" + history.state.view + " and next state is" + stateToLoad.view);
    console.log(stateToLoad);

    switch (stateToLoad.view) {
        case "main" :
        {
            console.log("loading main");
            return;
        }
        case "album" :
        {
            console.log("loading album");
            Kaleeri.loadAlbums();
            return;
        }
        case "albumPhotos":
        {
            console.log("loading album photos");
            Kaleeri.loadAlbumPhotos(stateToLoad.parameter.albumId, stateToLoad.parameter.pageNumber);
            return;
        }
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
});

Kaleeri.nextPage = function () {
    console.log(Kaleeri.state);
    Kaleeri.fadeOutAlbums(Kaleeri.state.parameter.albumId, parseInt(Kaleeri.state.parameter.pageNumber) + 1);
    Kaleeri.fadeInAlbums();
};

Kaleeri.previousPage = function () {
    console.log(Kaleeri.state);
    Kaleeri.fadeOutAlbums(Kaleeri.state.parameter.albumId, parseInt(Kaleeri.state.parameter.pageNumber) - 1);
    Kaleeri.fadeInAlbums();
};

Kaleeri.fadeInAlbums = function () {
    $("#content-placeholder").fadeIn();
};

Kaleeri.loadAlbums = function () {
    $(document).ready(function () {
        $.getJSON(window.location.origin + "/album/list", function (data) {
            var source = Kaleeri.templates.album_front;
            var template = Handlebars.compile(source);
            var html = template(data);
            $("#content-placeholder").html(html);
            state.view = "album";
            history.pushState(state, " ", "#album/");
        })
    });
};

Kaleeri.fadeOutAlbums = function (albumId, pageNumber) {
    parseAlbumId();
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
}

Kaleeri.photoToAlbum = function () {

}

Kaleeri.loadAlbumPhotos = function (albumId, pageNumber) {
    $(document).ready(function () {
        $.getJSON("album/" + albumId + "/", function (data2) {
            var source2 = Kaleeri.templates.album_details;
            var template2 = Handlebars.compile(source2);
            var html2 = template2(data2);
            $("#content-placeholder").html(html2);

        })
        $.getJSON("album/" + albumId + "/page/" + pageNumber, function (data) {
            var source = Kaleeri.templates.album_view;
            var template = Handlebars.compile(source);
            var html = template(data);
            $("#content-placeholder").append(html);

            Kaleeri.fadeInAlbums();
            state.view = "albumPhotos";
            console.log("Setting parameters " + albumId + " and " + pageNumber)
            state.parameter = {};
            state.parameter.albumId = String(albumId);
            state.parameter.pageNumber = String(pageNumber);
            Kaleeri.state = state;
            history.pushState(state, " ", "#album/" + albumId + "/page/" + pageNumber);

        })

    })

};
