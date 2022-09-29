#include <stdexcept>
#include "args_internal.hpp"
#include "args.hpp"

class arg_opt_visitor : public boost::static_visitor<std::vector<std::string>>
{
public:
	std::vector<std::string> operator()(std::string value) const
  {
		std::vector<std::string> v;
		v.push_back(value);
    return v;
  }
	std::vector<std::string> operator()(Args::name_value_t value) const
  {
		std::vector<std::string> v;
		v.push_back(value.name);
		v.push_back(value.value);
    return v;
  }
};

int initialize_config_with_args(int argc, char* argv[], std::map<std::string, std::string>& config, const std::map<std::string, int>& valid_option)
{
	int i;
	std::string str_argv="";
	for(i=1; i < argc; i++){
		str_argv += argv[i];
		str_argv += " ";
	}
	Args::args_t para;
	Args::parse_args<std::string::const_iterator> args_grammer;
	using boost::spirit::ascii::space;
	std::string::const_iterator first = str_argv.begin();
	std::string::const_iterator end = str_argv.end();
  if (!phrase_parse(first, end, args_grammer, space, para) ){
		std::cerr<< "parser fail" << std::endl;
		return -1;
  }
  try {
		std::for_each(
			para.options.begin(), para.options.end(), 
			[&](Args::option_t &opt){ 
				std::vector<std::string>v = boost::apply_visitor(arg_opt_visitor(), opt);
				if(v.size() == 1){
					std::string& opt_str = v[0];
					std::string str = "";
					for( i = 0; i < opt_str.size(); i++){
						str=""; 
							str.push_back(opt_str[i]);
    					auto search = valid_option.find(str);
    					if( search == valid_option.end() ){
    						throw std::invalid_argument( "Unkown option: -" + str);
    					}
							config[str] = "1";
					}
				}else{
    			auto search = valid_option.find(v[0]);
    			if( search == valid_option.end() ){
    				throw std::invalid_argument( "Unkown option: --" + v[0]);
    			}
					config[v[0]] = v[1];
				}
			}
		);
	} catch (std::invalid_argument &e) {
		std::cerr << e.what() << std::endl;
		return -1;
	}
	if(para.file.size() > 0)
		config["filename"] = para.file;
	return 0;
}

