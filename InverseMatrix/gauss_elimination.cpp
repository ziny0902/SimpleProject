#include <boost/numeric/ublas/matrix.hpp>
#include <boost/numeric/ublas/matrix_proxy.hpp>
#include <boost/numeric/ublas/assignment.hpp>
#include <boost/numeric/ublas/io.hpp>
#include <boost/numeric/ublas/lu.hpp>
#include <boost/spirit/include/karma.hpp>
#include <boost/multi_array.hpp>

#include <iostream>

using namespace boost::numeric::ublas;
namespace karma = boost::spirit::karma;

template <typename T> 
boost::const_multi_array_ref<T, 2> make_view(boost::numeric::ublas::matrix<T> const& m) {
    return  boost::const_multi_array_ref<T,2> (
            &*m.data().begin(),
            boost::extents[m.size1()][m.size2()]
        );
}

// row(j) = row(j) - factor*row(i)
template<typename T> inline
void subtract_row(boost::numeric::ublas::matrix<T>& A, 
        int j,
        int i,
        T factor,
        boost::numeric::ublas::matrix<T>& inv) 
{
    int col = A.size2();
    if(factor == 0 ) return;
    std::cout << "Row(" << j+1 << ") - " 
    <<"(" << factor << ")" <<  "*Row(" << i+1 << ")" << std::endl;
    for(int k = 0; k < col; k++){
        A(j,k) = A(j,k) - A(i,k)*factor;
        if(A.size2() == A.size1())
            inv(j,k) = inv(j,k) - inv(i,k)*factor;
    } 
}

using namespace karma;
template<class T>
bool forward_elimination(boost::numeric::ublas::matrix<T>& A,
        boost::numeric::ublas::matrix<T>& inv,
        boost::numeric::ublas::matrix<T>& LU ,
        boost::numeric::ublas::permutation_matrix<std::size_t> &P
        )
{
    int row = A.size1();
    int col = A.size2();


    std::cout << karma::format(auto_ % '\t' % karma::eol, make_view(A)) << "\n";

    for(int i=0; i < row-1; i++)
    {
        std::cout << "pivot (" << 
            i+1 << "," << i+1 << "): " << std::endl;

        // if the pivot is zero
        // then row swap.
        if(A(i,i)==0)
        {
            int j;
            for(j=i+1; j < row; j++)
            {
                if(A(j,i)==0) continue;
                boost::numeric::ublas::row(A, i).swap (
                   boost::numeric::ublas::row(A,j)
                       );
                std::cout << "swap row " << i+1 << " <-> " << j+1 << std::endl;
                P(j) = i;

                if(A.size1() == A.size2()){
                   boost::numeric::ublas::row(inv, i).swap (
                       boost::numeric::ublas::row(inv,j)
                       );
                   boost::numeric::ublas::row(LU, i).swap (
                       boost::numeric::ublas::row(LU,j)
                       );
                }
                break;
            }
            if(j >= row) return false;
        }

        double pVal = A(i,i);
        for( int j = 0; j < A.size2(); j++)
        {
            if(A.size1() == A.size2()) {
                // save Upper matrix value
                if(j >= i)
                    LU(i,j) = A(i,j);
                inv(i,j)=inv(i, j)/pVal;
            }

            A(i,j)=A(i, j)/pVal;
        }

        for(int j=(i+1); j < row; j++)
        {
            double x = A(j,i)/A(i,i);
            if(x==0) continue;
            // if the matrix is square matrix
            // then save Lower matrix value
            if(A.size1() == A.size2())
                LU(j,i)=A(j,i)/pVal;
            subtract_row(A, j, i, x, inv);
        }

        std::cout << "A : " << std::endl;
        using namespace karma;
        std::cout << karma::format(auto_ % '\t' % karma::eol, make_view(A)) << "\n";
        if(row != col) continue;
        std::cout << LU << std::endl;
        std::cout << "LU : " << std::endl;
        std::cout << karma::format(auto_ % '\t' % karma::eol, make_view(LU)) << "\n";
    }

    if(row != col ) return true;
    if(A(row-1, row -1) == 0 ) {
        // Zero pivot
        return false;
    }

    std::cout << "square matrix - inversiable" << std::endl;

    LU(row-1, row-1) = A(row-1, row-1);

    std::cout << "A : " << std::endl;
    std::cout << karma::format(auto_ % '\t' % karma::eol, make_view(A)) << "\n";

    std::cout << "LU : " << std::endl;
    std::cout << karma::format(auto_ % '\t' % karma::eol, make_view(LU)) << "\n";

    return true;
}

