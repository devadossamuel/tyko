function createFailResponse(xhr) {
  return {
    status: xhr.status,
    statusText: xhr.statusText,
    responseText: xhr.responseText,
  };
}

function handleResults(xhr, resolve, reject) {
  if (xhr.status >= 200 && xhr.status < 300) {
    resolve(xhr.response);
  } else {
    reject(createFailResponse(xhr));
  }
}

export const requests = {
  'get': (apiPath) => {
    const xhr = new XMLHttpRequest();
    xhr.withCredentials = false;

    return new Promise(((resolve, reject) => {
      xhr.onreadystatechange = function() {
        if (xhr.readyState !== 4) {
          return;
        }
        handleResults(xhr, resolve, reject);
      };
      xhr.open('get', apiPath, true);
      xhr.send();
    }));
  },
  'post': (apiPath, data) => {
    const xhr = new XMLHttpRequest();
    xhr.withCredentials = false;
    return new Promise(((resolve, reject) => {
      xhr.onreadystatechange = function() {
        if (xhr.readyState !== 4) {
          return;
        }
        handleResults(xhr, resolve, reject);
      };
      xhr.open('POST', apiPath, true);
      xhr.setRequestHeader('Content-Type', 'application/json');
      xhr.send(JSON.stringify(data));
    }));
  },
  'put': (apiPath, data) => {
    const xhr = new XMLHttpRequest();
    xhr.withCredentials = false;
    return new Promise(((resolve, reject) => {
      xhr.onreadystatechange = function() {
        if (xhr.readyState !== 4) {
          return;
        }
        handleResults(xhr, resolve, reject);
      };
      xhr.open('PUT', apiPath, true);
      xhr.setRequestHeader('Content-Type', 'application/json');
      xhr.send(JSON.stringify(data));
    }));
  },
  'delete': (apiPath) => {
    const xhr = new XMLHttpRequest();
    xhr.withCredentials = false;
    return new Promise(((resolve, reject) => {
      xhr.onreadystatechange = function() {
        if (xhr.readyState !== 4) {
          return;
        }

        if (xhr.status >= 200 && xhr.status < 300) {
          resolve(xhr.response);
        } else {
          reject(createFailResponse(xhr));
        }
      };
      xhr.open('DELETE', apiPath, true);
      xhr.send();
    }));
  },
};