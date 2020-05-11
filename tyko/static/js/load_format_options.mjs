import {requests} from './request.js';
import {items} from './api.js';

/**
 * @callback displayCallback
 * @param {Object} data
 * @return {string} Formatted text to be displayed
 */

/**
 * Get and load enum option for select
 * @param {string} url
 * @param {string} optionId
 * @param {displayCallback} [displayCallback]
 */
function updateOptions(url, optionId, displayCallback = null) {
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

/**
 * Load the CSS class for <input> that have use a date selector
 *
 * @param {string} className - defaults to tyko-input-fulldate
 */
function loadInputDatePickerClass(className = 'tyko-input-fulldate') {
  $.each($(`.${className}`), function(i, element) {
    $(element).datepicker({
      format: 'mm-dd-yyyy',
      uiLibrary: 'bootstrap4',
    });
  });
}

/**
 * @callback successCallback
 * @param {Object} response
 */

/**
 * load new css class for form
 * @param {string} className - element with the class name to be affecte3d,
 * @param {string} apiElementDataName - data attribute name that contains the
 *  api route information for post the data
 * @param {successCallback} onSuccess - success callback
 */
function loadNewEntityFormClass(
    className = 'tyko-form-new-entity',
    apiElementDataName = 'addapiurl',
    onSuccess = null) {
  onSuccess = onSuccess != null ? onSuccess : function(response) {
    location.reload();
  };
  $.each($(`.${className}`), function(index, element) {
    const form = $(element);
    const addUrl = $(element).data(apiElementDataName);
    form.unbind('submit').bind('submit',
        function(event) {
          event.preventDefault();
          const rawData = $(element).serializeArray();
          const data = {};
          for (let i = 0; i < rawData.length; i++) {
            const key = rawData[i].name.split('.');

            if (key.length === 1) {
              data[key[0]] = rawData[i].value;
              continue;
            }

            if (key.length === 2) {
              if (data.hasOwnProperty(key[0])) {
                data[key[0]][key[1]] = rawData[i].value;
              } else {
                const o = {};
                o[key[1]] = rawData[i].value;
                data[key[0]] = o;
              }
            }
          }
          items.addItem(addUrl, data).
              then((resp) => onSuccess(resp)).
              catch(function(reason) {
                const alertBox = $('#submitResultAlert');
                let responsesMessage =
                    '<div class="alert alert-danger alert-dismissible" ' +
                    'role="alert" id="submitResultAlert">\n' +
                    '<strong id="errorMessage">';

                responsesMessage += reason.statusText;
                responsesMessage += '</strong>';
                responsesMessage +=
                    '    <button type="button" class="close" ' +
                    'data-dismiss="alert" aria-label="Close">\n' +
                    '        <span aria-hidden="true">&times;</span>\n' +
                    '</div>';
                alertBox.html(responsesMessage);
                console.error(reason.responseText);
              });
          return false;
        },
    );
  });
}

/**
 * Loads all the class attributes
 */
export function loadTykoClasses() {
  loadNewEntityFormClass();
  loadInputEnumOptionClass();
  loadInputDatePickerClass();

  if (window.hasOwnProperty('CASSETTE_TAPE_THICKNESS_URL')) {
    updateOptions(CASSETTE_TAPE_THICKNESS_URL, 'cassetteTapeThicknessInput',
        function(item) {
          if (item['unit'] === null) {
            return item['value'];
          }
          return `${item['value']} ${item['unit']}`;
        });
  }
}

/**
 * Load the CSS class for <input> that have enumerated data the requires a
 * rest call from the API
 *
 * @param {string} className - defaults to tyko-input-enum-api-options
 * @param {string} apiElementDataName - name of the data attribute stored by
 *  the element that contains the API
 */
export function loadInputEnumOptionClass(
    className = 'tyko-input-enum-api-options',
    apiElementDataName = 'enumapi') {
  $.each($(`.${className}`), function(i, element) {
    const select = $(element);
    const apiUrl = $(element).data(apiElementDataName);
    requests.get(apiUrl).then((data) => {
      const jsonData = JSON.parse(data);
      select.append(`<option value=""></option>`);
      jsonData.forEach(function(it) {
        if (apiUrl.includes('cassette_tape_tape_thickness')) {
          let displayText;
          if (it['unit'] != null) {
            displayText = `${it['value']} ${it['unit']}`;
          } else {
            displayText = `${it['value']}`;
          }
          select.append(`<option value="${it['id']}">${displayText}</option>`);
        } else {
          select.append(`<option value="${it['id']}">${it['name']}</option>`);
        }
      });
    }).catch((resp) => {
      console.error(`Failed to load data from ${apiUrl}`);
    });
  });
}

loadTykoClasses();
