function editData(apiPath) {
    return false;
    var data = new FormData(document.forms["new-content-form"]);

    // Sanitize entries
    for(var item of data.entries()){
        console.log(item);
        // data.set(item[0])
    }
    var xhr = new XMLHttpRequest();
    xhr.withCredentials = true;

    xhr.addEventListener("readystatechange", function () {
      if (this.readyState === 4) {
        console.log(this.responseText);
      }
    });

    xhr.open("PUT", apiPath);
    xhr.onload = function(){
        if (this.readyState === XMLHttpRequest.DONE) {
            if(this.status === 200){
                $('#success').modal('show');
                document.getElementById("status_report_title").innerText = "Success";
                let changeLog =  this.responseText;
                document.getElementById("changelog").innerText = changeLog
            } else {
                $('#success').modal('show');
                document.getElementById("status_report_title").innerText = "Error";
                let changeLog =  this.responseText;
                document.getElementById("changelog").innerText = changeLog
            }
        }

    };
    xhr.send(data);



    return false;
}

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

    // xhr.send(dataToSend);
    return false;
}