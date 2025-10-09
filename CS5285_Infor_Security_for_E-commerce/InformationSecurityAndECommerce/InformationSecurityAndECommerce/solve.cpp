#include<bits/stdc++.h>
using namespace std;
map <char,char> m;

int main(void)
{	
	m['A']='d';
	m['B']='h';
	m['C']='p';
	m['D']='u';
	m['E']='w';
	m['F']='e';
	m['G']='b';
	m['H']='r';
	m['I']='y';
	m['J']='l';
	m['K']='k';
	m['L']='g';
	m['M']='j';
	m['N']='x';
	m['O']='f';
	m['P']='t';
	m['Q']='a';
	m['R']='z';
	m['S']='q';
	m['T']='o';
	m['U']='v';
	m['V']='i';
	m['W']='n';
	m['X']='s';
	m['Y']='m';
	m['Z']='c';

	/* qgzafolbvrkjywtcmhxpduenis*/
	char ch = '0';
	while(ch != EOF)
	{
		ch=getchar();
		printf("%c",m[ch]);
	}
	return 0;
}