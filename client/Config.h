//
// Created by Borchers, Henry Samuel on 2019-08-16.
//

#ifndef AVDATABASE_CONFIG_H
#define AVDATABASE_CONFIG_H

#include <QObject>

class Config: public QObject {
    Q_OBJECT
public:
    explicit Config(QObject *parent=0);

//signals:
//    void setServerUrl(int d);
//    void sendToQml(int count);

public slots:
    void setServerUrl(const std::string &url);
};


#endif //AVDATABASE_CONFIG_H
