async function download(urlVideo, fileName) {
    const extension = ".ts";
    var indexPart = 1;
    var count = 1;
    var urlForm;
    fileNameOne = fileName + "-parte-" + indexPart + extension
    var fileStream = streamSaver.createWriteStream(fileNameOne);
    var finishfile = 0;
    urlForm = urlVideo + count + extension;
    while(true) {
        await getVideoPart(fileStream, urlForm, true).then(async function(result) {
            count += 1;
            urlForm = urlVideo + count + extension;
            if (result[0] == "Finish") {
                const blob = new Blob([""]);
                const stream = blob.stream()
                await stream.pipeTo(fileStream)
                finishfile = 1
            } else if (count == indexPart * 120) {

                await getVideoPart(fileStream, urlForm, false).then(async function() {
                    indexPart += 1;
                    fileNamePart = fileName + "-parte-" + indexPart + extension;
                    fileStream = streamSaver.createWriteStream(fileNamePart);
                });
            }
        });

        if (finishfile == 1) {
            break;
        }
    }
    
}

async function getVideoPart(fileStream, url, prevent) {
    
    var result = await fetch(url).then((response) => {
        if (response.status == 404) {
            return "Finish"
        } else {
            return response;
        }});

    if (result == "Finish") {
        return [result];
    }

    await result.blob().then(async function(content) {
            const Readable = await content.stream()
            if (window.WritableStream && Readable.pipeTo) {
                await Readable.pipeTo(fileStream, {preventClose:prevent});
                console.log("Escrito " + url)
                return true;
            }
        });
    return true;
    
}
