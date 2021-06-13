function run_extension() {
    return new Promise(function (resolve, reject) {
        setTimeout(function () {
            browser = new Browser({id}, {path});
            resolve(browser);
        }, 500);
    });
}

run_extension().then(function (browser) {
    async function main(browser) {

        {source}

    }
    main(browser);
});
