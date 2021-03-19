function selectLanguage(language) {
    $("[lang]").each(function () {
        if ($(this).attr("lang") == language)
            $(this).show();
    });
}


function searchFilter() {
    var input, filter, ul, li, a, i, txtValue;
    input = document.getElementById("search");
    filter = input.value.toUpperCase();
    ul = document.getElementById("bookmark-list");
    li = ul.getElementsByTagName("li");
    for (i = 0; i < li.length; i++) {
        a = li[i].getElementsByTagName("a")[0];
        txtValue = a.textContent || a.innerText;
        if (txtValue.toUpperCase().indexOf(filter) > -1) {
            li[i].style.display = "";
        } else {
            li[i].style.display = "none";
        }
    }
}

var backend;
var bookmarks = 0;
var index = 0;

new QWebChannel(qt.webChannelTransport, function (channel) {
    window.backend = channel.objects.backend;

    backend.getBookmarkUrls(function(bookmark_urls) {
        backend.getBookmarkTitles(function(bookmark_titles) {
            backend.getBookmarkFavicons(function(bookmark_favis) {
                for (i = 0; i < bookmark_urls.length; i++) {
                    bookmark_url = bookmark_urls[i];
                    bookmark_title = bookmark_titles[i]
                    bookmark_favi = bookmark_favis[i]

                    var ul = document.getElementById("bookmark-list");
                    var li = document.createElement("li");
                    var im = document.createElement("img");
                    var au = document.createElement("a");
                    var an = document.createElement("a");

                    im.setAttribute("class", "favicon");
                    im.setAttribute("src", bookmark_favi);
                    im.setAttribute("alt", "bookmark icon");

                    au.setAttribute("href", bookmark_url);
                    au.setAttribute("class", "url");
                    au.appendChild(document.createTextNode(bookmark_url))

                    an.setAttribute("href", bookmark_url);
                    an.setAttribute("class", "name");
                    an.appendChild(document.createTextNode(bookmark_title))

                    li.appendChild(im);
                    li.appendChild(an);
                    li.appendChild(au);
                    ul.appendChild(li);
                }
            });
        });
    });

    backend.locale(function(l) {
        selectLanguage(l);
    });

});
