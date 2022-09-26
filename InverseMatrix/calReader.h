#ifndef cal_READER_H
#define cal_READER_H

#include <string>
#include <cstddef>
#include <iostream>
#include <istream>
#include <sstream>
#include <vector>
#include "ast.hpp"

namespace cal {

class calScanner;
class calParser;

class calReader {
friend class calParser;

	
public:
	calReader() :
		parser(nullptr),
		scanner(nullptr) {}

	virtual ~calReader();

	void parseFromFile(const std::string &filename);
	void parseFromString(const std::string &str);
	void parseFromStream(std::istream &stream);
	void moveAST(std::unique_ptr<ExprAST>);
	void push_back(std::unique_ptr<ExprAST> &exprast){
		exprasts.push_back(std::move(exprast));
	}
	std::vector<double> eval();

private:
	std::unique_ptr<ExprAST> exprast; 
	std::vector<std::unique_ptr<ExprAST>> exprasts; 
	std::map<std::string, double> symbol;

	////////////////////////////////////////////////////////////////////////////
	// Flex (Lex) / Bison (Yacc)
	////////////////////////////////////////////////////////////////////////////	
	calParser *parser;
	calScanner *scanner;

	////////////////////////////////////////////////////////////////////////////
	// Parsing callbacks.
	////////////////////////////////////////////////////////////////////////////

	// ### ADD PARSER CALLBACKS HERE ###
	
	// --- Example -------------------------------------------------------------
	void readCallback(const std::string &type, const std::string &text) { 
		std::cout << type << ": " << text << '\n';
	}
	// -------------------------------------------------------------------------	
	
}; // end class

} // end namespace
#endif

