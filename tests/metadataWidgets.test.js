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
                class="tyko-metadata-entity"
                data-name="Type Thickness"
                data-enumurl="/api/formats/cassette_tape/cassette_tape_tape_thickness"
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
  test("create callback", ()=> {
        applyStyles();
        $("#tapeThickness").metadataEntry({"requestEnums": function(url) {

          }});
      }
  )
})