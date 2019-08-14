function apiRequest(apiURL, route, callback){
    var xhr = new XMLHttpRequest();
    xhr.onreadystatechange = (function(myxhr){
            return function(){
                if(myxhr.readyState === 4) callback(myxhr)
            }
         })(xhr);
    xhr.open("GET", sourceURL + route, true)
    xhr.send("")
}

function updateModelData(jsondata, model){
    model.clear()
    var newData = eval('new Object(' + jsondata + ')' )
    for(var i=0; i<newData.length; i++){
        var newobject = newData[i]
        model.append(newobject)
    }

}


function getApiData(route){
    Resource.apiRequest(sourceURL, route , function(o){
        internal.json = o.responseText
    })
}
