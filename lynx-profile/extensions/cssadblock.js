var cssId = 'cssLynxId';
var adblock_code = @read(adblock)

if (!document.getElementById(cssId))
{
    css = document.createElement('style');
    css = document.createElement('style');   
    css.type = 'text/css';                   
    css.id = cssId;
    document.head.appendChild(css);          
    css.innerText = adblock_code;
}

