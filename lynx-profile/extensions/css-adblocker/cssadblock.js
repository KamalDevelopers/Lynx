let generated_filter = await browser.readFile("./custom-filter.txt");
var selectors = generated_filter.split("\n");

for (let i = 0; i < selectors.length; i++) {
    try {
        var block = document.querySelectorAll(selectors[i]);
    }
    catch (err) {
        console.log(selectors[i]);
        continue;
    }

    for (let x = 0; x < block.length; x++) {
        block[x].setAttribute("style", "display: none !important;");
    }
}
