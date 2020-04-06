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
                await getVideoPart(fileStream, urlForm, false).then(function(response) {
                    if (response != "Finish") {
                        indexPart += 1;
                        fileNamePart = fileName + "-parte-" + indexPart + extension;
                        count += 1;
                        fileStream = streamSaver.createWriteStream(fileNamePart);
                    }
                });
            }
        });

        if (finishfile == 1) {
            break;
        }
    }
    
}

async function getVideoPart(fileStream, url, prevent) {
    
    var result = await fetch(url).then(function(response) {
        if (response.status == 404) {
            return "Finish";
        } else {
            return response;
        }}).catch(async function (reason) {
            console.log("Error:" + reason);
            await new Promise(r => setTimeout(r, 2000));
            resul = await getVideoPart(fileStream, url, prevent);
        });

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
