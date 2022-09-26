#include <iostream>
#include <cstdlib>
#include <cstring>
#include <stdexcept>
#include "calReader.h"

int 
main(const int argc, const char * argv[]) {
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
