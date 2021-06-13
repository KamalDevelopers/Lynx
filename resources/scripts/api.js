new QWebChannel(qt.webChannelTransport, function (channel) {
    window.backend = channel.objects.backend;
});

class Browser {
    constructor(script_id, base_path) {
        this.id = script_id;
        this.path = base_path;
    }

    notification(title, description, icon, delay) {
        window.backend.sendNotification(
            this.id, title, description, icon, delay
        );
    }

    async locale() {
        let result = await backend.locale(this.id);
        return result;
    }

    async bookmarks() {
        let urls = await backend.getBookmarkUrls(this.id);
        let titles = await backend.getBookmarkTitles(this.id);
        let favicons = await backend.getBookmarkFavicons(this.id);
        return [urls, titles, favicons];
    }

    writeFile(path, data) {
        backend.writeFile(this.id, this.path + path, data);
    }

    async readFile(path) {
        let data = await backend.readFile(this.id, this.path + path);
        return data;
    }
}
