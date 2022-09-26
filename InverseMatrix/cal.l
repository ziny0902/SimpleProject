%{
#include <string>

/* Implementation of yyFlexScanner */ 
#include "../calScanner.h"
#undef  YY_DECL
#define YY_DECL int cal::calScanner::yylex( \
  cal::calParser::semantic_type * const lval, \
  cal::calParser::location_type* loc)

/* typedef to make the returns for the tokens shorter */
using token = cal::calParser::token;

/* define yyterminate as this instead of NULL */
#define yyterminate() return( token::END )

/* msvc2010 requires that we exclude this header file. */
#define YY_NO_UNISTD_H

/* update location on matching */
#define YY_USER_ACTION loc->step(); loc->columns(yyleng);

%}

%option nodefault
%option yyclass="cal::calScanner"
%option noyywrap
%option c++
%option prefix="yycal"

%x MULTI_LINE_COMMENT
%x SINGLE_LINE_COMMENT

WS [ \t\b\f\r]+

%%
%{          
/* Executed at the beginning of yylex */
yylval = lval;
%}
 
 /* ### ADD TOKEN MATCHING RULES HERE ###
 
 /* --- Example ------------------------------------------------------------- */

 /* Whitespaces and New Lines */

{WS} { ; }
\n { loc->lines(); return token::CRLF; }

"%pi" { return token::C_PI; }
"%e" { return token::C_E; }
"," { return token::COMMA;}
"=" { return token::EQ;}
";" { return token::SEMICOLON;}

[A-Za-z][A-Za-z0-9_-]* {
		yylval->build<std::string>(yytext);
    return token::NAME;
}

[0-9][0-9]* {
		yylval->build<std::string>(yytext);
		return token::NUMBER;
	}

 /* Floating Point: +1.02e10, 1.003, -1e-3, .0 */
[0-9]*\.[0-9]+([Ee][+-]?[0-9]+)? {
		yylval->build<std::string>(yytext);
		return token::NUMBER;
	}

"+" {
		yylval->build<std::string>(yytext);
		return token::PLUS;
}

"-" {
		yylval->build<std::string>(yytext);
		return token::MINUS;
}

"/" {
		yylval->build<std::string>(yytext);
		return token::BIOP;
}

"*" {
		yylval->build<std::string>(yytext);
		return token::BIOP;
}

"^" {
		yylval->build<std::string>(yytext);
		return token::BIOP;
}

"(" {
		return token::LPAREN;
}

")" {
		return token::RPAREN;
  }

<<EOF>>    { return token::END; }

. { 
    throw cal::calParser::syntax_error
     (*loc, "invalid character: " + std::string(yytext)); 
   }

%%

	
