class absMetadataWidget {
  constructor(element, fieldName, fieldText) {
    this.element = element;

    this._data = {
      'fieldText': fieldText,
      'fieldName': fieldName,
    };
    this.options = [];
    this.editButtonId = `${fieldName}EditButton`;
  }

  get widgetType() {
    throw new Error('You have to implement the method widgetType!');
  }

  stateName() {
    return this._state._type;
  }

  swap() {
    this._state.swap();
    this.draw();
  }

  draw() {
    this._state.draw(this.element, this._data);
  }

  set onEdited(value) {
    this._onEdited = value;
  }

  get onEdited() {
    if (this._onEdited == null) {
      throw new Error(`${this.constructor.name}.onEdited(data) not set`);
    }
    return this._onEdited;
  }

  get state() {
    return this._state._type;
  }
}


class WidgetState {
  draw(element, data) {
    throw new Error('You have to implement the draw method!');
  }

  constructor(parentClass) {
    this._parent = parentClass;
  }

  newRoot() {
    const newRow = document.createElement('div');
    newRow.setAttribute('class', 'd-flex');

    return newRow;
  }

  confirmChangesGroup() {
    const confirmationButtons = document.createElement('div');
    confirmationButtons.setAttribute('class',
        'input-group-append input-group-sm');
    return confirmationButtons;
  }

  /**
   * Create a new column
   *
   * @param {string} id - id to assign the new column
   * @param {string} colClass - html classes to assign to the new column
   * @return {HTMLDivElement}
   */
  newColumn(id, colClass = 'col') {
    const newColumnSection = document.createElement('div');

    newColumnSection.setAttribute('class', colClass);
    newColumnSection.setAttribute('id', id);
    return newColumnSection;
  }
}


class WidgetEditState extends WidgetState {
  constructor(parentClass) {
    super(parentClass);
    this._type = 'edit';
  }

  accept(parent, data) {
    parent.onEdited(data);
    parent.viewOnlyMode();
  }

  cancel(parent) {
    parent.viewOnlyMode();
  }

  setupEventListeners(rootId) {

    const onOffFocusEvent = function(e) {
      if (document.getElementById(rootId).contains(e.target) || e.target.id ===
          this._parent.editButtonId) {
        return;
      }
      this.clickedOffFocus();
      window.removeEventListener('click', onOffFocusEvent);

    }.bind(this);

    window.addEventListener('click', onOffFocusEvent);
  }

  clickedOffFocus() {
    this.cancel(this._parent);
  }

  newRoot(rootId) {
    const newRoot = document.createElement('div');
    newRoot.setAttribute('id', rootId);
    newRoot.setAttribute('class', 'input-group input-group-sm');
    return newRoot;
  }

  newInputLabel(id) {
    const newLabel = document.createElement('label');
    newLabel.setAttribute('for', id);
    return newLabel;
  }

  newInput(id, text, type) {
    const newInputElement = document.createElement('input');
    newInputElement.setAttribute('id', id);
    newInputElement.setAttribute('value', text);
    newInputElement.setAttribute('type', type);
    newInputElement.setAttribute('class', 'form-control');
    return newInputElement;
  }

  confirmChangesGroup() {
    const confirmationButtons = document.createElement('div');
    confirmationButtons.setAttribute('class',
        'input-group-append input-group-sm');
    return confirmationButtons;
  }

  newConfirmationButton(confirmButtonId, inputElement) {
    const confirmationButtons = this.confirmChangesGroup();

    const parent = this._parent;

    const confirmButton = document.createElement('button');
    confirmButton.innerText = 'Confirm';
    confirmButton.setAttribute('class', 'btn btn-sm btn-outline-primary');
    confirmButton.setAttribute('id', confirmButtonId);

    const accept = this.accept;
    confirmButton.onclick = function() {
      accept(parent, inputElement.value);
    };

    confirmationButtons.appendChild(confirmButton);

    const cancelButton = document.createElement('button');
    cancelButton.innerText = 'Cancel';
    cancelButton.setAttribute('class', 'btn btn-outline-danger');

    const cancel = this.cancel;
    cancelButton.onclick = function() {
      cancel(parent);

    };

    confirmationButtons.appendChild(cancelButton);

    return confirmationButtons;
  }
}


class ViewWidget extends WidgetState {
  constructor(parentClass) {
    super(parentClass);
    this._type = 'view';
    this.editWidget = null;
  }

  swap() {
    if (this.editWidget != null) {
      this._parent._state = new this.editWidget(this._parent);
    } else {
      throw Error('No edit has no valid state');
    }
  }

  draw(element, data) {
    element.innerHTML = '';
    const newRoot = this.newRoot();
    const newContent = this.newColumn('content', 'align-self-stretch');
    newContent.innerText = data['fieldText'];
    newRoot.appendChild(newContent);

    const editCol = this.newColumn('editFunction', 'col');
    editCol.appendChild(this.newEditButton());
    newRoot.appendChild(editCol);
    element.appendChild(newRoot);

  }

