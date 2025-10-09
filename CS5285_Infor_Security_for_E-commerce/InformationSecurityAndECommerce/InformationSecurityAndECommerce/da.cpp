#include<bits/stdc++.h>
using namespace std;
int main(void)
{
	int i=0;
	char q,t;
	char ch = 'A';
	for(i=0;i<26;++i)
	{
		t=getchar();
		q=getchar();
		printf("	m['%c']='%c';\n",ch+i,ch+i);
	}
	return 0;
}
