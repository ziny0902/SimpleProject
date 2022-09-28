#ifndef __ARGS_H__
#define __ARGS_H__
#include <string>
#include <map>

int initialize_config_with_args(int argc, char* argv[], std::map<std::string, std::string>& config, const std::map<std::string, int>& valid_option);

#endif
