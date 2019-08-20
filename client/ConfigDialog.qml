import QtQuick 2.9
import QtQuick.Controls 2.4
import QtQuick.Layouts 1.3
import QtQuick.Dialogs 1.2
Dialog{
    id: root
    title: "Connect to Database"
    visible: false
    property alias sourceURL: serverURL.text
    modality: Qt.ApplicationModal
    GridLayout {
        anchors.fill: parent

        Layout.margins: 4
        id: column
        columns: 2
        Text{
            text: "Server URL"
        }
        TextField{
            id: serverURL
            placeholderText: "Server url"
            Layout.fillWidth: true
        }
    }
    standardButtons: StandardButton.Ok | StandardButton.Cancel

}