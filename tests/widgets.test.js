import {MetadataWidget} from "../tyko/static/js/widgets";

describe('Testing widgets', ()=> {
    let metadataWidget;

    beforeEach(()=>{
        document.body.innerHTML =
            '<div id="sample">' +

            '</div>';
        metadataWidget = new MetadataWidget(
            document.getElementById("sample"),
            "sampleField",
            "Sample text"
        );
    });


    test("The default state is view", ()=>{
        expect(metadataWidget.stateName()).toBe("view");
    });
    test("The default state to contain the field text and an edit button", ()=>{
        const root = document.getElementById("sample");
        const contentElement = root.querySelector("#content");
        const paragraphElement = contentElement.firstChild;
        expect(paragraphElement.innerHTML).toBe("Sample text");
    });

    test("After swapping state is edit", ()=>{
        metadataWidget.swap();
        expect(metadataWidget.stateName()).toBe("edit");
    });


    test("Edit has an input element", ()=>{
        metadataWidget.swap();
        let root = document.getElementById("sample").firstChild;
        let labelElement = root.childNodes[0];
        expect(labelElement.tagName).toBe("LABEL");

        let inputElement = root.childNodes[1];
        expect(inputElement.tagName).toBe("INPUT");
        expect(inputElement.getAttribute("value")).toBe("Sample text")
    });

    test("Metadata API setter", ()=>{
        metadataWidget.apiRoute = "/api/item/2";
        expect(metadataWidget.apiRoute).toBe("/api/item/2");
    })
});
