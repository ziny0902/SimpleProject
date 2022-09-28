#ifndef __USER_LOG_H__
#define __USER_LOG_H__

#include <boost/log/common.hpp>
#include <boost/log/core.hpp>
#include <boost/log/sources/global_logger_storage.hpp>
#include <boost/log/sources/severity_logger.hpp>
#include <boost/log/expressions.hpp>
#include <boost/log/attributes.hpp>
#include <boost/log/utility/setup/console.hpp>
namespace user {
    namespace log{
        BOOST_LOG_ATTRIBUTE_KEYWORD(severity, "Severity", int)
        BOOST_LOG_GLOBAL_LOGGER(main, boost::log::sources::severity_logger_mt< >)
        inline void set_severity_level(const int lev){
            using namespace boost::log;
            core::get()->set_filter( severity  >= lev );
        }
        extern boost::log::sources::severity_logger_mt< >& main_log; 
        void main_log_init();
    }
}
/*
 * use case
 *
#include "log.hpp"

...
{
    ...
    BOOST_LOG_SEV(usr::log::main_log, 0) << "square matrix - inversiable" ;
    ...
}
int main(...)
{
    user::log::main_log_init(); 
    ...
    BOOST_LOG_SEV(usr::log::main_log, 0) << "..." ;
}
 */

#endif
