import {edit_note} from "../tyko/static/js/noteModal";
import {notes} from "../tyko/static/js/api.js"

describe('Testing text widget', ()=> {
    beforeEach(()=>{
        document.body.innerHTML =
            '<button id="select"></button>' +
            '<div class="modal" id="noteEditor" tabindex="-1" role="dialog"\n' +
            '         aria-labelledby="exampleModalLabel" aria-hidden="true">\n' +
            '        <div class="modal-dialog modal-lg modal-dialog-centered"\n' +
            '             role="document">\n' +
            '            <div class="modal-content">\n' +
            '                <div class="modal-header">\n' +
            '                    <h5 class="modal-title" id="exampleModalLabel">Edit Note</h5>\n' +
            '                    <button type="button" class="close" data-dismiss="modal"\n' +
            '                            aria-label="Close">\n' +
            '                        <span aria-hidden="true">&times;</span>\n' +
            '                    </button>\n' +
            '                </div>\n' +
            '                <div class="modal-body">\n' +
            '                    <form>\n' +
            '                        <div class="form-group">\n' +
            '                            <label for="noteTypeSelect" class="col-form-label">Type:</label>\n' +
            '                            <select class="custom-select"\n' +
            '                                    id="noteTypeSelect"></select>\n' +
            '                            <label for="message-text" class="col-form-label">Note:</label>\n' +
            '                            <textarea class="form-control"\n' +
            '                                      id="message-text" required></textarea>\n' +
            '                        </div>\n' +
            '                    </form>\n' +
            '                </div>\n' +
            '                <div class="modal-footer">\n' +
            '                    <button type="button" class="btn btn-secondary"\n' +
            '                            id="cancelButton"\n' +
            '                            data-dismiss="modal">Cancel\n' +
            '                    </button>\n' +
            '                    <button type="button" class="btn btn-primary"\n' +
            '                            id="saveNoteButton" data-dismiss="modal">Save\n' +
            '                    </button>\n' +
            '                </div>\n' +
            '            </div>\n' +
            '        </div>\n' +
            '    </div>'
    })
    test("cancel button closes the window", ()=>{
        let modal = $("#noteEditor");
        let triggerButton = $(document.getElementById("select"));
        triggerButton.trigger('click');
        triggerButton.data('apiroute', "/api");
        expect(modal.hasClass('show')).toBe(false);

        modal.modal('show');
        expect(modal.hasClass('show')).toBe(true);
        edit_note(triggerButton, modal, notes.editNote);
        modal.find('#cancelButton').trigger("click");
        expect(modal.hasClass('show')).toBe(false);
    });

    test("save button closes the window", ()=>{
        let modal = $("#noteEditor");
        let triggerButton = $(document.getElementById("select"));
        triggerButton.trigger('click');
        triggerButton.data('apiroute', "/api");
        expect(modal.hasClass('show')).toBe(false);

        modal.modal('show');
        expect(modal.hasClass('show')).toBe(true);
        edit_note(triggerButton, modal, notes.editNote);
        modal.find('#saveNoteButton').trigger("click");
        expect(modal.hasClass('show')).toBe(false);
    });
});