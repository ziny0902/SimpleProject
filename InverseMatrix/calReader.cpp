#include <cctype>
#include <fstream>
#include <cassert>

#include "calReader.h"
#include "build/cal.yy.hpp"
#include "calScanner.h"

namespace cal {

calReader::~calReader() {
	delete scanner;
	delete parser;
} // end destructor
  //
void calReader::moveAST(std::unique_ptr<ExprAST> _ast){
	exprast = std::move(_ast);
}

std::vector<double> calReader::eval() { 
	std::vector<double> dvect;

	for (auto const& expr : exprasts) {
		double dret;
		ExprAST *ast = expr.get();
		if(ast->get() == "assign"){
			AssignmentAST *assign = (AssignmentAST *)ast;
			dret = evalAST(assign->getExpr(), symbol);
			symbol[assign->getName()] = dret;
		}
		else {
			dret = evalAST(expr.get(), symbol);
			dvect.push_back(dret);
		}

  }
	return dvect;
}

// -----------------------------------------------------------------------------

void calReader::parseFromFile(const std::string &filename) {
	std::ifstream file(filename.c_str());
	if (!file.good()) {
		std::exit(1);
	} // end if
	parseFromStream(file);
} // end method

// -----------------------------------------------------------------------------

void calReader::parseFromString(const std::string &str) {
	std::istringstream iss(str);
	parseFromStream(iss);
} // end method

// -----------------------------------------------------------------------------

void calReader::parseFromStream(std::istream &stream) {
	if (!stream.good() && stream.eof()) {
		return;
	} // end if
	
	delete scanner;
	try {
		scanner = new cal::calScanner(&stream);
	} catch (std::bad_alloc &ba) {
		std::cerr << "Failed to allocate scanner: (" <<
				ba.what() << "), exiting!!\n";
		std::exit(1);
	} // end catch

	delete parser ;
	try {
		parser = new cal::calParser(*scanner, *this);
	} catch (std::bad_alloc &ba) {
		std::cerr << "Failed to allocate parser: (" <<
				ba.what() << "), exiting!!\n";
		std::exit(1);
	} // end catch
	
	if (parser->parse() != 0) {
		std::cout << "Parse failed.\n";
		std::exit(1);
	} else {
		//std::cout << "Parse succeed.\n";
	} // end else

} // end method

} // end namespace
