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
  ret[1] = a[2]*b[0] - a[0]*b[2];
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

  // 2 variable scalar function.
  struct {
    constexpr double operator()(std::array<double, 2>v){  
      return pow(v[0], 2)*v[1];
    }
  } fn_d;
  std::array<double, 2> in_2 = {3, 2};
  support::math::partial_derivative<decltype(fn_d), 2>df_2(fn_d);
  std::array<double, 2> ret_2 = df_2.gradiant(in_2);
  std::array<double, 2> v {2, 1};

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
  std::array<double, 3> dir{3, -1, 4};
  std::cout << "x^2*pow(M_E, x^2 + z^2 - 5) (x=1, y=3, z=2) direction vector[3, -1, 4] directional derivative:" << std::endl;
  std::cout << df_3.directional_derivative(in, dir) << std::endl;

  {
  // parametric function.
  // d: 3 dimension, N: 1 variable
  support::math::parametric_fn<double(*)(std::array<double, 1>&), 3, 1>
    para_fn({
        [](std::array<double,1>& t){return cos(t[0]);}, // x 
        [](std::array<double,1>& t){return sin(t[0]);}, // y
        [](std::array<double,1>& t){return t[0];} // z
        });
  support::math::parametric_derivative<decltype(para_fn), 1>df_para(para_fn);
  std::array<double, 1>para_in{M_PI/2};
  std::cout<< "parametric function x(t)=cos(t), y(t)=sin(t), t=t (t=pi/2) derivative:" << std::endl;
  std::array<double, 3> tangent;
  std::array<double, 3> normal;
  for(int i = 0; i < 3; i++){
    df_para.select_variable(i);
    tangent[i] =  df_para.diff(para_in, 0);
    normal[i] = df_para.second_order_diff(para_in, 0);
  }
  tangent = unit_vector(tangent);
  normal = unit_vector(normal);
  std::array<double, 3> binormal = cross(tangent, normal);
  std::cout << "tangent: " << tangent << std::endl;
  std::cout << "normal: " << normal << std::endl;
  std::cout << "binormal: " << binormal << std::endl;
  }

  {
  // d: 3 dimension, N: 2 variable
  support::math::parametric_fn<double(*)(std::array<double, 2>&), 3, 2>
    surface_fn({
        [](std::array<double, 2>&t){return t[0]+1;}, // x
        [](std::array<double, 2>&t){return t[1];}, // y
        [](std::array<double, 2>&t){return t[1]*t[1] - t[0]*t[0] +1;} // z
        });
  support::math::parametric_derivative<decltype(surface_fn), 2>df_surface(surface_fn);

   v = {1, -2};
  std::array<double, 3>ru{};
  std::array<double, 3>rv{};
  for(int i = 0; i < 3; i++){
    // surface_fn.var=i;
    df_surface.select_variable(i);
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
}

// #include <boost/math/quadrature/gauss_kronrod.hpp>
#include "integral.hpp"
void boost_integrate(void)
{
  std::cout << "<<test Integral>>" << std::endl;
  using namespace boost::math::quadrature;
  auto f1 = [](double t) { return std::exp(-t*t / 2); };
  double error;
  double Q;

  // basic integral
  Q = gauss_kronrod<double, 15>::integrate(f1, 0, std::numeric_limits<double>::infinity(), 0, 0, &error);
  std::cout << "0 - INF: " << Q << std::endl;
  for (double x=0; x <= 4.1; x=x+0.1)
  {
    Q = gauss_kronrod<double, 15>::integrate(f1, 0, x, 5, 1e-9, &error);
  }
  // double integral without wrapper
  {
    std::array<double, 2> x{0, 2};
    std::array<double, 2> y{-M_PI, M_PI};
    double total;
    total = 
    gauss_kronrod<double, 15>::integrate(
        [&] (double _y){ 
            return gauss_kronrod<double, 15>::integrate
            (
              [&] (double _x) { return _x + std::sin(_y)+1 ; },
              x[0], x[1], 5, 1e-9, &error
            ); 
          }, 
          y[0], y[1], 5, 1e-9, &error);
    std::cout << "integral(x + sin(y) + 1) | x[0 2], y[-pi pi]: " << total << std::endl;
  }
  //
  // using wrapper class
  //
  // basic single Integral
  std::cout << "--wrapper test" << std::endl;
  {
    // e^(-t^2/2)
    auto f = [](double t) { return std::exp(-t*t / 2); };
    support::math::single_integral_t df
      { f, {0, std::numeric_limits<double>::infinity()} };
    std::cout << "Integral( -x^2 / 2 ) | x[0  INF]: " << df.eval() << std::endl;
  }
  // double integral
  {
    // x + sin(y) + 1
    auto f = [](double x, double y){ return x + std::sin(y) + 1; };
    // ( function, x range, y range )
    support::math::double_integral_t df{f, {0,2}, {-M_PI, M_PI}};
    std::cout << "integral(x + sin(y) + 1) | x[0 2], y[-pi pi]: " << df.eval() << std::endl;
  }
  // triple integral
  {
    // f(x,y,z) = 8xyz
    auto f = [](double x, double y, double z){ return 8*x*y*z; };
    support::math::triple_integral_t df (f, {0, 1}, {2, 3}, {1, 2});
    std::cout << "integral( 8xyz ) | z[0 1] x[2 3] y[1 2]: " << df.eval() << std::endl;
  }
  {
    // f(x,y,z) = x+ yz^2 
    auto f = [](double x, double y, double z){ return x + z*z*y; };
    support::math::triple_integral_t df (f, {-1, 5}, {2, 4}, {0, 1});
    std::cout << "integral( x + yz^2) | x[-1 5] y[0 1] z[2 4]: " << df.eval() << std::endl;
  }
  {
    // f(x,y,z) = x^2yz 
    auto f = [](double x, double y, double z){ return x*x*y*z; };
    support::math::triple_integral_t df (f, {-2, 1}, {0, 3}, {1, 5});
    std::cout << "integral( x^2yz ) | x[0 3] y[-2 1] z[1 5]: " << df.eval() << std::endl;
  }
}

int main()
{
  boost_partial_derivative();
  boost_integrate();
  return 0;
}
