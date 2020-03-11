/**
 *
 * @param apiPath
 * @param apiParameter
 * @param data
 * @param onSuccess
 * @param onFailure
 * @returns {boolean}
 * @deprecated use api.js or the request.js module
 */
function editDataValue(apiPath, apiParameter, data,
                       onSuccess = function (){
                            console.log("Success");
                            location.reload();}
                        ,
                       onFailure= function(){console.log("failed")}){
    console.log("apiPath = " + apiPath);
    console.log("data = " + data);
    console.log("apiParameter = " + apiParameter);
    var xhr = new XMLHttpRequest();
    xhr.withCredentials = true;

    xhr.addEventListener("readystatechange", function () {
      if (this.readyState === 4) {
        console.log(this.responseText);
      }
    });

    xhr.open("PUT", apiPath);
    xhr.setRequestHeader('Content-Type', 'application/json');
    const dataToSend = JSON.stringify({[apiParameter]: data});

    console.log(dataToSend);
    xhr.onload = function(){
        if (this.readyState === XMLHttpRequest.DONE) {
            if(this.status === 200){
                onSuccess()
            } else {
                onFailure();
            }
        }


    };
    xhr.send(dataToSend);

    return false;
}