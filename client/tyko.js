function create_fail_response(xhr) {
    console.log("xhr.status = " + xhr.status )
    console.log("xhr.statusText = " + xhr.statusText )
    console.log("xhr = " + xhr )
    console.log("Object.keys(xhr) = " + Object.keys(xhr))

    console.log("xhr.readyState = " + xhr.readyState )
    return {
        status: xhr.status,
        statusText: xhr.statusText,
        responseText: xhr.responseText
    }
}
function get(url){
    return new Promise((resolve, reject) => {
        let xhr = new XMLHttpRequest();
        xhr.withCredentials = false;
        xhr.open("get", url);
        xhr.onload = function () {
            if (xhr.status >= 200 && xhr.status < 300){
                resolve(xhr.response);
            } else {
                reject(create_fail_response(xhr))
            }
        };
        xhr.onerror = function () {
              reject({
                status: xhr.status,
                statusText: xhr.statusText
          });
        };

        xhr.send();
    });
}
