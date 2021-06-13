function add_adblocker(css_id, code)
{
    if (!document.getElementById(css_id)) {
        css = document.createElement('style');
        css = document.createElement('style');   
        css.type = 'text/css';                   
        css.id = css_id;
        document.head.appendChild(css);          
        css.innerText = code;
    }
}

let filter = await browser.readFile("adblock.css");
let generated_filter = await browser.readFile("../../adblock/generated.css");

add_adblocker("lynx_filter1", filter);
add_adblocker("lynx_filter2", generated_filter);
