#ifndef __CAL_AST_H__
#define __CAL_AST_H__
#include <string>
#include <memory>
#include <map>
/// ExprAST - Base class for all expression nodes.
class ExprAST {
public:
  virtual ~ExprAST() {} 
  virtual std::string const & get() = 0;
  friend std::ostream& operator<< (std::ostream& out, ExprAST& );
};

double evalAST(ExprAST *ast, std::map<std::string, double>&);

/// BinaryExprAST - Expression class for a binary operator.
class BinaryExprAST : public ExprAST {
  std::string Op;
  std::unique_ptr<ExprAST> LHS, RHS;
public:
  static std::map<std::string, int> precedence;
  BinaryExprAST(std::string op, std::unique_ptr<ExprAST> LHS,
                std::unique_ptr<ExprAST> RHS)
    : Op(op), LHS(std::move(LHS)), RHS(std::move(RHS)) {}
  BinaryExprAST(BinaryExprAST& arg) :
    Op(arg.Op), LHS(std::move(arg.LHS)), RHS(std::move(arg.RHS)) {}
  ~BinaryExprAST() {}

  virtual std::string const &get() { return Op; }
  std::unique_ptr<ExprAST> getLHS() { return std::move(LHS); }
  std::unique_ptr<ExprAST> getRHS() { return std::move(RHS); }
  void setLHS(std::unique_ptr<ExprAST> &L){ LHS = std::move(L); }
  void setRHS(std::unique_ptr<ExprAST> &R){ RHS = std::move(R); }
  ExprAST *pLHS() {return LHS.get();}
  ExprAST *pRHS() {return RHS.get();}
};

class NumberAST : public ExprAST {
  std::string val;
public:
  NumberAST(std::string arg) : val(arg) {}
  NumberAST(NumberAST& arg) : val(arg.val) {}
  virtual std::string const &get() { return val; }
  ~NumberAST() {}
};

class FunctionAST: public ExprAST {
  const std::string val = "function";
  std::string func;
  std::unique_ptr<ExprAST> expr;
public:
  FunctionAST(std::string &func, std::unique_ptr<ExprAST> expr) {
    this->func = func;
    this->expr = std::move(expr);
  }
  FunctionAST(FunctionAST & arg) : func(arg.func), expr(std::move(arg.expr)) {}
  virtual std::string const &get() { return val; }
  ~FunctionAST() {}
  ExprAST *getExpr(){ return expr.get(); }
  std::string &getFnuc(){ return func; }
};

class AssignmentAST: public ExprAST {
  const std::string val = "assign";
  std::string name;
  std::unique_ptr<ExprAST> expr;
public:
  AssignmentAST(std::string &name, std::unique_ptr<ExprAST> &expr) {
    this->name = name;
    this->expr = std::move(expr);
  }
  AssignmentAST(AssignmentAST& arg) : name(arg.name), expr(std::move(arg.expr)) {}
  virtual std::string const &get() { return val; }
  ~AssignmentAST() {}
  ExprAST *getExpr(){ return expr.get(); }
  std::string &getName(){ return name; }
};

class VariableAST : public ExprAST{
  const std::string val = "variable";
  std::string name;
public:
  VariableAST(std::string &name)   {
    this->name = name;
  }
  VariableAST(VariableAST& arg) : name(arg.name) {}
  virtual std::string const &get() { return val; }
  ~VariableAST() {}
  std::string &getName(){ return name; }
};

static int getPrecedence(std::string op){
    int prec = BinaryExprAST::precedence[op];
    if( prec <= 0) return -1;
    return prec;
}
std::unique_ptr<BinaryExprAST> 
  create_bi_expr(std::string biop, std::unique_ptr<ExprAST> LHS, std::unique_ptr<ExprAST> RHS);

#endif //__CAL_AST_H__
