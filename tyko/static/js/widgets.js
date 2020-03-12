class absMetadataWidget {
    constructor(element, fieldName, fieldText) {
        this.element = element;

        this._data = {
            "fieldText": fieldText,
            "fieldName": fieldName
        };
        this.options = [];
        this.editButtonId = `${fieldName}EditButton`;
    }
    stateName() {
        return this._state._type;
    }
    swap(){
        this._state.swap();
        this.draw();
    }
    draw(){
        this._state.draw(this.element, this._data)
    }
    set onEdited(value){
        this._onEdited = value;
    }
    get onEdited(){
        if (this._onEdited == null){
            throw `${this.constructor.name}.onEdited(data) not set`
        }
        return this._onEdited;
    }
    get state(){
        return this._state._type;
    }
}

class WidgetState{
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
    confirmChangesGroup() {
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
class WidgetEditState extends WidgetState{
    constructor(parentClass) {
        super(parentClass);
        this._type = "edit";
    }
    accept(parent, data){
        parent.onEdited(data);
        parent.viewOnlyMode();
    }
    cancel(parent){
        parent.viewOnlyMode();
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
    newRoot(rootId){
        let newRoot =  document.createElement("div");
        newRoot.setAttribute("id", rootId);
        newRoot.setAttribute("class", "input-group");
        return newRoot;
    }
    newInputLabel(id){
        let newLabel = document.createElement("label");
        newLabel.setAttribute("for", id);
        return newLabel
    }
    newInput(id, text, type){
        let newInputElement = document.createElement("input");
        newInputElement.setAttribute("id", id);
        newInputElement.setAttribute("value", text);
        newInputElement.setAttribute("type", type);
        newInputElement.setAttribute("class", "form-control");
        return newInputElement;
    }

    confirmChangesGroup() {
        let confirmationButtons = document.createElement("div");
        confirmationButtons.setAttribute("class", "input-group-append");
        return confirmationButtons;
    }

    newConfirmationButton(confirmButtonId, inputElement) {
        let confirmationButtons = this.confirmChangesGroup();

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
class ViewWidget extends WidgetState{
    constructor(parentClass) {
        super(parentClass);
        this._type = "view";
        this.editWidget = null;
    }
    swap(){
        if(this.editWidget != null){
            this._parent._state = new this.editWidget(this._parent)
        } else {
            throw "No edit has no valid state ";
        }
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
class SelectDateWidget extends WidgetEditState {
    draw(element, data){
        element.innerHTML = "";
        const rootId = `editArea${data['fieldName']}`;
        let newRoot = this.newRoot(rootId);
        console.log("data['fieldText'], = " + data['fieldText']);
        let new_date_picker = this._new_date_picker(data['fieldText']);
        newRoot.appendChild(new_date_picker);


        const confirmButtonID = `${data['fieldName']}ConfirmButton`;
        newRoot.appendChild(this.newConfirmationButton(confirmButtonID, new_date_picker) );
        element.appendChild(newRoot);
        this.setupEventListeners(element.id);
    }
    _new_date_picker(value){

        let datePicker = document.createElement("input");
        datePicker.setAttribute("class", "form-control");
        datePicker.setAttribute("value", value);
        $(datePicker).datepicker({
                    uiLibrary: 'bootstrap4',
                    format: 'yyyy-mm-dd'
                });

        return datePicker;
    }
}
class SelectEditWidget extends WidgetEditState {
    constructor(parentClass) {
        super(parentClass);
        this.options = [];
    }
    swap(){
        this._parent._state = new ViewWidget(this._parent);
    }
    draw(element, data){
        element.innerHTML = "";
        const rootId = `editArea${data['fieldName']}`;
        let newRoot = this.newRoot(rootId);
        const inputId = `input${data['fieldName']}`;
        newRoot.appendChild(this.newInputLabel(inputId));

        let inputElement = this._newSelect(this._parent.options, data['fieldText'], data['fieldName']);

        newRoot.appendChild(inputElement);
        const confirmButtonID = `${data['fieldName']}ConfirmButton`;
        newRoot.appendChild(this.newConfirmationButton(confirmButtonID, inputElement) );
        element.appendChild(newRoot);
        this.setupEventListeners(element.id);
    }

    _newSelect(options, selected, fieldName) {
        const selectionId = `${fieldName}Select`;
        let inputElement = document.createElement("select");
        inputElement.setAttribute("id", selectionId);
        inputElement.setAttribute("class", "form-control");
        options.forEach(option =>{
            let optionElement = document.createElement("option");
            optionElement.innerText = option.text;
            optionElement.setAttribute("value", option.value);
            if( option.text === selected){
                optionElement.setAttribute("selected", "");
            }
            inputElement.appendChild(optionElement)
        });
        return inputElement;
    }
}

class TextEditWidget extends WidgetEditState{

    constructor(parentClass) {
        super(parentClass);
    }


    swap(){
        this._parent._state = new ViewWidget(this._parent);
    }

    draw(element, data){
        element.innerHTML = "";
        const rootId = `editArea${data['fieldName']}`;
        let newRoot = this.newRoot(rootId);

        const inputId = `input${data['fieldName']}`;
        newRoot.appendChild(this.newInputLabel(inputId));
        const inputElement = this.newInput(inputId, data['fieldText'], "text");
        newRoot.appendChild(inputElement);

        const confirmButtonID = `${data['fieldName']}ConfirmButton`;
        newRoot.appendChild(this.newConfirmationButton(confirmButtonID, inputElement) );

        element.appendChild(newRoot);
        this.setupEventListeners(element.id);
    }
}
class DatePickerPartFactory {
    constructor(type, rootElement) {

        if (type === "viewState") {
            return () => {
                let viewWidget = new ViewWidget(rootElement);
                viewWidget.editWidget = SelectDateWidget;
                rootElement._state = viewWidget;
                rootElement._state.draw(rootElement.element, rootElement._data);
            }
        }
    }
}
class SelectEditorPartFactory{
    constructor(type, rootElement) {

        if (type === "viewState") {
            return () => {
                let viewWidget = new ViewWidget(rootElement);
                viewWidget.editWidget = SelectEditWidget;
                rootElement._state = viewWidget;
                rootElement._state.draw(rootElement.element, rootElement._data);
            }
        }
        if (type === "editState") {
            return () => {
                rootElement._state = new SelectEditWidget(rootElement);
                rootElement._state.draw(rootElement.element, rootElement._data);
            }
        }

    }
}
class TextEditorPartFactory{
    constructor(type, rootElement) {

        if (type === "viewState"){
            return ()=>{
                let viewWidget = new ViewWidget(rootElement);
                viewWidget.editWidget = TextEditWidget;
                rootElement._state = viewWidget;
                rootElement._state.draw(rootElement.element, rootElement._data);
            }
        }
        if (type === "editState"){
            return ()=>{
                rootElement._state = new TextEditWidget(rootElement);
                rootElement._state.draw(rootElement.element, rootElement._data);
            }
        }
    }
}

class Factory {
    constructor() {
        this.widgetTypes = {
            "textEditor": (rootElement, fieldName, displayText) => {
                let baseWidget = new absMetadataWidget(rootElement, fieldName, displayText);
                baseWidget["inputType"] = "text";
                baseWidget['editMode'] = new TextEditorPartFactory("editState", baseWidget);
                baseWidget['viewOnlyMode'] = new TextEditorPartFactory("viewState", baseWidget);
                return baseWidget;
            },
            "selectEditor": (rootElement, fieldName, displayText) => {
                let baseWidget = new absMetadataWidget(rootElement, fieldName, displayText);
                baseWidget["inputType"] = "select";
                baseWidget['viewOnlyMode'] = new SelectEditorPartFactory("viewState", baseWidget);
                baseWidget['editMode'] = new SelectEditorPartFactory("editState", baseWidget);
                return baseWidget
            },
            "datePicker": (rootElement, fieldName, displayText) => {
                let baseWidget = new absMetadataWidget(rootElement, fieldName, displayText);
                baseWidget['viewOnlyMode'] = new DatePickerPartFactory("viewState", baseWidget);
                return baseWidget;
            }
        };
    }
    createWidget(type, rootElement, fieldName, displayText){
        if( !(type in this.widgetTypes) ){
            throw `${type} is not valid type`;
        }

        let widgetFactory =this.widgetTypes[type];
        let widget = widgetFactory(rootElement, fieldName, displayText);

        widget.viewOnlyMode();
        return widget
    }
}

export function getWidget(type, rootElement, fieldName, displayText) {
    const factory = new Factory();
    return factory.createWidget(type, rootElement, fieldName, displayText);
}