export const requests = {
    "get": (apiPath)=>{
        let xhr = new XMLHttpRequest();
        xhr.withCredentials = false;

        return new Promise(((resolve, reject) => {
            xhr.onreadystatechange = function () {
                if (xhr.readyState !== 4) {
                    return;
                }

                if (xhr.status >= 200 && xhr.status < 300){
                    resolve(xhr.response);
                } else {
                    reject({
                        status: xhr.status,
                        statusText: xhr.statusText
                    })
                }
            };
            xhr.open("get", apiPath, true);
            xhr.send();
        }));
    },
    "post": (apiPath, data)=>{
        let xhr = new XMLHttpRequest();
        xhr.withCredentials = false;
        return new Promise(((resolve, reject) => {
            xhr.onreadystatechange = function () {
                if (xhr.readyState !== 4) {
                    return;
                }

                if (xhr.status >= 200 && xhr.status < 300){
                    resolve(xhr.response);
                } else {
                    reject({
                        status: xhr.status,
                        statusText: xhr.statusText,
                        responseText: xhr.responseText
                    })
                }
            };
        xhr.open("POST", apiPath, true);
        xhr.setRequestHeader('Content-Type', 'application/json');
        xhr.send(JSON.stringify(data));
        }));
    },
    "put" : (apiPath, data) => {
        let xhr = new XMLHttpRequest();
        xhr.withCredentials = false;
        return new Promise(((resolve, reject) => {
            xhr.onreadystatechange = function () {
                if (xhr.readyState !== 4) {
                    return;
                }
                if (xhr.status >= 200 && xhr.status < 300) {
                    resolve(xhr.response);
                } else {
                    reject({
                        status: xhr.status,
                        statusText: xhr.statusText,
                        responseText: xhr.responseText
                    })
                }
            };
            xhr.open("PUT", apiPath, true);
            xhr.setRequestHeader('Content-Type', 'application/json');
            xhr.send(JSON.stringify(data));

        }));
    },
    "delete" : (apiPath) =>{
        let xhr = new XMLHttpRequest();
        xhr.withCredentials = false;
        return new Promise(((resolve, reject) => {
            xhr.onreadystatechange = function () {
                if (xhr.readyState !== 4) {
                    return;
                }

                if (xhr.status >= 200 && xhr.status < 300){
                    resolve(xhr.response);
                } else {
                    reject({
                        status: xhr.status,
                        statusText: xhr.statusText
                    })
                }
            };
        xhr.open("DELETE", apiPath, true);
        xhr.send();
        }));
    }
};