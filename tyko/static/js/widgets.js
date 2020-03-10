export class MetadataWidget {

    constructor(element, fieldName, fieldText) {
        this.element = element;

        this._data = {
            "fieldText": fieldText,
            "fieldName": fieldName
        };
        this.editButtonId = `${fieldName}EditButton`;
        this._state = new ViewWidget(this);
        this._state.draw(this.element, this._data)
    }
    swap(){
        this._state.swap();
        this._state.draw(this.element, this._data);
    }

    stateName() {
        return this._state._type;
    }
    set onEdited(value){
        this._onEdited = value;
    }

    editMode(){
        this._state = new EditWidget(this);
        this._state.draw(this.element, this._data);
    }
    viewOnlyMode(){
        this._state = new ViewWidget(this);
        this._state.draw(this.element, this._data);
    }
}

class Widgets{
    constructor(parentClass) {
        this._parent = parentClass;
    }
    newRoot() {
        let contentContainer = document.createElement("div");
        contentContainer.setAttribute("class", "container");

        let newRow = document.createElement("div");
        newRow.setAttribute("class", "row");
        contentContainer.appendChild(newRow);

        return contentContainer

    }
    buttonGroup() {
        let confirmationButtons = document.createElement("div");
        confirmationButtons.setAttribute("class", "input-group-append");
        return confirmationButtons;
    }
    newColumn(id, parent, colClass="col") {
        let row = parent.querySelector(".row");
        let newColumnSection = document.createElement("div");

        newColumnSection.setAttribute("class", colClass);
        newColumnSection.setAttribute("id", id);
        row.appendChild(newColumnSection);
        return newColumnSection;
    }
}

class ViewWidget extends Widgets{
    constructor(parentClass) {
        super(parentClass);
        this._type = "view";
    }
    swap(){
        this._parent._state = new EditWidget(this._parent)
    }



    draw(element, data){
        element.innerHTML = "";
        let newRoot = this.newRoot();
        let newRow = this.newColumn("content", newRoot, "col-6");
        newRow.appendChild(this._newReadOnlyText(data['fieldText']));

        let editCol = this.newColumn("editFunction", newRoot, "col");
        editCol.appendChild(this.newEditButton());
        element.appendChild(newRoot);

    }



    _newReadOnlyText(text) {
        let newText = document.createElement("p");
        newText.innerHTML = text;
        return newText;
    }

    newEditButton() {
        let newButton = document.createElement("button");
        newButton.setAttribute("class", "btn btn-secondary float-right");
        newButton.setAttribute("id", this._parent.editButtonId);

        newButton.innerHTML = "Edit";
        let self = this._parent;
        newButton.onclick = function () {
            self.swap();
        };
        return newButton;
    }

}


class EditWidget extends Widgets{

    constructor(parentClass) {
        super(parentClass);
        this._type = "edit";
        this._click_events = []
    }

    newRoot(rootId){
        let newRoot =  document.createElement("div");
        newRoot.setAttribute("id", rootId);
        newRoot.setAttribute("class", "input-group");
        return newRoot;
    }
    swap(){
        this._parent._state = new ViewWidget(this._parent);
    }


    _newInputLabel(id){
        let newLabel = document.createElement("label");
        newLabel.setAttribute("for", id);
        return newLabel

    }
    _newInput(id, text){
        let newInput = document.createElement("input");
        newInput.setAttribute("id", id);
        newInput.setAttribute("value", text);
        newInput.setAttribute("type", "text");
        newInput.setAttribute("class", "form-control");
        return newInput;
    }

    draw(element, data){
        element.innerHTML = "";
        const rootId = `editArea${data['fieldName']}`;
        let newRoot = this.newRoot(rootId);

        const inputId = `input${data['fieldName']}`;
        newRoot.appendChild(this._newInputLabel(inputId));
        const inputElement = this._newInput(inputId, data['fieldText']);
        newRoot.appendChild(inputElement);

        const confirmButtonID = `${data['fieldName']}ConfirmButton`;
        newRoot.appendChild(this._newConfirmationButton(confirmButtonID, inputElement) );

        element.appendChild(newRoot);
        this.setupEventListeners(element.id);
    }
    setupEventListeners(rootId){

        const onOffFocusEvent = function (e){
            if (document.getElementById(rootId).contains(e.target)  || e.target.id === this._parent.editButtonId) {
                return;
            }
            this.clickedOffFocus();
            window.removeEventListener("click", onOffFocusEvent);

        }.bind(this);

        window.addEventListener("click", onOffFocusEvent);
    }

    clickedOffFocus(){
        this.cancel(this._parent)
    }

    accept(parent, data){
        parent._onEdited(data);
    }

    cancel(parent){
        parent.viewOnlyMode();
    }
    _newConfirmationButton(confirmButtonId, inputElement) {
        let confirmationButtons = this.buttonGroup();

        const parent = this._parent;

        let confirmButton = document.createElement("button");
        confirmButton.innerText = "Confirm";
        confirmButton.setAttribute("class", "btn btn-outline-secondary");
        confirmButton.setAttribute("id", confirmButtonId);

        const accept = this.accept;
        confirmButton.onclick = function(){
          accept(parent, inputElement.value)
        };

        confirmationButtons.appendChild(confirmButton);

        let cancelButton = document.createElement("button");
        cancelButton.innerText = "Cancel";
        cancelButton.setAttribute("class", "btn btn-outline-secondary");

        const cancel = this.cancel;
        cancelButton.onclick = function(){
            cancel(parent);

        };

        confirmationButtons.appendChild(cancelButton);

        return confirmationButtons;
    }


}
