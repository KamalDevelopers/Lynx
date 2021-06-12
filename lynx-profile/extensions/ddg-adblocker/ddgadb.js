function setCookie(cname, cvalue, exdays) {
    var d = new Date();
    d.setTime(d.getTime() + (exdays*24*60*60*1000));
    var expires = "expires="+ d.toUTCString();
    document.cookie = cname + "=" + cvalue + ";" + expires + ";path=/";
}

if ((window.location.hostname == "duckduckgo.com") || (window.location.hostname == "www.duckduckgo.com")) {
    setCookie("1", "-1", 365*3);
}
