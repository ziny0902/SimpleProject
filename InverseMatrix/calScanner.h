#ifndef cal_SCANNER_H
#define cal_SCANNER_H

/* From Flex documentation:
 *   The c++ scanner is a mess. The FlexLexer.h header file relies on the
 *   following macro. This is required in order to pass the c++-multiple-scanners
 *   test in the regression suite. We get reports that it breaks inheritance.
 *   We will address this in a future release of flex, or omit the C++ scanner
 *   altogether.
 *
 * So, for now, let's define this macro too...
 */
 
#define yyFlexLexer yycalFlexLexer

#if ! defined(yyFlexLexerOnce)
#include <FlexLexer.h>
#endif

#undef yylex

#include "cal.yy.hpp"

namespace cal {

class calScanner : public yyFlexLexer {
public:
   
   calScanner(std::istream *in) : yyFlexLexer(in) {
      loc = new calParser::location_type();
   };
   virtual ~calScanner() {
      delete loc;
   };

   // Get rid of override virtual function warning.
   using FlexLexer::yylex;

   virtual
   int yylex(calParser::semantic_type * const lval, 
             calParser::location_type *location);

private:
   calParser::semantic_type *yylval = nullptr;
   calParser::location_type *loc    = nullptr;
};

} // end namespace

#endif

