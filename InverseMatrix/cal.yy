%skeleton "lalr1.cc"
%require  "3.2"
%defines 
%define api.namespace {cal}
%define api.parser.class {calParser}

%code requires{
  #include <memory>
  #include <string>
  #include <cmath>
  #include "../ast.hpp"
  namespace cal {
     class calScanner;
     class calReader;
  }

}

%parse-param { calScanner &scanner }
%parse-param { calReader &reader }

%code{
   #include <iostream>
   #include <cstdlib>
   #include <fstream>
   
   #include "../calReader.h"
   #include "../calScanner.h"   
 
   #undef yylex
   #define yylex scanner.yylex

  #define make_unique_ExprAST(AST) std::unique_ptr<ExprAST>(AST.release())
}

%define api.value.type variant
%define parse.assert

// ### ADD TOKEN DEFINITIONS HERE ###

// Example ---------------------------------------------------------------------

%token               END    0     "end of file"
%token  LPAREN
%token  RPAREN
%token  C_PI
%token  C_E
%token  COMMA
%token  CRLF
%token  EQ
%token  SEMICOLON


%token <std::string> NAME
%token <std::string> NUMBER
%token <std::string> BIOP
%token <std::string> MINUS
%token <std::string> PLUS

%type <std::unique_ptr<ExprAST>> expr
%type <std::unique_ptr<ExprAST>> function 
%type <std::string> constant

// -----------------------------------------------------------------------------


%locations

%%

// ### ADD GRAMMAR RULES HERE ###
start: bodys
     | bodys newlines
     ;

bodys: 
     | body
     | bodys newlines body
body:
    exprs
    | assignments

exprs: 
     expr { reader.push_back($1); }
     | exprs COMMA expr { reader.push_back($3); }
     ;
newlines: CRLF 
     | newlines CRLF
     ;

assignment:
    NAME EQ expr {
      std::unique_ptr<ExprAST> assign = make_unique_ExprAST(std::make_unique<AssignmentAST>($1, $3));
      reader.push_back( assign );
    }
assignments: assignment
    | assignments SEMICOLON assignment
    ;

function: NAME LPAREN expr RPAREN 
        {
          $$ = make_unique_ExprAST(
            std::make_unique<FunctionAST>($1, std::move($3))
          );
        }
        ;
constant: C_PI { $$ = std::to_string(M_PI); }
        | C_E{ $$ = std::to_string(M_E); }
        ;

%left PLUS MINUS;
%left BIOP;

expr: NUMBER { $$ = make_unique_ExprAST(std::make_unique<NumberAST>($1)); }
    | NAME { $$ = make_unique_ExprAST(std::make_unique<VariableAST>($1)); }
| constant { $$ = make_unique_ExprAST(std::make_unique<NumberAST>($1)); }
| function { $$ = std::move($1);}
| PLUS expr { $$ = std::move($2); } 
| MINUS expr {
  std::unique_ptr<ExprAST>L = make_unique_ExprAST(std::make_unique<NumberAST>("-1"));
  $$ = make_unique_ExprAST(create_bi_expr( "*", std::move(L), std::move($2)));
}
| LPAREN expr RPAREN { $$ = std::move($2); }
| expr BIOP expr { 
                    $$ = make_unique_ExprAST(create_bi_expr($2, std::move($1), std::move($3)));
                 }
| expr PLUS expr { 
                    $$ = make_unique_ExprAST(create_bi_expr($2, std::move($1), std::move($3)));
                 }
| expr MINUS expr { 
                    $$ = make_unique_ExprAST(create_bi_expr($2, std::move($1), std::move($3)));
                 }
;

   
%%

void 
cal::calParser::error(const cal::calParser::location_type &l, const std::string &err_message) {
   std::cout << "Parsing Error: " << err_message << " at " << l << "\n";
}
