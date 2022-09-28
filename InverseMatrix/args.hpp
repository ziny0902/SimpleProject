#ifndef __ARGS_H__
#define __ARGS_H__
#include <boost/config/warning_disable.hpp>
#include <boost/spirit/include/qi.hpp>
#include <boost/phoenix/core.hpp>
#include <boost/phoenix/operator.hpp>
#include <boost/fusion/include/adapt_struct.hpp>

namespace Args
{
    enum class arg_type { sarg, larg, name};

    struct name_value_t {
        std::string name;
        std::string value;
    };
    typedef boost::variant<std::string, name_value_t> option_t;

    struct args_t {
        std::vector<option_t> options;
        std::string file;
    };
}

BOOST_FUSION_ADAPT_STRUCT(
    Args::args_t,
    (std::vector<Args::option_t>, options)
    (std::string, file)
)
namespace Args
{
    namespace qi = boost::spirit::qi;
    namespace ascii = boost::spirit::ascii;
    using qi::_1;
    using qi::_val;
    using ascii::char_;
    using qi::lexeme;
    template <typename Iterator>
    struct parse_args : qi::grammar<Iterator, args_t(), ascii::space_type>
    {
        parse_args() : parse_args::base_type(start)
        {
            loption %= "--" 
                >> +(char_-'='-' ') >> -("="  >> +(char_-' '));
            soption %= '-' >>  +(char_-'-'-' ');
            quoted_string %= lexeme['"' >> +(char_ - '"') >> '"'];
            string =  (char_-'"'-'-')[_val=_1] >> +(char_-' ')[_val += _1];
            start %= *(soption | loption) >> 
                 -(quoted_string | string);
        }
        qi::rule<Iterator, option_t()> loption;
        qi::rule<Iterator, option_t()> soption;
        qi::rule<Iterator, std::string()> string;
        qi::rule<Iterator, std::string(), ascii::space_type> quoted_string;
        qi::rule<Iterator, args_t(), ascii::space_type> start;
    };
}
#endif
