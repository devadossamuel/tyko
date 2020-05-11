import * as formatOptions from '../tyko/static/js/load_format_options';

jest.mock('../tyko/static/js/request.js');

describe('Testing loadInputEnumOptionclass', () => {
  beforeEach(() => {
    document.body.innerHTML =
        `<form id="newEntity" class="tyko-form-new-entity" data-addapiurl="/api/new">
        <div class="form-group row cassette-row format-row">
              <label for="dummy" class="col-sm-2 col-form-label">Audio type</label>
              <div class="col-sm-10">
                  <select id="dummy" 
                          class="form-control tyko-input-enum-api-options" 
                          data-enumapi="/api/formats" 
                          name="format_details.format_type_id"></select>
              </div>
        </div>
    </form>`;
    formatOptions.loadTykoClasses();
  });
  test('loadInputEnumOptionclass changes', () => {
    expect($('#dummy > *').length).toBe(7);
  });
});

describe('loadInputDatePickerClass', () => {
  beforeEach(() => {
    document.body.innerHTML = `
    <form id="newEntity" class="tyko-form-new-entity" data-addapiurl="/api/new">
      <div class="form-group row cassette-row format-row">
          <label for="dummy" class="col-sm-2 col-form-label">Date Inspected</label>
          <div class="col-sm-10">
              <input id="dummy" class="form-control tyko-input-fulldate" name="format_details.DateInspected">
          </div>
      </div>
    </form>`;
    formatOptions.loadTykoClasses();
  });

  test('loadInputDatePickerClass changes', () => {
    expect($('#dummy').attr('data-datepicker')).toBe('true');
  });
});