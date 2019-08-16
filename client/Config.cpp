//
// Created by Borchers, Henry Samuel on 2019-08-16.
//

#include <iostream>
#include "Config.h"
#include <QDebug>
Config::Config(QObject *parent) : QObject(parent) {

}

void Config::setServerUrl(const std::string &url) {
    std::cerr << "changing to " << url << "\n";

}
