window.Kaleeri = {
    "templates": {}
};

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
        })
    });
}