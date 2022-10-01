#include <iostream>
#include "derivative.hpp"

template<typename A, size_t d>
std::ostream& operator << (std::ostream &os, std::array<A, d> arr) {
  os << "[ ";
  for( int i=0; i < d; i++ ) {
    os << arr[i] << " ";
  }
  os << "]"; 
  return os;
}

std::array<double, 3> cross(std::array<double, 3> a, std::array<double, 3>b)
{
  std::array<double, 3> ret;
  ret[0] = a[1]*b[2] - a[2]*b[1];
  ret[1] = -1*a[0]*b[2] + a[2]*b[0];
  ret[2] = a[0]*b[1] - a[1]*b[0];
  return ret;
}

std::array<double, 2> unit_vector(std::array<double, 2>& v)
{
  double len = sqrt(v[0]*v[0] + v[1]*v[1] );
  std::array<double, 2> ret;
  ret[0] = v[0]/len;
  ret[1] = v[1]/len;
  return ret;
}

std::array<double, 3> unit_vector(std::array<double, 3>& v)
{
  double len = sqrt(v[0]*v[0] + v[1]*v[1] + v[2]*v[2]);
  std::array<double, 3> ret;
  ret[0] = v[0]/len;
  ret[1] = v[1]/len;
  ret[2] = v[2]/len;
  return ret;
}

void boost_partial_derivative(void)
{
  std::cout << "<<test derivative funtion>>" << std::endl;
  struct {
    constexpr double operator()(std::array<double, 3>v){  
      return v[0]*sin(v[1])/pow(v[2], 2); 
    }
  } fn;
  std::array<double, 3> in = {1, 2, 3};
  support::math::partial_derivative<decltype(fn), 3>df(fn);
  std::array<double, 3> ret = df.gradiant(in);
  // std::cout << ret[0] << " " << ret[1] << " " << ret[2] << std::endl;
  // std::cout << df.diff(in, 1) << std::endl;
  // std::cout << df.second_order_diff(in, 1) << std::endl;

  // 2 variable scalar function.
  struct {
    constexpr double operator()(std::array<double, 2>v){  
      return pow(v[0], 2)*v[1];
    }
  } fn_d;
  std::array<double, 2> in_2 = {3, 2};
  support::math::partial_derivative<decltype(fn_d), 2>df_2(fn_d);
  std::array<double, 2> ret_2 = df_2.gradiant(in_2);
  // std::cout << ret_2[0] << " " << ret_2[1] << std::endl;
  std::array<double, 2> v {2, 1};
  // std::cout << df_2.directional_derivative(in_2, v) << std::endl;

  // 3 variable scalar function
  struct {
    constexpr double operator()(std::array<double, 3>v){  
      return v[0]*v[1]*pow(M_E, v[0]*v[0] + v[2]*v[2] - 5); 
    }
  } fn_3;
  in = {1, 3, -2};
  support::math::partial_derivative<decltype(fn_3), 3>df_3(fn_3);
  ret = df_3.gradiant(in);
  std::cout << "x^2*pow(M_E, x^2 + z^2 - 5) (x=1, y=3, z=2) gradiant:" << std::endl;
  std::cout << ret << std::endl;
  std::array<double, 3> v_3 {3, -1, 4};
  std::cout << "x^2*pow(M_E, x^2 + z^2 - 5) (x=1, y=3, z=2) direction vector[3, -1, 4] directional derivative:" << std::endl;
  std::cout << df_3.directional_derivative(in, v_3) << std::endl;

  // parametric function.
  struct {
    std::array<double(*)(double), 3> fn_arr {
      [](double t){return cos(t);},
      [](double t){return sin(t);},
      [](double t){return t;}
    };
    int var {1};
    double operator()(std::array<double, 1>&t){  
      return fn_arr[var](t[0]); 
    }
    double operator()(std::array<double, 1>&t, int var){  
      return fn_arr[var](t[0]); 
    }
  } para_fn;
  support::math::partial_derivative<decltype(para_fn), 1>df_para(para_fn);
  std::array<double, 1>para_in{M_PI/2};
  std::cout<< "parametric function x(t)=cos(t), y(t)=sin(t), t=t (t=pi/2) derivative:" << std::endl;
  for(int i = 0; i < 3; i++){
    para_fn.var=i;
    std::cout << df_para.diff(para_in, 0) << ", ";
  }
  std::cout << std::endl;
  para_fn.var=1;
  std::cout << "y'': "<<df_para.second_order_diff(para_in, 0) << std::endl;

  // unit normal, tangent, binormal
  struct {
    std::array<double(*)(std::array<double, 2>&), 3> fn_arr {
      [](std::array<double, 2>&t){return t[0]+1;},
      [](std::array<double, 2>&t){return t[1];},
      [](std::array<double, 2>&t){return t[1]*t[1] - t[0]*t[0] +1;}
    };
    int var {0};
    double operator()(std::array<double, 2>&t){  
      return fn_arr[var](t); 
    }
    double operator()(std::array<double, 2>&t, int var){  
      return fn_arr[var](t); 
    }
  } surface_fn;
  support::math::partial_derivative<decltype(surface_fn), 2>df_surface(surface_fn);
   v = {1, -2};
  std::array<double, 3>ru{};
  std::array<double, 3>rv{};
  for(int i = 0; i < 3; i++){
    surface_fn.var=i;
    ru[i] = df_surface.diff(v, 0);
    rv[i] = df_surface.diff(v, 1);
  }
  std::cout << "surface: f(t,s)=[t+1, s, t^2 - s^2 +1] (t = 1, s = -2)" << std::endl;
  std::cout << "dt: " << ru << std::endl;
  std::cout << "ds: " << rv << std::endl;
  std::array<double, 3>normal = cross(ru, rv);
  std::cout << "normal(dt X ds): " << normal << std::endl;
  std::cout << "unit normal: " << unit_vector(normal) << std::endl;
}

int main()
{
  boost_partial_derivative();
  return 0;
}
