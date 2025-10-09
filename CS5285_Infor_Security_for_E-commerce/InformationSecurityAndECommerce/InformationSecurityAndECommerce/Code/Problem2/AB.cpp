#include<bits/stdc++.h>
using namespace std;
int a,b,temp,t;
char c,d,f;
int p=0;
int q;
queue<char> m;
int main(void)
{
	printf("Please input the IV code in DEC:\n");
	scanf("%d%c",&t,&f); 
	b=t;
	while(1)
	{
		char str[5];
		printf("input="); 
		scanf("%c%c",&c,&d);
		a=c-'A';
		printf("Before : a=%d b=%d ....... \n",a,b); 
		printf("Code=%c \n Number=%d String=%s \n",
		'A'+(((a^b)+3)%16),(((a^b)+3)%16),itoa((((a^b)+3)%16),str,2));
		++p;
		m.push('A'+(((a^b)+3)%16));
		for(int i=1;i<=p;++i)
		{
			printf("%c ",m.front());
			m.push(m.front());
			m.pop(); 
		}
		printf("\n");
		temp=(((a^b)+3)%16);
		b=temp;
		printf("After: a=%d b=%d ....... \n\n\n\n",a,b);
	}
	return 0;
}
