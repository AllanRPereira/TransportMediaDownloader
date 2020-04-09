
async function download(urlVideo, fileName, packageNumberReceive, partNumber) {
    var indexPart;
    var count;
    var percent;
    var initPercent = 0;
    var limit = false;
    const extension = ".ts";
    if (packageNumberReceive != 0) {
        var numberOfPackage = packageNumberReceive;
    } else {
        var numberOfPackage = await getLastPackage(urlVideo, 700, 125, extension);
    }
    var separator = Math.ceil(numberOfPackage / 3) + 1;
    if (partNumber == 0) {
        indexPart = 1;
        count = 1;
        limit = numberOfPackage;
        percent = 100 / numberOfPackage;
    } else {
        indexPart = partNumber;
        count = (partNumber - 1) * separator;
        limit = partNumber * separator;
        percent = 100 / (limit - count);
        initPercent = count;
    };
    var urlForm;
    fileNameOne = fileName + "-parte-" + indexPart + extension;
    var fileStream = await streamSaver.createWriteStream(fileNameOne);
    var finishfile = 0;
    urlForm = urlVideo + count + extension;
    while(true) {
        await getVideoPart(fileStream, urlForm, true).then(async function(result) {
            count += 1;
            urlForm = urlVideo + count + extension;
            if (result == "Finish" || limit == count) {
                const blob = new Blob([""]);
                const stream = blob.stream()
                await stream.pipeTo(fileStream)
                finishfile = 1
            } else if (count == indexPart * separator) {
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
        var percentToPut = Math.ceil((count - initPercent) * percent)
        document.getElementById("progressBar").outerHTML = `<div class="progress-bar bg-success" id="progressBar" role="progressbar" style="width:` + percentToPut + `%;" aria-valuenow="`+ percentToPut +`" aria-valuemin="0" aria-valuemax="100">`+percentToPut+`%</div>`

        if (finishfile == 1) {
            document.getElementById("progressBar").outerHTML = `<div class="progress-bar bg-success" id="progressBar" role="progressbar" style="width:100%;" aria-valuenow="100" aria-valuemin="0" aria-valuemax="100">100%</div>`
            break;
        }
    }
    
}

async function getLastPackage(url, packageNumber, numberDown, extension) {
    return await fetch(url + packageNumber + extension).then(function(response) {
        if(response.status == 404) {
            return getLastPackage(url, packageNumber-numberDown, numberDown, extension);
        } else {
            if(numberDown != 1) {
                return getLastPackage(url, packageNumber+numberDown, numberDown/5, extension);
            } else {
                return packageNumber;
            }
        }
    });
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
        return result;
    }
    
    await result.blob().then(async function(content) {
            const Readable = await content.stream()
            if (window.WritableStream && Readable.pipeTo) {
                await Readable.pipeTo(fileStream, {preventClose:prevent});
                return true;
            };
        });
    return true;
    
}


