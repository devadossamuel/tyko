import QtQuick 2.9
import QtQuick.Controls 2.5
import QtQuick.Dialogs 1.2
import "js/tyko.js" as Tyko

Item{
    signal getData(string url)
    onGetData: {

        Tyko.get(url)
        .then(function(response){
            myResponse.text = response
        })
        .catch(function(res){
            if(res.status === 0){
                messageDialog.text = "Failed to connect to server"
            }else{
                messageDialog.text = "Failed for unknown reason"
            }

            myResponse.text = "Failed"

            messageDialog.open()
        });
    }
    MessageDialog {
        id: messageDialog
        title: "Failed to load data"
        onAccepted: {
            Qt.quit()
        }
    }

    TextArea {
        id: myResponse
    }
}
