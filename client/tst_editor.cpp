#include "projectadder.h"
#include <QtQuickTest>
#include <QQmlEngine>
#include <QQmlContext>

// TODO: create a setup the registers ProjectAdder

class Setup: public QObject
{
    Q_OBJECT

public:
     Setup(){}
public slots:
     void qmlEngineAvailable(QQmlEngine *engine){
        engine->rootContext()->setContextProperty("myContextProperty", QVariant(true));
         qmlRegisterType<ProjectAdder>("Api", 1, 0, "ProjectAdder");
     }

};
QUICK_TEST_MAIN_WITH_SETUP(editor, Setup)

#include "tst_editor.moc"
