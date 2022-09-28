#include "log.hpp"

BOOST_LOG_GLOBAL_LOGGER_DEFAULT(user::log::main, boost::log::sources::severity_logger_mt< >)
namespace user{
  namespace log {
  boost::log::sources::severity_logger_mt< >& main_log = user::log::main::get();

  namespace logging = boost::log;
  namespace expr = boost::log::expressions;
  namespace keywords = boost::log::keywords;
  void main_log_init()
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
  }
}
}
