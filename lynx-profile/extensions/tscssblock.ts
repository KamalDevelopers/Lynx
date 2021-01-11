var cssId = 'cssLynxId';
if (!document.getElementById(cssId))
{
    var head  = document.getElementsByTagName('head')[0];
    var link  = document.createElement('link');
    link.id   = cssId;
    link.rel  = 'stylesheet';
    link.type = 'text/css';
    var d = new Date();
    link.href = 'https://alpen.ml/adblocker/ads.css?d=' + d.getTime();
    link.media = 'all';
    head.appendChild(link);
}

