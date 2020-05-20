import {MetadataWidgetBuilder, applyStyles} from "../tyko/static/js/metadataWidgets.mjs"

describe('Testing text widget', ()=> {
  beforeEach(()=> {
    document.body.innerHTML =
    `<table class="table table-sm">
        <tbody>
            <tr id="dummy" 
                class="tyko-metadata-entity"
                data-name="Audio Type"
                data-displaydata="cassette tape">
            </tr>
            <tr id="tapeThickness" 
                class="tyko-metadata-entity tyko-metadata-entity-enum"
                data-name="Type Thickness"
                data-enumurl="/api/formats/cassette_tape/cassette_tape_tape_thickness"
                data-displaydata="cassette tape">
            </tr>
            <tr id="tapeType" 
                class="tyko-metadata-entity tyko-metadata-entity-enum"
                data-name="Type Type"
                data-enumoptions='[{"text": "I", "value": "1"}]'
                data-value="1"
                data-displaydata="cassette tape">
            </tr>
            <tr id="inspectionDate" 
                class="tyko-metadata-entity tyko-metadata-entity-fulldate"
                data-name="Inspection Date"
                data-displaydata="cassette tape">
            </tr>
        </tbody>
    </table>`;
  })

  test("Applying the styles Transforms", ()=> {
        applyStyles();
        expect($("#dummy").html()).toEqual(expect.stringContaining("cassette tape"));
      }
  )

  test("Set edit mode", ()=>{
    applyStyles()
    const row = $('#inspectionDate');
    row.trigger("mode:edit");
    expect($(row).html()).toContain("input")
  })

  test("Set edit mode and then view mode", ()=>{
    applyStyles()
    const row = $('#inspectionDate');
    row.trigger("mode:edit");
    row.trigger("mode:view");
    expect($(row).html()).not.toContain("input")
  })
})