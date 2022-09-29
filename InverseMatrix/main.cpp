#include <stdexcept>
#include <fstream>
#include "log.hpp"
#include "args.hpp"
#include "calReader.h"
#include "gauss_elimination.hpp"

void print_usage(void)
{
  std::cout <<"Usage: inverse [option] [file]" << std::endl;
  std::cout << std::endl;
  std::cout <<"option:" << std::endl;
  std::cout <<"\t--help, --level=#NUM(0-3)" << std::endl;
  std::cout << std::endl;
  std::cout <<"file format:" << std::endl;
  std::cout <<"\texp ,exp .. ,exp" << std::endl;
  std::cout <<"\t..." << std::endl;
  std::cout <<"\texp ,exp .. ,exp" << std::endl;
  std::cout << std::endl;
  std::cout <<"ex):" << std::endl;
  std::cout <<"\t2*3, 7*sqrt(9)" << std::endl;
  std::cout <<"\t2^2, -(8+9)^2" << std::endl;
}
void print_message_usage_and_exit(std::string msg)
{
  std::cout << msg << std::endl;
  print_usage();
  exit(0);
}

void log_init(std::map<std::string, std::string>& config)
{
  auto search = config.find("level");
  int lev = 0;
  if(search != config.end())
    lev = std::stoi(config["level"]);
  user::log::set_severity_level(lev);
}

int InputMatrixParse(const char *input, std::vector<double>& M)
{
  std::string str;
	cal::calReader reader;
  std::istream *in = &std::cin;
  std::ifstream fin ;
	if(input != nullptr){
    fin = std::ifstream(input);
    if (!fin) {
      BOOST_LOG_SEV(main_log, 3) << std::strerror(errno) ;
      return 0;
    }
    in = &fin;
  }
  while(getline(*in, str)){
    if(str.empty()) continue;
    if(!*in)
    {
      if(in->eof())
        break;
      else{
        BOOST_LOG_SEV(main_log, 3) << "broken pipe\n";
        return 0;
      }
    }
	  reader.parseFromString(str);
  }

  std::vector<double> dvect;
	try{
		 dvect = reader.eval();
	}  catch (std::invalid_argument &e) {
		BOOST_LOG_SEV(main_log, 3) << e.what() ;
		return 0;
	}
	//
  int rows = 0;
	rows = (int)sqrt(dvect.size());
	if( dvect.size() != (rows*rows) ){
    BOOST_LOG_SEV(main_log, 3) << "rows: " << rows;
    BOOST_LOG_SEV(main_log, 3) << "size: " << dvect.size() ;
    BOOST_LOG_SEV(main_log, 3) << "Can't invert non-square matrix" ;
    return 0;
	}
	M = dvect;
	
  return rows;
}

void main_config(int argc, char *argv[], std::map<std::string, std::string>& config)
{
  //
  // initialize option map.
  //
  const std::map<std::string, int> valid_option
  {
    {"help", 1}, {"level", 1}
  };

  int ret = initialize_config_with_args(argc, argv, config, valid_option);
  if(ret){
    print_message_usage_and_exit("Invalid argument");
  }
  // check help option flag
  auto search = config.find("help");
  if( search != config.end() ){
    print_usage();
    exit(0);
  }
  
  // validate log level.
  {
    auto search = config.find("level");
    if( search != config.end() ){
      std::string lev = config["level"];
      if(lev.size() != 1){
        print_message_usage_and_exit("Invalid level");
      }
      std::size_t pos {};
      std::stoi(lev, &pos, 4);
      if(pos!=1){
        print_message_usage_and_exit("Invalid level");
      }
    }
  }
}

#include <filesystem>
int main(int argc, char* argv[])
{
  user::log::main_log_init(); 
  std::map<std::string, std::string> config;
  main_config(argc, argv, config);
  log_init(config);
  const char *input = NULL;
  {
    auto search = config.find("filename");
    if( search != config.end())
    {
      namespace fs = std::filesystem;
      const fs::path filepath{ config["filename"] };
      if( !std::filesystem::exists(filepath) ){
        print_message_usage_and_exit("file does not exist");
      }
      input = config["filename"].c_str();
    }
  }
  std::vector<double> M;
  int row = InputMatrixParse(input, M);
  if(row == 0){
    BOOST_LOG_SEV(main_log, 3) << "Invalid data\n";
    return 0;
  }
  int col = M.size()/row;

  boost::numeric::ublas::matrix<double> A(row, col);
  boost::numeric::ublas::matrix<double> I(row, row);
  boost::numeric::ublas::matrix<double> LU(row, row);
  boost::numeric::ublas::permutation_matrix<std::size_t> P(row);
  I.assign(identity_matrix<double> (row));
  LU.assign(identity_matrix<double> (row));

  int ir = 0;
  int ic = 0;
  for(auto d : M){
    A(ir, ic) = d;
    ic++;
    ic = ic%col; 
    if(ic == 0) ir++;
  }

  // Gauss
  BOOST_LOG_SEV(main_log, 0) << "forward elimination" ;
  bool Fret = forward_elimination<double>(A, I, LU, P);
  BOOST_LOG_SEV(main_log, 0) << std::boolalpha << Fret ;
  if(!Fret){
    BOOST_LOG_SEV(main_log, 3) << "Matrix is not inversiable." << std::endl;
    return 1;
  }

  // Jordan Method
  BOOST_LOG_SEV(main_log, 0) << "backward elimination" ;
  bool Bret = backward_elimination<double>(A, A.size1(), A.size2(), I);
  BOOST_LOG_SEV(main_log, 0) << std::boolalpha << Bret ;

  BOOST_LOG_SEV(main_log, 0) << karma::format(auto_ % '\t' % karma::eol, make_view(A)) << "\n";

  // Inverse matrix exist only if the matrix is square matrix
  // if forward elimination is sucess then the matrix is inversiable
  if(row == col && Fret)
  {
    BOOST_LOG_SEV(main_log, 1) << "Inverse matrix (by gauss Jordan)" ;
    BOOST_LOG_SEV(main_log, 1) << karma::format(auto_ % '\t' % karma::eol, make_view(I)) << "\n";

    BOOST_LOG_SEV(main_log, 1) << "LU matrix" ;
    BOOST_LOG_SEV(main_log, 1) << karma::format(auto_ % '\t' % karma::eol, make_view(LU)) << "\n";
    BOOST_LOG_SEV(main_log, 1) << "permutation matrix" ;
    BOOST_LOG_SEV(main_log, 1) << P ;

    // Test LU Decomposition by caculating inverse matrix.
    boost::numeric::ublas::matrix<double> inverse(row, row);
    inverse.assign(identity_matrix<double> (row));
    lu_substitute(LU, P, inverse);

    BOOST_LOG_SEV(main_log, 1) << "inverse matrix (by LU)" ;
    BOOST_LOG_SEV(main_log, 2) << karma::format(auto_ % '\t' % karma::eol, make_view(inverse)) << "\n";
  }

  return 0;
}
