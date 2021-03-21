var backend;
var adblock_code;

function add_adblocker(cssId)
{
    if (!document.getElementById(cssId)) {
        css = document.createElement('style');
        css = document.createElement('style');   
        css.type = 'text/css';                   
        css.id = cssId;
        document.head.appendChild(css);          
        css.innerText = adblock_code;
    }
}

new QWebChannel(qt.webChannelTransport, function (channel) {
    backend = channel.objects.backend;

    backend.readFile("extensions/adblock.css", function(pyval) {
        adblock_code = pyval;
        add_adblocker("deflynx");
    });
    backend.readFile("adblock/generated.css", function(pyval) {
        adblock_code = pyval;
        add_adblocker("pluscsslynx");
    });
});

