import QtQuick 2.9
import QtQuick.Controls 1.4
import QtQml.Models 2.3
import QtQuick.Controls.Styles 1.4

Item{
    id: root
    property alias model: projectsView.model
    property alias contextMenu: loader_contextMenu.sourceComponent
    property bool validSelection: false
    signal selectionChanged
    signal activated(int row)
    SystemPalette { id: appPalette; colorGroup: SystemPalette.Active }
    property alias currentRow: projectsView.currentRow
    Loader {
        id: loader_contextMenu
        sourceComponent: Menu{

        }
    }

    TableView{
        id: projectsView
        anchors.fill: root
        frameVisible: true
        selectionMode: SelectionMode.SingleSelection
        Connections{
            target: projectsView.selection
            onSelectionChanged: {

                console.log("changed")

                root.selectionChanged()

            }

        }

        onActivated: {
            root.activated(row)
        }
        TableViewColumn{
            title: "Title"
            role: "title"
        }
        TableViewColumn{
            title: "Project Code"
            role: "project_code"

        }
        TableViewColumn{
            title: "Status"
            role: "status"

        }
        TableViewColumn{
            title: "Current Location"
            role: "current_location"

        }
        itemDelegate: Item {

            width: parent.width
            Text {
                anchors{
                    left: parent.left
                }
                anchors.leftMargin: 8
                width: parent.width

                height: parent.height
                text: styleData.value
                color: styleData.textColor
                elide: styleData.elideMode
            }
            MouseArea{
                anchors.fill: parent
                propagateComposedEvents: true
                acceptedButtons: Qt.RightButton
                onClicked: {
                    console.log("clicked "+ styleData.row)

                    projectsView.selection.clear()
//                    projectsView.currentRow = styleData.row
                    projectsView.selection.select(styleData.row)
                    loader_contextMenu.item.popup()
                }

            }

        }
    }
    states: [
        State {
            name: "validSelection"
            when: currentRow >= 0
            PropertyChanges {
                target: root
                validSelection: true
            }
        },
        State {
            name: "invalidSelection"
            when: currentRow < 0
            PropertyChanges {
                target: root
                validSelection: false
            }
        }
    ]
}
