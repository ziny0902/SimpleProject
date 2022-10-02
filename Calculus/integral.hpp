#ifndef __DOUBLE_INTEGRAL_H__
#define __DOUBLE_INTEGRAL_H__

#include <boost/math/quadrature/gauss_kronrod.hpp>
#include <array>

namespace support{ namespace math{

  using namespace boost::math::quadrature;
  typedef  double(* single_variable_fn)(double) ;
  typedef  double(* two_variable_fn)(double, double) ;
  typedef  double(* triple_variable_fn)(double, double, double) ;

  struct single_integral_t {
    std::array<double, 2> x{};  
    single_variable_fn fn;
    single_integral_t(single_variable_fn _f, std::array<double, 2>_x):fn(_f), x(_x){}; 
    double eval(void){
      double error;
      return gauss_kronrod<double, 15>::integrate
      (
        fn, x[0], x[1], 5, 1e-9, &error
      ); 
    }
  };

  struct double_integral_t {
    std::array<double, 2> x{};  
    std::array<double, 2> y{};  
    two_variable_fn fn{nullptr};

    double_integral_t(two_variable_fn _f, std::array<double, 2>_x, std::array<double, 2>_y) 
      :  x(_x), y(_y), fn(_f){ };

    double eval(void){
      double error;
      auto int_fx =[&](double _y){
        return gauss_kronrod<double, 15>::integrate
        (
          [&] (double _x) { return fn(_x, _y); },
          x[0], x[1], 5, 1e-9, &error
        ); 
      };

      return gauss_kronrod<double, 15>::integrate
      (
        int_fx, y[0], y[1], 5, 1e-9, &error
      ); 
    }
  };

  struct triple_integral_t {
    std::array<double, 2> x{};  
    std::array<double, 2> y{};  
    std::array<double, 2> z{};  
    triple_variable_fn fn{nullptr};

    triple_integral_t( triple_variable_fn _f, 
        std::array<double, 2> _x, 
        std::array<double, 2> _y,
        std::array<double, 2> _z
        ) 
      :  x(_x), y(_y), z(_z), fn(_f){ };

    double eval(void){
      double error;
      auto int_fx =[&](double _y, double _z){
        return gauss_kronrod<double, 15>::integrate
        (
          [&] (double _x) { return fn(_x, _y, _z); },
          x[0], x[1], 5, 1e-9, &error
        ); 
      };
      auto int_fy = [&](double _z) {
        return gauss_kronrod<double, 15>::integrate
        (
          [&] (double _y) { return int_fx(_y, _z); },
          y[0], y[1], 5, 1e-9, &error
        ); 
      };

      return gauss_kronrod<double, 15>::integrate
      (
        int_fy, z[0], z[1], 5, 1e-9, &error
      ); 
    }
  };

}}

#endif
