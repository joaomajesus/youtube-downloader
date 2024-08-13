chrome.runtime.onInstalled.addListener(() => {
    chrome.contextMenus.create({
        id: "SendToYouTubeDownloader",
        title: "Send to YouTube Downloader",
        contexts: ["link", "page"]
    });
    chrome.contextMenus.create({
        id: "SendToYouTubeDownloaderAudio",
        title: "Send to YouTube Downloader Audio Only",
        contexts: ["link", "page"]
    });
});

chrome.contextMenus.onClicked.addListener((info, tab) => {
    if (info.menuItemId === "SendToYouTubeDownloader"
        || info.menuItemId === "SendToYouTubeDownloaderAudio"
    ) {
        const audioOnly = info.menuItemId === "SendToYouTubeDownloaderAudio";

        const linkUrl = info.linkUrl || info.pageUrl;

        chrome.storage.sync.get(
            { apiUrl: "http://localhost:8000/download" },
            (items) => {
                const apiUrl = items.apiUrl;

                fetch(apiUrl,
                    {
                        method: "POST",
                        headers: {
                            "Content-Type": "application/json",
                        },
                        body: JSON.stringify({ url: linkUrl, audioOnly }),
                    })
                    .then((response) => response.json())
                    .then((data) => {
                        console.log('Success:', data);
                    })
                    .catch((error) => {
                        chrome.scripting.executeScript({
                            target: { tabId: tab.id },
                            func: (error) => {
                                alert('Error: ' + error.message);
                            },
                            args: [error]
                        });

                        console.error('Error:', error);
                    });
            })
    }
});
