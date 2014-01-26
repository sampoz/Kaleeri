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

function loadAlbums(){

}