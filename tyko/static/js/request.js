function create_fail_response(xhr) {
  return {
    status: xhr.status,
    statusText: xhr.statusText,
    responseText: xhr.responseText,
  };
}

function handle_results(xhr, resolve, reject) {
  if (xhr.status >= 200 && xhr.status < 300) {
    resolve(xhr.response);
  } else {
    reject(create_fail_response(xhr));
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
        handle_results(xhr, resolve, reject);
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
        handle_results(xhr, resolve, reject);
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
        handle_results(xhr, resolve, reject);
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
          reject(create_fail_response(xhr));
        }
      };
      xhr.open('DELETE', apiPath, true);
      xhr.send();
    }));
  },
};