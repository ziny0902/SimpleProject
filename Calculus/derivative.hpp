#ifndef __DERIVATIVE_HPP__
#define __DERIVATIVE_HPP__

#include <boost/math/differentiation/finite_difference.hpp>
#include <cmath>
#include <array>

namespace support{namespace math{
  template <class F, size_t d>
  class partial_derivative{
    protected:
      F fn;
    public:
      partial_derivative(F& f ) : fn(f){};
      double diff(std::array<double, d>& in, size_t t){
        auto f = [&](double x){
          double orig = in[t];
          in[t] = x;
          double ret = fn(in);
          in[t] = orig;
          return ret;
        };
        return boost::math::differentiation::finite_difference_derivative(f, in[t]);
      };
      double second_order_diff(std::array<double, d>& in, size_t t)
      {
        auto f = [&](double x){
          double old = in[t];
          in[t] = x;
          double ret = this->diff(in, t);
          in[t] = old;
          return ret;
        };
        return boost::math::differentiation::finite_difference_derivative(f, in[t]); 
      }
      std::array<double, d> gradiant(std::array<double, d>& in){
        int i;
        std::array<double, d> ret;
        for (i = 0; i < d; i++){
          ret[i] = diff(in, i);
        }
        return ret;
      };
      double directional_derivative(std::array<double, d>&in, std::array<double, d>& v)
      {
        int i;
        double len {0};
        for(i = 0; i < d; i++){
          len += v[i]*v[i];
        }
        len = std::sqrt(len);
        std::array<double, d> u;
        for(i = 0; i < d; i++){
          u[i] = v[i]/len;
        }
        std::array<double, d> g = gradiant(in);
        double dret{0};
        for(i = 0; i < d; i++){
          dret += u[i] * g[i];
        }
        return dret;
      }
  };

  // d: dimension, N: num of variable
  template <typename F, size_t d, size_t N>
  struct parametric_fn{
    std::array<F, d> fn_arr{}; 
    int var{0};
    parametric_fn(std::array<F, d> f_arr) : fn_arr(f_arr){};
    virtual double operator()(std::array<double, N>&t){
      return fn_arr[var](t);
    };
  };

  template <class F, size_t d>
  class parametric_derivative : public partial_derivative< F,  d>{
    public:
      parametric_derivative(F & _fn) : partial_derivative<F, d>(_fn){};
      void select_variable(int var){
        this->fn.var = var;
      }
  };

}
}

#endif

