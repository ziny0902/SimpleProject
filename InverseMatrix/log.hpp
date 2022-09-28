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
    }
}
/*
 * use case
 *
#include "log.hpp"
BOOST_LOG_GLOBAL_LOGGER_DEFAULT(user::log::main, boost::log::sources::severity_logger_mt< >)
boost::log::sources::severity_logger_mt< >& main_log = user::log::main::get();

namespace logging = boost::log;
namespace expr = boost::log::expressions;
namespace keywords = boost::log::keywords;
void log_init()
{
    logging::add_console_log
    (
        std::clog,
        keywords::format =
        (
            expr::stream
                << "> \n" << expr::smessage
        )
    );

    user::log::set_severity_level(1);
}
...
{
    ...
    BOOST_LOG_SEV(main_log, 0) << "square matrix - inversiable" ;
    ...
}
 */

#endif
