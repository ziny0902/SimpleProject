#include <iostream>
#include <string>
#include "ast.hpp"
#include <cmath>

#include <stdexcept>

std::map<std::string, int> BinaryExprAST::precedence {
  {"+", 10},
  {"-", 10},
  {"*", 20},
  {"/", 20},
  {"^", 30},
};

std::unique_ptr<BinaryExprAST> 
create_bi_expr(
    std::string biop,
    std::unique_ptr<ExprAST> LHS,
    std::unique_ptr<ExprAST> RHS 
    )
{
  int lprecedence = getPrecedence((LHS.get())->get());
  
  if (lprecedence < 0){
    return std::make_unique<BinaryExprAST>(biop, std::move(LHS), std::move(RHS));
  }
  
  if(getPrecedence(biop) > lprecedence){
    BinaryExprAST *lptr= (BinaryExprAST *)LHS.get();
    std::unique_ptr<BinaryExprAST> expr 
      = create_bi_expr(biop, lptr->getRHS(), std::move(RHS));
    std::unique_ptr<ExprAST> R = std::unique_ptr<ExprAST>(expr.release());
    lptr->setRHS(R);
    return std::make_unique<BinaryExprAST>(*(BinaryExprAST *)lptr);
  }
  return std::make_unique<BinaryExprAST>(biop, std::move(LHS), std::move(RHS));
}

double evalFunc(FunctionAST *ast, std::map<std::string, double>& symbol)
{
  double dval = evalAST( ast->getExpr(), symbol );
  std::string const &func  = (std::string const &) ast->getFnuc();
  if(func == "cos"){
    return cos(dval);
  }else if(func == "sin"){
    return sin(dval);
  }else if(func == "tan"){
    return tan(dval);
  }else if(func == "exp"){
    return exp(dval);
  }else if(func == "log"){
    return log(dval);
  }else if(func == "sqrt"){
    return sqrt(dval);
  }
  else {
    throw std::invalid_argument( "[evaluation error] Unkown function: " + func);
    return .0;
  }
}

double evalAST(ExprAST *ast, std::map<std::string, double>& symbol)
{
  std::string const val = ast->get();
  //debug
  if(val == "function"){
    return evalFunc((FunctionAST *)ast, symbol);
  }
  if( val == "variable" ){
    VariableAST * var = (VariableAST *)ast;
    auto it = symbol.find(var->getName());
    if( it != symbol.end() ){
      return it->second;
    }
    else {
      throw std::invalid_argument( "[evaluation error] Unkown variable: " + var->getName());
    }
  }
  int lprecedence = getPrecedence(val);
  if (lprecedence < 0){
    return stod(val);
  }
  // LEFT
  ExprAST *L = ((BinaryExprAST *)ast)->pLHS();
  double lval = evalAST(L, symbol);
  // Right 
  ExprAST *R = ((BinaryExprAST *)ast)->pRHS();
  double rval = evalAST(R, symbol);
  if(val == "+"){
    return lval + rval;
  }else if(val == "-") {
    return lval - rval;
  }else if(val == "*") {
    return lval*rval;
  }else if(val == "/") {
    return lval/rval;
  }else if(val == "^"){
    return pow(lval, rval);
  }else {
    throw std::invalid_argument( "[evaluation error] Unkown operation: " + val);
  }
  return .0;
}

std::ostream& operator<< (std::ostream& out, ExprAST& ast)
{
  out << ast.get();
  return out;

}
