import QtQuick 2.9
import QtQuick.Controls 2.4
import QtQuick.Layouts 1.3

Dialog{
    id: editingDialog
    x: (parent.width - width)/2
    y: (parent.height - height) / 2
    width: 400
    title: "Edit"
    modal: true

    property alias projectTitle: titleData.text
    property alias projectCode: projectCodeData.text
    property alias status: statusData.text
    property alias currentLocation: currentLocationData.text
    padding: 20
    closePolicy: Popup.CloseOnEscape
    contentItem:Item{
        GridLayout{
            columns: 8

            anchors.right: parent.right
            anchors.left: parent.left
            anchors.top: parent.top
            Label{
                text: "Title"
                Layout.columnSpan: 2
            }
            TextField{
                id: titleData

                Layout.columnSpan: 6
                Layout.fillWidth: true
            }
            Label{
                text: "Project Code"
                Layout.columnSpan: 2
            }
            TextField{
                id: projectCodeData

                Layout.columnSpan: 6
                Layout.fillWidth: true
            }
            Label{
                text: "Status"
                Layout.columnSpan: 2
            }
            TextField{
                id: statusData
                Layout.columnSpan: 6
                Layout.fillWidth: true
            }
            Label{
                text: "Current Location"
                Layout.columnSpan: 2
            }
            TextField{
                id: currentLocationData
                Layout.columnSpan: 6
                Layout.fillWidth: true
            }
        }

    }
    standardButtons: StandardButton.Save | StandardButton.Cancel
}