  newEditButton() {
    const newButton = document.createElement('button');
    newButton.setAttribute('class',
        'btn btn-sm btn-secondary btn-sm float-right');
    newButton.setAttribute('id', this._parent.editButtonId);

    newButton.innerHTML = 'Edit';
    const self = this._parent;
    newButton.onclick = function() {
      self.swap();
    };
    return newButton;
  }

}

class NumberPickerWidget extends WidgetEditState {

  draw(element, data) {
    element.innerHTML = '';
    const rootId = `editArea${data['fieldName']}`;
    let newRoot = this.newRoot(rootId);

    const inputElement = this._newNumberPicker(data['fieldName'],
        data['fieldText']);
    newRoot.appendChild(inputElement);

    const confirmButtonID = `${data['fieldName']}ConfirmButton`;
    newRoot.appendChild(
        this.newConfirmationButton(confirmButtonID, inputElement));
    element.append(newRoot);
    this.setupEventListeners(element.id);
  }

  _newNumberPicker(fieldName, value = null) {
    const inputElement = document.createElement('input');
    inputElement.setAttribute('class', 'form-control');
    inputElement.setAttribute('type', 'number');
    inputElement.setAttribute('name', fieldName);
    if (value != null) {
      inputElement.setAttribute('value', value);

    }

    return inputElement;
  }
}


class SelectDateWidget extends WidgetEditState {
  draw(element, data) {
    element.innerHTML = '';
    const rootId = `editArea${data['fieldName']}`;
    const newRoot = this.newRoot(rootId);
    const newDatePicker = this._newDatePicker(data['fieldText']);

    newRoot.appendChild(newDatePicker);

    const confirmButtonID = `${data['fieldName']}ConfirmButton`;
    newRoot.appendChild(
        this.newConfirmationButton(confirmButtonID, newDatePicker));
    const validator = this.validateInput;
    newDatePicker.onchange = function(e) {
      console.log('Changed ' + e);
      validator(confirmButtonID, newDatePicker.value);
    };
    newDatePicker.addEventListener('input', function() {
      validator(confirmButtonID, newDatePicker.value);
    });

    element.appendChild(newRoot);
    this.setupEventListeners(element.id);
    this.validateInput(confirmButtonID, newDatePicker.value);
  }

  validateInput(confirmButtonID, value) {
    const re = new RegExp('^([0-9]{4})-([0-9]{2})-([0-9]{2})$');
    const confirmButton = document.getElementById(confirmButtonID);
    if (!confirmButton) {
      return;
    }
    if (re.test(value) === true) {
      if (confirmButton.hasAttribute('disabled')) {
        confirmButton.removeAttribute('disabled');
      }
    } else {
      confirmButton.setAttribute('disabled', '');
    }
  }

  _newDatePicker(value) {

    const datePicker = document.createElement('input');
    datePicker.setAttribute('class', 'form-control');
    datePicker.setAttribute('value', value);
    $(datePicker).datepicker(
        {
          uiLibrary: 'bootstrap4',
          format: 'yyyy-mm-dd',
        },
    );

    return datePicker;
  }
}


class SelectEditWidget extends WidgetEditState {
  constructor(parentClass) {
    super(parentClass);
    this.options = [];
  }

  swap() {
    this._parent._state = new ViewWidget(this._parent);
  }

  draw(element, data) {
    element.innerHTML = '';
    const rootId = `editArea${data['fieldName']}`;
    const newRoot = this.newRoot(rootId);
    const inputId = `input${data['fieldName']}`;
    newRoot.appendChild(this.newInputLabel(inputId));

    const inputElement = this._newSelect(
        this._parent.options,
        data['fieldText'],
        data['fieldName'],
    );

    newRoot.appendChild(inputElement);
    const confirmButtonID = `${data['fieldName']}ConfirmButton`;
    newRoot.appendChild(
        this.newConfirmationButton(confirmButtonID, inputElement));
    element.appendChild(newRoot);
    this.setupEventListeners(element.id);
  }

  _newSelect(options, selected, fieldName) {
    const selectionId = `${fieldName}Select`;
    const inputElement = document.createElement('select');
    inputElement.setAttribute('id', selectionId);
    inputElement.setAttribute('class', 'form-control');
    options.forEach(option => {
      const optionElement = document.createElement('option');
      optionElement.innerText = option.text;
      optionElement.setAttribute('value', option.value);
      if (option.text === selected) {
        optionElement.setAttribute('selected', '');
      }
      inputElement.appendChild(optionElement);
    });
    return inputElement;
  }
}


class TextEditWidget extends WidgetEditState {

  constructor(parentClass) {
    super(parentClass);
  }

  swap() {
    this._parent._state = new ViewWidget(this._parent);
  }

  draw(element, data) {
    element.innerHTML = '';
    const rootId = `editArea${data['fieldName']}`;
    const newRoot = this.newRoot(rootId);

    const inputId = `input${data['fieldName']}`;
    newRoot.appendChild(this.newInputLabel(inputId));
    const inputElement = this.newInput(inputId, data['fieldText'], 'text');
    newRoot.appendChild(inputElement);

    const confirmButtonID = `${data['fieldName']}ConfirmButton`;
    newRoot.appendChild(
        this.newConfirmationButton(confirmButtonID, inputElement));

    element.appendChild(newRoot);
    this.setupEventListeners(element.id);
  }
}


