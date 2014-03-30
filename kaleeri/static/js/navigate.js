window.Kaleeri = window.Kaleeri || {};
$.extend(window.Kaleeri, {
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
});

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

Kaleeri.submitAjaxForm = function (form) {
    var $form = $(form);
    var url = $form.attr('action');
    var vals = {};
    $form.find("input:not([type=submit]), select").each(function (_, e) {
        e = $(e);
        vals[e.attr('name')] = e.val();
    });

    var ret = Kaleeri.submitAjaxData(url, vals, $form);
};

Kaleeri.submitAjaxData = function (url, data, errorHolder) {
    $.post(url, data, function (data) {
        if (data.hasOwnProperty("redirect")) {
            if (data.redirect == window.location) {
                location.reload(false);
            } else {
                window.location = data.redirect;
            }
        } else if (data.hasOwnProperty("error")) {
            $(errorHolder).prepend('<div class="error">' + data.error + '</div>');
        }
    });
};

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

            initAddPhoto();
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
        var $content = $("#content-placeholder");
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
            $content.prepend(html);
            $spinner.hide();
            $content.fadeIn();

            $.getJSON("album/" + albumId + "/page/" + pageNumber + "/" + shareId, function (data) {
                var source = Kaleeri.templates.album_view;
                var template = Handlebars.compile(source);
                $.extend(data, {
                    "currentUser": Kaleeri.currentUser || null,
                    "loggedIn": !!Kaleeri.currentUser,
                    "isOwner": Kaleeri.currentUser === Kaleeri.currentAlbum.owner
                });

                var html = template(data);
                if ($content.html().length > 0) {
                    $content.append(html);
                    $spinner.hide();
                    $content.fadeIn();
                } else {
                    $content.append(html);
                }

                $content.find("#album_rename_btn").click(function () {
                    var $row = $content.find('#album_rename_row');
                    if ($row.length > 0) {
                        $row.remove();
                        $(this).text('Rename album');
                        return;
                    }

                    $(this).text('Cancel renaming');
                    var template = Handlebars.compile(Kaleeri.templates.album_rename);
                    var html = template(Kaleeri.currentAlbum);
                    $content.find("#share_bar").before(html);
                    $row = $('#album_rename_row');
                    $form = $row.find('form');
                    $form.append('<input type="hidden" name="csrfmiddlewaretoken" value="' + getCookie('csrftoken') + '">');
                    $row.find('input[type=submit]').click(function (e) {
                        Kaleeri.submitAjaxForm($form);
                        e.preventDefault();
                    });
                });

                $content.find("#remove_photos").click(function () {
                    if ($(this).text() == "Remove photos") {
                        $('.img-remove-overlay').show();
                        $(this).text("Done removing");
                    } else {
                        $('.img-remove-overlay').hide();
                        $(this).text("Remove photos");
                    }
                });

                $content.find("#page_edit_btn").click(function () {
                    var $row = $content.find("#page_edit_row");
                    if ($row.length > 0) {
                        $row.remove();
                        $(this).text('Edit page');
                        return;
                    }

                    $(this).text('Cancel editing');
                    var template = Handlebars.compile(Kaleeri.templates.page_edit);
                    var data = Kaleeri.currentAlbum;
                    data.page = pageNumber;
                    var html = template(data);
                    $content.find("#share_bar").before(html);
                    $row = $('#page_edit_row');
                    $form = $row.find('form');
                    $form.append('<input type="hidden" name="csrfmiddlewaretoken" value="' + getCookie('csrftoken') + '">');

                    $.getJSON('/layouts/', function (data) {
                        $select = $form.find('select');
                        $select.empty();
                        var option;
                        for (var i = 0; i < data.length; ++i) {
                            $option = $(document.createElement('option'));
                            $option.val(data[i].id);
                            $option.text(data[i].name);
                            if (data[i].id == Kaleeri.currentAlbum.layout_id) {
                                $option.attr('selected', true);
                            }
                            $select.append($option);
                        }

                        $row.find('input[type=submit]').click(function (e) {
                            Kaleeri.submitAjaxForm($form);
                            e.preventDefault();
                        });
                    });
                });

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

                $content.find(".img-remove-overlay .btn").click(function () {
                    if (!confirm("Do you want to remove this image?")) { return; }
                    var img = $(this).closest('[id^=photo-]')[0].id.split("-")[1];
                    var csrf = getCookie('csrftoken');
                    var url = '/album/' + albumId + '/page/' + pageNumber + '/photo/' + img + '/remove/';
                    var data = {csrfmiddlewaretoken: csrf};
                    var ret = Kaleeri.submitAjaxData(url, data, $content);
                });
            });
        });
    });
};

Kaleeri.addPage = function(){
    console.log("tried to add");
    var albumNumber = /album\/(\d+)\//.exec(location.href)[1];
    var pageNumber = /page\/(\d+)\//.exec(location.href)[1];
    var csrf = getCookie('csrftoken');
    $.ajax({
        url : "album/" + albumNumber + "/page/add/" +(parseInt(pageNumber)+1)+ "/",
        type : "POST",
        data : {'layout':'Four per page'},
        setRequestHeader : csrf,
        success : function (data) {
        console.log(data);
        location.reload();
    }});
};

Kaleeri.removePage = function(){
    console.log("tried to remove");
};

function csrfSafeMethod(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
}
function sameOrigin(url) {
    // test that a given url is a same-origin URL
    // url could be relative or scheme relative or absolute
    var host = document.location.host; // host + port
    var protocol = document.location.protocol;
    var sr_origin = '//' + host;
    var origin = protocol + sr_origin;
    // Allow absolute or scheme relative URLs to same origin
    return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
        (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
        // or any other URL that isn't scheme relative or absolute i.e relative.
        !(/^(\/\/|http:|https:).*/.test(url));
}
$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
            // Send the token to same-origin, relative URLs only.
            // Send the token only if the method warrants CSRF protection
            // Using the CSRFToken value acquired earlier
            xhr.setRequestHeader("X-CSRFToken", getCookie('csrftoken'));
        }
    }
});

Kaleeri.getCookie = function (name) {
    var cookieValue = null;
    if (document.cookie && document.cookie != '') {
        var cookies = document.cookie.split(';');
        for (var i = 0; i < cookies.length; i++) {
            var cookie = jQuery.trim(cookies[i]);
            // Does this cookie string begin with the name we want?
            if (cookie.substring(0, name.length + 1) == (name + '=')) {
                cookieValue = decodeURIComponent(cookie.substring(name.length + 1));
                break;
            }
        }
    }
    return cookieValue;
}


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