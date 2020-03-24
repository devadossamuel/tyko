import {notes} from "../tyko/static/js/api.js";

jest.mock("../tyko/static/js/request");
describe('Testing api', ()=>{
    test("get notes", ()=> {
        const sample_notes_data = `
{
  "notes": [
    {
      "note_id": 1, 
      "note_type": "Inspection", 
      "note_type_id": 1, 
      "text": "inspection note"
    }, 
    {
      "note_id": 2, 
      "note_type": "Project", 
      "note_type_id": 3, 
      "text": "One 16mm film"
    }
  ]
}`;
    return notes.getNotes()
        .then(function (data){

            expect(data).toBe(sample_notes_data)
        });
    });
    test("add note no args", ()=> {
        expect(() => {
            notes.addNote()
        }).toThrow(TypeError)
    });

    test("add note only api", ()=> {
        expect(() => {
            notes.addNote("/api")
        }).toThrow(TypeError)
    });

    test("add note no text", ()=> {
        expect(() => {
            notes.addNote("/api", 2)
        }).toThrow(TypeError)
    });
});
