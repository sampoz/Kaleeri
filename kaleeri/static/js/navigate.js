window.Kaleeri = {
    "templates": {}
};
var state = {
    "view" : "main",
    "parameter" : ""
}

window.addEventListener("popstate", function(e) {
    console.log(event.state);
    loadState(event.state);
});

function loadState(stateToLoad){
    console.log("loading"+ history.state.view +" and next state is"+ stateToLoad.view);
    switch (stateToLoad.view){
        case "main" : {
            console.log("loading main");
            return;
        }
        case "album" :{
            console.log("loading album")
            Kaleeri.loadAlbums();
            return;
        }
        case "albumPhotos":{
            console.log("loading album photos");
            Kaleeri.loadAlbumPhotos(1,1);
            return;
        }
    }
}

$(function() {
    $(document.createElement("div")).load(
        "/static/handlebar-templates.html",
        function () {
            $(this).find("script").each(function(i, e) {
                Kaleeri.templates[e.id]= e.innerHTML;
            });
        }
    );
});

Kaleeri.loadAlbums= function() {
    $(document).ready(function(){
        $.getJSON("album/list", function (data) {
            var source = Kaleeri.templates.album_front;
            var template = Handlebars.compile(source);
            var html = template(data);
            $("#content-placeholder").html(html);
            state.view="album";
            history.pushState(state,"Albums bitches","");
        })
    });
}
Kaleeri.loadAlbumPhotos= function(albumId,pageNumber) {
    $(document).ready(function(){
        $.getJSON("album/"+albumId+"/page/"+pageNumber, function (data) {
            var source = Kaleeri.templates.album_view;
            var template = Handlebars.compile(source);
            var html = template(data);
            $("#content-placeholder").html(html);

            state.view="albumPhotos";
            history.pushState(state,"Albums bitches","");
        })
    });
}