export function initDb(initUrl, restartUrl) {
  const xhr = new XMLHttpRequest();
  xhr.withCredentials = false;

  const initDataRequest = new Promise(((resolve, reject) => {
    xhr.onreadystatechange = () => {
      if (xhr.readyState !== 4) {
        return;
      }
      if (xhr.status >= 200 && xhr.status < 300) {
        const data = {
          'status': xhr.status,
          'responseText': xhr.responseText,
          'statusText': xhr.statusText,
        };

        if (xhr.getResponseHeader('Content-Type') === 'application/json') {
          data['response'] = JSON.parse(xhr.response);
        } else {
          data['response'] = xhr.response;
        }

        resolve(data);
      } else {
        reject(xhr.statusText);
      }

    };
    xhr.open('post', initUrl, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send();
  }));

  initDataRequest.then(function(res) {
    console.log('SUCCESS');
    return restartUrl;
  }).then(function(res) {
    console.log('running ' + res);
  }).catch(function(reason) {
    console.error('Failed ' + reason);
  });
}