#include <boost/numeric/ublas/matrix_proxy.hpp>
template<class T>
bool backward_elimination(boost::numeric::ublas::matrix<T>& A, 
        int row, 
        int col,
        boost::numeric::ublas::matrix<T>& inv
        )
{

    if( row == 0 ) return false;

    int pivot_c = 0;
    for (int i = 0; i < col ; i++)
    {
        if(((double)(A(row-1, i))) != 0) {
            pivot_c = i;
            break;
        }
    }
    if(col > row && pivot_c == col -1){
        // no solution
        std::cout << "no solution" << std::endl;
        return false;
    }
    if( A(row - 1, pivot_c) == 0) {
        //submatrix backward elimination.
        return backward_elimination(A, row - 1, col , inv);
        
    }

    for(int i=row-1; i >= 0; i--, pivot_c--)
    {
        // no need to swap row.
        // all pivot should be non zero

        if(A(i,pivot_c)==0) break;
        if(i==0 && pivot_c != 0) break;

        double pVal = A(i,pivot_c);
        for( int j = 0; j < A.size2(); j++)
        {
            A(i,j)=A(i, j)/pVal;
            if(A.size1() == A.size2()) {
                inv(i,j)=inv(i, j)/pVal;
            }
        }

        std::cout << "pivot (" << 
            i+1 << "," << pivot_c+1 << "): " << std::endl;

        //reached end of matrix.
        if(i==0) break;

        for(int j=(i-1); j >= 0; j--)
        {
            double x = A(j,pivot_c)/A(i,pivot_c);
            subtract_row(A, j, i, x, inv);
        }

        std::cout << karma::format(auto_ % '\t' % karma::eol, make_view(A)) << "\n";
    }

    if(pivot_c != 0) {
        // submatrix backward elimination.
        return backward_elimination(A, pivot_c+1, pivot_c +1, inv);
    }
    return true;
}

#include<boost/tokenizer.hpp>

int argParser(std::string const& s, std::vector<double>& data)
{
    typedef boost::tokenizer<boost::char_separator<char> > tokenizer;
    boost::char_separator<char> row_sep(";"); 
    boost::char_separator<char> col_sep(" "); 
    tokenizer row_tok(s, row_sep);

    std::vector<std::string> row_strs;
    int row=0;
    for (tokenizer::iterator tok_iter = row_tok.begin();
            tok_iter != row_tok.end(); ++tok_iter)
    {
        row++;
        row_strs.push_back(*tok_iter);
    }

    int col = 0;
    for(auto row_str : row_strs)
    {
        tokenizer col_tok(row_str,  col_sep);
        int cnt = 0;
        for (tokenizer::iterator tok_iter = col_tok.begin();
            tok_iter != col_tok.end(); ++tok_iter)
        {
            boost::char_separator<char> div_sep("/"); 
            tokenizer div_tok(std::string(*tok_iter), div_sep);
            tokenizer::iterator it =div_tok.begin();
            std::string a , b;
            a = *it;
            it++;
            if(it == div_tok.end()){
                data.push_back(std::stod(*tok_iter));
            }
            else {
                b = *it;
                double val = std::stod(a) /std::stod(b);
                data.push_back(val);
            }
            cnt++;
        }
        if(col == 0) col = cnt;
        else if(col != cnt) {
            std::cout << "column number not match (" 
                << cnt << ", " << col << ")" <<  std::endl;
            return 0;
        }
    }

    return row;
}

#ifdef __BOOST_SPIRIT_PARSER__
#include <boost/config/warning_disable.hpp>
#include <boost/spirit/home/x3.hpp>

namespace client
{
    namespace x3 = boost::spirit::x3;
    namespace ascii = boost::spirit::x3::ascii;

