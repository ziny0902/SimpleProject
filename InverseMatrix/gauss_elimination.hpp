#include <boost/numeric/ublas/matrix.hpp>
#include <boost/numeric/ublas/matrix_proxy.hpp>
#include <boost/numeric/ublas/assignment.hpp>
#include <boost/numeric/ublas/io.hpp>
#include <boost/numeric/ublas/lu.hpp>
#include <boost/spirit/include/karma.hpp>
#include <boost/multi_array.hpp>
#include "log.hpp"

using namespace user::log;
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
    BOOST_LOG_SEV(main_log, 0) << "Row(" << j+1 << ") - " 
    <<"(" << factor << ")" <<  "*Row(" << i+1 << ")" ;
    for(int k = 0; k < col; k++){
        A(j,k) = A(j,k) - A(i,k)*factor;
        if(A.size2() == A.size1())
            inv(j,k) = inv(j,k) - inv(i,k)*factor;
    } 
}

template<typename T>
int find_max_row(const int srow, boost::numeric::ublas::matrix<T>& A)
{
    int rows = A.size1();
    double max = std::abs<double>(A(srow, srow));
    int max_row = srow;
    for( int row = srow+1; row < rows; row++){
        int i = row;
        double abs_val = std::abs<double>(A(i, i));
        if( abs_val  > max ){
            max = abs_val;
            max_row = i;
        }
    }
    return max_row;
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


    BOOST_LOG_SEV(main_log, 0) << karma::format(auto_ % '\t' % karma::eol, make_view(A)) << "\n";

    for(int i=0; i < row-1; i++)
    {
        BOOST_LOG_SEV(main_log, 0) << "pivot (" << 
            i+1 << "," << i+1 << "): " ;

        // partial pivot
        int max_row = find_max_row(i, A);

        if( i != max_row ){
            boost::numeric::ublas::row(A, i).swap (
               boost::numeric::ublas::row(A, max_row)
                   );
            BOOST_LOG_SEV(main_log, 0) << "swap row " << i+1 << " <-> " << max_row+1 ;
            P(i) = max_row;

            if(A.size1() == A.size2()){
               boost::numeric::ublas::row(inv, i).swap (
                   boost::numeric::ublas::row(inv, max_row)
                   );
               boost::numeric::ublas::row(LU, i).swap (
                   boost::numeric::ublas::row(LU, max_row)
                   );
            }
        }
        // pivot can't be zero
        if(A(max_row, max_row)==0)
        {
            return false;
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

        BOOST_LOG_SEV(main_log, 0) << "A : " ;
        using namespace karma;
        BOOST_LOG_SEV(main_log, 0) << karma::format(auto_ % '\t' % karma::eol, make_view(A)) << "\n";
        if(row != col) continue;
        BOOST_LOG_SEV(main_log, 0) << LU ;
        BOOST_LOG_SEV(main_log, 0) << "LU : " ;
        BOOST_LOG_SEV(main_log, 0) << karma::format(auto_ % '\t' % karma::eol, make_view(LU)) << "\n";
    }

    if(row != col ) return true;
    if(A(row-1, row -1) == 0 ) {
        // Zero pivot
        return false;
    }

    BOOST_LOG_SEV(main_log, 0) << "square matrix - inversiable" ;

    LU(row-1, row-1) = A(row-1, row-1);

    BOOST_LOG_SEV(main_log, 0) << "A : " ;
    BOOST_LOG_SEV(main_log, 0) << karma::format(auto_ % '\t' % karma::eol, make_view(A)) << "\n";

    BOOST_LOG_SEV(main_log, 0) << "LU : " ;
    BOOST_LOG_SEV(main_log, 0) << karma::format(auto_ % '\t' % karma::eol, make_view(LU)) << "\n";

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
        BOOST_LOG_SEV(main_log, 3) << "no solution" ;
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

        BOOST_LOG_SEV(main_log, 0) << "pivot (" << 
            i+1 << "," << pivot_c+1 << "): " ;

        //reached end of matrix.
        if(i==0) break;

        for(int j=(i-1); j >= 0; j--)
        {
            double x = A(j,pivot_c)/A(i,pivot_c);
            subtract_row(A, j, i, x, inv);
        }

        BOOST_LOG_SEV(main_log, 0) << karma::format(auto_ % '\t' % karma::eol, make_view(A)) << "\n";
    }

    if(pivot_c != 0) {
        // submatrix backward elimination.
        return backward_elimination(A, pivot_c+1, pivot_c +1, inv);
    }
    return true;
}


