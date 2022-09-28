

#include <iostream>
#include <cstdlib>
#include <cstring>
#include <stdexcept>
#include "calReader.h"

#include "args.hpp"


// namespace Args{
// template <typename Iterator>
// bool parse_args(Iterator first, Iterator last, std::vector<std::string>& v){ return true;}
// }
void args_test( void )
{
	// std::string args=" -a -b --backup=ttt \"test\" -a";
	std::string args=" -a -b  --level \"test\"";
	Args::args_t v;
	Args::parse_args<std::string::const_iterator> args_grammer;
	using boost::spirit::ascii::space;
	std::string::const_iterator first = args.begin();
	std::string::const_iterator end = args.end();
  if ( phrase_parse(first, end, args_grammer, space, v) ){
		std::cout << "parser sucess" << std::endl;
		std::cout << v.file << std::endl;
		std::cout << v.options.size() << std::endl;
		std::cout << boost::get<std::string>(v.options[2]) << std::endl;
		// std::cout << boost::fusion::as_vector(v) << std::endl;
  }
  else {
		std::cout << "parser fail" << std::endl;
  }
}

int 
main(const int argc, const char * argv[]) {
	args_test();
	return 0;

	if (argc == 2) {
		cal::calReader reader;
		reader.parseFromFile(argv[1]);
		return 0;
	} if (argc == 1) {
		cal::calReader reader;
		reader.parseFromString(
				"a=10\n\
				b=1; c=0\n\
				\n\
				2 * -( cos( a * %pi/360)+6*4^2)+3/2*66.6, 2+3\n \n8+2*sqrt(9^5)\n");
		try{
		std::vector<double> dvect = reader.eval();
		std::cout << "Result: ";
		for( auto d : dvect){
			std::cout << d << " ";
		}
		std::cout << std::endl;
		}  catch (std::invalid_argument &e) {
			std::cerr << e.what() << std::endl;
			return 1;

		}

		// std::cout << "Result: " << reader.eval() << std::endl;
		// cal::calReader reader;
		// reader.parseFromStream(std::cin);
		return 0;	 	
	} else {
		std::cout << "Usage: ./" << argv[0] << " <file to be parsed>"  << "\n";
		return 1;
	} // end else
} // end main