    ///////////////////////////////////////////////////////////////////////////
    //  Our number list compiler
    ///////////////////////////////////////////////////////////////////////////
    //[tutorial_numlist4
    template <typename Iterator>
    bool parse_numbers(Iterator first, Iterator last, std::vector<double>& v)
    {
        using x3::double_;
        using x3::phrase_parse;
        using x3::_attr;
        using ascii::space;

        bool r = phrase_parse(first, last,

            //  Begin grammar
            (
                double_ % ','
            )
            ,
            //  End grammar

            space, v);

        if (first != last) // fail if we did not get a full match
            return false;
        return r;
    }
    //]
}
#endif //__BOOST_SPIRIT_PARSER__


#include <stdexcept>
#include <fstream>
#include "calReader.h"
int InputMatrixParse(char *input, std::vector<double>& M)
{
    std::string str;
    int rows = 0;
	cal::calReader reader;
    std::istream *in = &std::cin;
    std::ifstream fin ;
	if(input != nullptr){
        fin = std::ifstream(input);
        in = &fin;
    }
    while(getline(*in, str)){
        if(str.empty()) continue;
        if(!*in)
        {
            if(in->eof())
                break;
            else{
                std::cout << "broken pipe\n";
                return 0;
            }
        }
#ifdef __BOOST_SPIRIT_PARSER__
        if(!client::parse_numbers(str.begin(), str.end(), M))
        {
            std::cout << "Invalid Data: " << str << std::endl;
            return 0;

        }
#endif
		reader.parseFromString(str);
        rows += 1;
    }

    std::vector<double> dvect;
	try{
		 dvect = reader.eval();
	}  catch (std::invalid_argument &e) {
		std::cerr << e.what() << std::endl;
		return 1;
	}
    // display data
    // for debuging
	std::cout << "data: ";
	for( auto d : dvect){
		std::cout << d << " ";
	}
	std::cout << std::endl;
	//
	if( dvect.size() != (rows*rows) ){
        std::cout << "rows: " << rows << std::endl;
        std::cout << "size: " << dvect.size() << std::endl;
        std::cerr << "Can't invert non-square matrix" << std::endl;
        return 0;
	}
	M = dvect;
	
    return rows;
}

int main(int argc, char* argv[])
{
    std::vector<double> M;
    int row;
    char *input = NULL;
    if(argc > 2) {
        std::cout << "invalid argument" << std::endl;
        return 0;
    }
    if (argc == 2) input = argv[1];

    row = InputMatrixParse(input, M);
    if(row == 0){
        std::cout << "Invalid data\n";
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
    std::cout << "forward elimination" << std::endl;
    bool Fret = forward_elimination<double>(A, I, LU, P);
    std::cout << std::boolalpha << Fret << std::endl;

    // Jordan Method
    std::cout << "backward elimination" << std::endl;
    bool Bret = backward_elimination<double>(A, A.size1(), A.size2(), I);
    std::cout << std::boolalpha << Bret << std::endl;

    std::cout << karma::format(auto_ % '\t' % karma::eol, make_view(A)) << "\n";

    // Inverse matrix exist only if the matrix is square matrix
    // if forward elimination is sucess then the matrix is inversiable
    if(row == col && Fret)
    {
        std::cout << "Inverse matrix (by gauss Jordan)" << std::endl;
        std::cout << karma::format(auto_ % '\t' % karma::eol, make_view(I)) << "\n";

        std::cout << "LU matrix" << std::endl;
        std::cout << karma::format(auto_ % '\t' % karma::eol, make_view(LU)) << "\n";
        std::cout << "permutation matrix" << std::endl;
        std::cout << P << std::endl;

        // Test LU Decomposition by caculating inverse matrix.
        boost::numeric::ublas::matrix<double> inverse(row, row);
        inverse.assign(identity_matrix<double> (row));
        lu_substitute(LU, P, inverse);

        std::cout << "inverse matrix (by LU)" << std::endl;
        std::cout << karma::format(auto_ % '\t' % karma::eol, make_view(inverse)) << "\n";
    }

    return 0;
}
