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
        </tbody>
    </table>`;
  })

  test("Appling the styles Transforms", ()=> {
        applyStyles();
        expect($("#dummy").html()).toEqual(expect.stringContaining("<td>cassette tape</td>"));
      }
  )
})