

function submitNewEntity(apiRoot) {
    var formElement = document.querySelector("form");
    var x = new FormData(formElement);
    const formJson = JSON.stringify(Object.fromEntries(x));
    var XHR = new XMLHttpRequest();
    XHR.addEventListener('load', function(event) {
        console.log("loaded");
        if(this.status === 200){
            alert("Success!!");
             console.log(" Returned with " + this.responseText)
        } else {
            alert("status " + this.status + "\n" + this.responseText);

        }
        console.log(" Returned with " + this.status)
    });

    XHR.addEventListener('error', function(event) {
        alert('Oops! Something goes wrong.');
  });
    XHR.open("POST", apiRoot);
    XHR.setRequestHeader('Content-Type', 'application/json');
    console.log(" Sending post");
    XHR.send(formJson)
}
