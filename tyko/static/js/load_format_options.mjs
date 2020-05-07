import {requests} from "./request.js"
import {items} from "./api.js"

function updateOptions(url, optionId, displayCallback = null) {
  if (displayCallback === null) {

  }
  requests.get(url).then((data) => {
    const jsonData = JSON.parse(data);
    jsonData.forEach(function(it) {
      let displayName = '';
      if (displayCallback === null) {
        displayName = it['name'];
      } else {
        displayName = displayCallback(it);
      }
      $(`#${optionId}`).
          append(`<option value="${it['id']}">${displayName}</option>`);
    });
  }).catch((resp) => {
    alert('failed to get cassette_tape_types');
  });
}

$(".tyko-form-new-entity").each(function() {
  const form = $(this);
  const addUrl = $(this).data("addapiurl");
  form.unbind("submit").bind("submit",
        function(event) {
            event.preventDefault();
            const rawData = $(this).serializeArray();
            let data = {};
            for (let i=0; i < rawData.length; i++ ){
                let key = rawData[i].name.split(".");

                if (key.length == 1){
                  data[key[0]] = rawData[i].value;
                  continue;
                }

                if (key.length == 2){
                  if(data.hasOwnProperty(key[0])){
                    data[key[0]][key[1]] = rawData[i].value;
                  } else {
                    let o = {};
                    o[key[1]] =  rawData[i].value;
                    data[key[0]] = o;
                  }
                }


            }
            items.addItem(addUrl, data)
                .then(function(){
                    location.reload();
                })
                .catch(function(reason){
                    let alertBox = $("#submitResultAlert");
                    let responsesMessage =
                        '<div class="alert alert-danger alert-dismissible" role="alert" id="submitResultAlert">\n' +
                        '<strong id="errorMessage">';

                    responsesMessage += reason.statusText;
                    responsesMessage += "</strong>";
                    responsesMessage +=
                        '    <button type="button" class="close" data-dismiss="alert" aria-label="Close">\n' +
                        '        <span aria-hidden="true">&times;</span>\n' +
                        '    </button>\n' +
                        '</div>';
                    alertBox.html(responsesMessage);
                    console.error(reason.responseText)
                }
            );
            return false;
        }
    );
});

$(".tyko-input-enum-api-options").each(function() {
  const select = $(this);
  const apiUrl = $(this).data("enumapi");
  requests.get(apiUrl).then((data) => {
    const jsonData = JSON.parse(data);
    jsonData.forEach(function(it) {
      select.append(`<option value="${it['id']}">${it['name']}</option>`);
    });
  }).catch((resp) => {
    alert('failed to get cassette_tape_types');
  });
});

$(".tyko-input-fulldate").each(function() {
  $(this).datepicker({
    format: 'mm-dd-yyyy',
    uiLibrary: 'bootstrap4',
  });
});

updateOptions(CASSETTE_TAPE_THICKNESS_URL, 'cassetteTapeThicknessInput',
    function(item) {
      if (item['unit'] === null) {
        return item['value'];
      }
      return `${item['value']} ${item['unit']}`;
    });