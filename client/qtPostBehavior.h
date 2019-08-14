//
// Created by Borchers, Henry Samuel on 2019-06-28.
//

#ifndef AVDATABASEEDITOR_QTPOSTBEHAVIOR_H
#define AVDATABASEEDITOR_QTPOSTBEHAVIOR_H

#include "postBehavior.h"


class qtPostBehavior: public PostBehavior {
public:
    long send(const std::string &url, std::string &response_text, const std::map<std::string, std::string > &form_data) override;
};


#endif //AVDATABASEEDITOR_QTPOSTBEHAVIOR_H
