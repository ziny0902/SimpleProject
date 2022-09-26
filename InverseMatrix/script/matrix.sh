#!/usr/bin/bash
print_usage(){
  echo "Matrix Fomatter"
  echo -e "usage: matrix.sh [option] {file}\n"
  echo "option:"
  echo -e "\t-py : python matrix format"
  echo -e "\t-jl : julia matrix format"
  echo -e "\nfile format:"
  echo -e "{exp}, ..., {exp}, {exp}"
  echo "{exp}, ..., {exp}, {exp}"
  echo -e "\nexp: bc expression"
  echo -e "\nex)"
  echo "pi=3.14"
  echo "1/sqrt(10), s(pi*0.5), 3^2"
  echo "(4+3)*e(3), 5.0/2 ,(6^3)*10"
  echo -e "\nsee also: bc"
  exit 1
}

read_from_file() {
	echo $( cat $1 | 
  	sed -E 's/,/\n/g; s/$/\n print ";"/'| 
  	bc -lq | 
  	tr '\n' ',' 
	)
}

opt=""

# read data from stdin
if  [ $# -eq 0 ] || ([ $# -eq 1 ] && [[ $1 =~ -[a-zA-Z]+ ]])
then
	result=$( tee | 
  sed -E 's/,/\n/g; s/$/\n print ";"/'| 
  bc -lq | 
  tr '\n' ','
	)
	if [ $# -eq 1 ]
	then
		opt=$1
	fi
elif [ $# -eq 1 ] && [[ ! $1 =~ -[a-zA-Z]+ ]]
then
  result=$(read_from_file $1)
elif [ $# -eq 2 ]
then
  result=$(read_from_file $2)
  opt=$1
else
	print_usage
fi

# python fomatter
if [[ $opt == "-py" ]]
then
  echo $result |  sed -E 's/,;/;/g; s/;/\n/g' | awk -F ',' 'BEGIN{printf("[")} {
      if( NF > 1)
        printf("[")
      for (i = 1; i <= NF; i++) {
        if ( i != 1 )
          printf(",%10s", $i)
        else
          printf("%10s", $i)
      }
      if( NF > 1)
        printf("],\n")
      } END{printf("]\n")}' | sed -n ':x; /],$/{N;bx}; s/,\n]/]/; p'
# julia fomatter
elif [[ $opt == "-jl" ]]
then
  echo $result |  sed -E 's/,;/;/g; s/;/\n/g' | awk -F ',' 'BEGIN{printf("[\n")} {
      for (i = 1; i <= NF; i++) {
          printf("%10s", $i)
      }
      if( NF > 1)
        printf("\n")
      } END{printf("]\n")}'

# LaTex Math fomatter
elif [[ $opt == "-tex" ]]
then
  echo $result |  sed -E 's/,;/;/g; s/;/\n/g' | awk -F ',' 'BEGIN{printf("\\[\\begin{pmatrix*}[r]\n")} {
      for (i = 1; i <= NF; i++) {
      	if( i != 1 )
          printf(" &%10s", $i)
        else
          printf("%10s", $i)
      }
      if( NF > 1)
        printf("\\\\\n")
      } END{printf("\\end{pmatrix*}\\]\n")}'
      echo -e "\nWarning: need the mathtools package for the column alignment"

# csv fomatter
elif [[ $opt == "-csv" ]]
then
  echo $result |  sed -E 's/,;/;/g; s/;/\n/g' | awk -F ',' '{
      for (i = 1; i <= NF; i++) {
        if( i != 1)
          printf(", %10s", $i)
        else
          printf("%10s", $i)
      }
      printf("\n")
    }'

# stdout fomatter
else
  echo $result |  sed -E 's/,;/;/g; s/;/\n/g' | awk -F ',' '{
      for (i = 1; i <= NF; i++) {
        printf("%10s", $i)
      }
      printf("\n")
    }'
fi
exit 0