class DatePickerPartFactory {
  constructor(type, rootElement) {

    if (type === 'viewState') {
      return () => {
        const viewWidget = new ViewWidget(rootElement);
        viewWidget.editWidget = SelectDateWidget;
        rootElement._state = viewWidget;
        rootElement._state.draw(rootElement.element, rootElement._data);
      };
    }
  }
}


class SelectEditorPartFactory {
  constructor(type, rootElement) {

    if (type === 'viewState') {
      return () => {
        const viewWidget = new ViewWidget(rootElement);
        viewWidget.editWidget = SelectEditWidget;
        rootElement._state = viewWidget;
        rootElement._state.draw(rootElement.element, rootElement._data);
      };
    }
    if (type === 'editState') {
      return () => {
        rootElement._state = new SelectEditWidget(rootElement);
        rootElement._state.draw(rootElement.element, rootElement._data);
      };
    }

  }
}


class TextEditorPartFactory {
  constructor(type, rootElement) {

    if (type === 'viewState') {
      return () => {
        const viewWidget = new ViewWidget(rootElement);
        viewWidget.editWidget = TextEditWidget;
        rootElement._state = viewWidget;
        rootElement._state.draw(rootElement.element, rootElement._data);
      };
    }
    if (type === 'editState') {
      return () => {
        rootElement._state = new TextEditWidget(rootElement);
        rootElement._state.draw(rootElement.element, rootElement._data);
      };
    }
  }
}


class builder {
  constructor(rootElement, fieldName, displayText) {
    const baseWidget = new absMetadataWidget(rootElement,
        fieldName, displayText);

    baseWidget['inputType'] = this.getInputType();
    baseWidget['editMode'] = this.getEditMode(baseWidget);
    baseWidget['viewOnlyMode'] = this.getViewOnlyMode(baseWidget);
    Object.defineProperty(baseWidget,
        'widgetType',
        {
          get: this.getWidgetTypeName,
        },
    );
    return baseWidget;
  }

  getViewOnlyMode(baseWidget) {
    throw new Error('You have to implement the method getViewOnlyMode!');
  }

  getInputType() {
    throw new Error('You have to implement the method getInputType!');
  }

  getEditMode(baseWidget) {

  }

  getWidgetTypeName() {
    throw new Error('You have to implement the method getWidgetTypeName!');
  }
}


class textEditorBuilder extends builder {

  getEditMode(baseWidget) {
    return new TextEditorPartFactory('editState', baseWidget);
  }

  getInputType() {
    return 'text';
  }

  getViewOnlyMode(baseWidget) {
    return new TextEditorPartFactory('viewState', baseWidget);
  }

  getWidgetTypeName() {
    return 'textEditor';
  }
}


class selectionEditorBuilder extends builder {

  getViewOnlyMode(baseWidget) {
    return new SelectEditorPartFactory('viewState', baseWidget);
  }

  getInputType() {
    return 'select';
  }

  getEditMode(baseWidget) {
    return new SelectEditorPartFactory('editState', baseWidget);
  }

  getWidgetTypeName() {
    return 'selectEditor';
  }
}

class DatePickerBuilder extends builder {

  getViewOnlyMode(baseWidget) {
    return new DatePickerPartFactory('viewState', baseWidget);
  }

  getInputType() {
    return 'input';
  }

  getWidgetTypeName() {
    return 'datePicker';
  }
}

class NumberPickerBuilder extends builder {
  getViewOnlyMode(baseWidget) {
    return () => {
      const viewWidget = new ViewWidget(baseWidget);
      viewWidget.editWidget = NumberPickerWidget;
      baseWidget._state = viewWidget;
      baseWidget._state.draw(baseWidget.element, baseWidget._data);
      return viewWidget;
    };
  }

  getInputType() {
    return 'input';
  }

  getWidgetTypeName() {
    return 'numberPicker';
  }
}

class Factory {
  constructor() {
    this.widgetTypes = {

      'textEditor': (rootElement, fieldName, displayText) => {
        return new textEditorBuilder(rootElement, fieldName, displayText);
      },
      'selectEditor': (rootElement, fieldName, displayText) => {
        return new selectionEditorBuilder(rootElement, fieldName, displayText);
      },
      'datePicker': (rootElement, fieldName, displayText) => {
        return new DatePickerBuilder(rootElement, fieldName, displayText);
      },
      'numberPicker': (rootElement, fieldName, displayText) => {
        return new NumberPickerBuilder(rootElement, fieldName, displayText);
      },
    };
  }

  createWidget(type, rootElement, fieldName, displayText) {
    if (!(type in this.widgetTypes)) {
      throw `${type} is not valid type`;
    }

    const widgetFactory = this.widgetTypes[type];
    const widget = widgetFactory(rootElement, fieldName, displayText);
    widget.viewOnlyMode();
    return widget;
  }
}

export function getWidget(type, rootElement, fieldName, displayText) {
  const factory = new Factory();
  return factory.createWidget(type, rootElement, fieldName, displayText);
}
