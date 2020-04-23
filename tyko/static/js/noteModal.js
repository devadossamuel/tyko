/**
 * Initializes a modal dialog
 * @param {jQuery} modal - modal used as the dialog box
 * @param {jQuery} button - Button used
 */
export function setupModalWindow(modal, button) {
  modal.find('.modal-title').text(button.data('title'));
  modal.find('#message-text').val(button.data('text'));
}

/**
 * Handle the result of editing a note to the modal dialog box.
 * @param {jQuery} button - Button used
 * @param {jQuery} modal - modal used as the dialog box
 * @param {Promise | Promise<Object>} promise - resulting promise that made a
 * request made to server
 */
export function editNote(button, modal, promise) {
  const noteId = button.data('notetype');
  modal.find('#noteTypeSelect').val(noteId);
  modal.find('#saveNoteButton').unbind('click').bind('click',
      function() {
        const noteApiRoute = button.data('apiroute');
        const noteTypeId = modal.find('#noteTypeSelect').val();
        const noteText = modal.find('#message-text').val();
        promise(noteApiRoute, noteTypeId, noteText).then(function(data) {
          location.reload();
        }).catch(function(data) {
          alert('Failed: ' + data.responseText);
        });
      });
}

/**
 * Handle the result of a note creation to the modal dialog box.
 * @param {jQuery} modal - modal used as the dialog box
 * @param {string} apiPath - url to request a note be added
 * @param {Promise | Promise<Object>} promise - resulting promise that made a
 * request made to server
 */
export function newNote(modal, apiPath, promise) {
  modal.find('#saveNoteButton').unbind('click').bind('click',
      function() {
        const noteTypeId = modal.find('#noteTypeSelect').val();
        const noteText = modal.find('#message-text').val();
        promise(apiPath, noteTypeId, noteText).then(function() {
          location.reload();
        }).catch(function(data) {
          alert('Failed: ' + data.responseText);
        });
      });
}

/**
 * Handle the result of a note removal to the modal dialog box.
 * @param {jQuery} modal - modal used as the dialog box
 * @param {string} apiroute - url to request a note be added
 * @param {Promise | Promise<Object>} promise - resulting promise that made a
 * request made to server
 */
export function removeNote(modal, apiroute, promise) {
  modal.find('#confirmRemoveNoteButton').unbind('click').bind('click',
      function() {
        promise(apiroute).then(function() {
          location.reload();
        }).catch(function(data) {
          alert('Failed: ' + data.responseText);
        });
      });
}
