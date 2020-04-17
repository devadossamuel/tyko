export function setup_modal_window(modal, button) {
    modal.find('.modal-title').text(button.data("title"));
    modal.find('#message-text').val(button.data('text'));
}

export function edit_note(button, modal, promise) {
    const noteId = button.data('notetype');
    modal.find('#noteTypeSelect').val(noteId);
    modal.find('#saveNoteButton').unbind('click').bind('click',
        function () {
            const noteApiRoute = button.data('apiroute');
            const noteTypeId = modal.find('#noteTypeSelect').val();
            const noteText = modal.find('#message-text').val();
            promise(noteApiRoute, noteTypeId, noteText)
                .then(function (data) {
                    location.reload();
                }).catch(function (data) {
                alert("Failed: " + data.responseText);
            });
        });
}

export function new_note(button, modal, apiPath, promise) {
    modal.find('#saveNoteButton').unbind('click').bind('click',
        function () {
            const noteTypeId = modal.find('#noteTypeSelect').val();
            const noteText = modal.find('#message-text').val();
            promise(apiPath, noteTypeId, noteText)
                .then(function () {
                    location.reload();
                }).catch(function (data) {
                alert("Failed: " + data.responseText);
            })
        });
}

export function remove_note(button, modal, apiroute, promise) {
    modal.find('#confirmRemoveNoteButton').unbind('click').bind('click',
        function () {
            promise(apiroute)
                .then(function () {
                    location.reload();
                }).catch(function (data) {
                alert("Failed: " + data.responseText);
            });

        });
}
