import {getWidget} from "../tyko/static/js/widgets";

describe('Testing text widget', ()=> {
    let metadataWidget;

    beforeEach(()=>{
        document.body.innerHTML =
            '<body>' +
                '<div id="sample">' +
                '</div>' +
            '   <script src="https://code.jquery.com/jquery-3.3.1.min.js" integrity="sha256-FgpCb/KJQlLNfOu91ta32o/NMZxltwRo8QtmkMRdAu8=" crossorigin="anonymous"></script>' +
            '</body>';
        metadataWidget = getWidget(
            "textEditor",
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
        // const paragraphElement = contentElement.firstChild;
        expect(contentElement.innerText).toBe("Sample text");
    });

    test("After swapping state is edit", ()=>{
        metadataWidget.swap();
        expect(metadataWidget.stateName()).toBe("edit");
    });

    test("Swaps back to view mode after being in edit mode", ()=>{
        expect(metadataWidget.stateName()).toBe("view");

        metadataWidget.swap();
        expect(metadataWidget.stateName()).toBe("edit");

        metadataWidget.swap();
        expect(metadataWidget.stateName()).toBe("view");
    });

    test("Selecting edit mode changed it to edit mode", ()=>{
        expect(metadataWidget.stateName()).toBe("view");
        metadataWidget.editMode();
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
    });


});

describe("test select widget", ()=>{
    beforeEach(()=>{
        document.body.innerHTML =
            '<div id="sample">' +

            '</div>';
    });
    test("select widget adds options in editmode", ()=>{
        const sampleElement = document.getElementById("sample");
        let selectWidget = getWidget(
            "selectEditor",
            sampleElement,
            "sampleField",
            "Sample text");
        selectWidget.options = ['one', 'two'];
        expect(selectWidget.state).toBe("view");
        selectWidget.editMode();
        expect(selectWidget.state).toBe("edit");
    })
});

describe("Widget factory", ()=>{
    beforeEach(()=>{
        document.body.innerHTML =
            '<div id="sample">' +

            '</div>';
    });
    test("Get text widgets", ()=>{
        const sampleElement = document.getElementById("sample");
        let res = getWidget("textEditor", sampleElement, "sampleField", "Sample text");
        expect(res.inputType).toBe("text");
        expect(res.widgetType).toBe("textEditor");

    });

    test("get datePicker", ()=>{

        global.$ = $;
        const sampleElement = document.getElementById("sample");
        let res = getWidget("datePicker", sampleElement, "sampleField", "Sample text");
        expect(res.widgetType).toBe("datePicker");
        res.swap();
        res.draw();
        expect(sampleElement.innerHTML).toContain("datepicker");

    });

    test("get select widget", ()=>{
        const sampleElement = document.getElementById("sample");
        let res = getWidget("selectEditor", sampleElement, "sampleField", "Sample text");
        expect(res.widgetType).toBe("selectEditor");

        res.swap();
        res.draw();
        expect(sampleElement.innerHTML).toContain("select");
    });
    test("get numberPicker widget", ()=>{
        const sampleElement = document.getElementById("sample");
        let res = getWidget("numberPicker", sampleElement, "sampleField", "Sample text");
        expect(res.widgetType).toBe("numberPicker");
        expect(res.stateName()).toBe("view");
        res.swap();
        expect(res.stateName()).toBe("edit");
        res.draw();
        expect(sampleElement.innerHTML).toContain("input");
        expect(sampleElement.innerHTML).toContain('type="number"');
    });
});