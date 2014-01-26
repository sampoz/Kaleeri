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
            var context = data;
            var template = Handlebars.compile(source);
            var html = template(context);
            $("#content-placeholder").html(html);
        })
    });
}