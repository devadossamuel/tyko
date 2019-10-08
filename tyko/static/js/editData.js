function editData(apiPath) {

    var data = new FormData(document.forms["new-content-form"]);
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