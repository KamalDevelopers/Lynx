function getCookie(cname) {
    var name = cname + "=";
    var decodedCookie = decodeURIComponent(document.cookie);
    var ca = decodedCookie.split(';');
    for (var i = 0; i <ca.length; i++) {
        var c = ca[i];
        while (c.charAt(0) == ' ') {
            c = c.substring(1);
        }
        if (c.indexOf(name) == 0) {
            return c.substring(name.length, c.length);
        }
    }
    return "";
}

function setCookie(cname, cvalue, exdays) {
    var d = new Date();
    d.setTime(d.getTime() + (exdays*24*60*60*1000));
    var expires = "expires="+ d.toUTCString();
    document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
}


if ((window.location.hostname == "duckduckgo.com") || (window.location.hostname == "www.duckduckgo.com")) {
    var cTheme = getCookie("ae");
    setCookie("ae", "d", 365*3);
    if (cTheme != "d") location.reload();
}

if ((window.location.hostname == "youtube.com") || (window.location.hostname == "www.youtube.com")) {
    var cTheme = getCookie("PREF");
    setCookie("PREF", "f6=400", 365*3);
    if (cTheme != "f6=400") location.reload();
}
