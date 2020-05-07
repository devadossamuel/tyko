export function initDb(init_url, restart_url) {
  const xhr = new XMLHttpRequest();
  xhr.withCredentials = false;

  let initDataRequest = new Promise(((resolve, reject) => {
    xhr.onreadystatechange = () => {
      if (xhr.readyState !== 4) {
        return;
      }
      if (xhr.status >= 200 && xhr.status < 300) {
        let data = {
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
    xhr.open('post', init_url, true);
    xhr.setRequestHeader('Content-Type', 'application/json');
    xhr.send();
  }));

  initDataRequest.then(function(res) {
    const response_data = res['response'];
    console.log('SUCCESS');
    return restart_url;
  }).then(function(res) {
    console.log('running ' + res);
  }).catch(function(reason) {
    console.error('Failed ' + reason);
  });

  // location.reload()
}