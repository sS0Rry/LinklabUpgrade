/*
* C Module of LinkLAB.
*
* Su Feng, Nanjing University.
*/

#include <stdio.h>
#include <string.h>
#include "config.h"


//
// Randomization
//

char DECOY_FUNC_NAME( int index )
{
	char buf[] = RAND_STRING_INIT_VALUE;
	int n = sizeof(buf)/sizeof(buf[0]);

	return (index>=0 && index<n)? buf[index] : 0;
}

//
// Global data
//

const char* phase_id = "6";

char BUFVAR[] = MYID;

//
// Code generation
//
const int CODE_TRAN_ARRAY[] = CODE_TRAN_ARRAY_INIT_VALUE;
int CODE = 0xFFFFFFFF;

int transform_code( int code, int mode )
{
	switch ( CODE_TRAN_ARRAY[mode] & 0x00000007 )
	{
	case 0:
		code = ~ code;
		break;
	case 1:
		code = code >> ( CODE_TRAN_ARRAY[mode] & 0x00000003 );
		break;
	case 2:
		code = code & (~ CODE_TRAN_ARRAY[mode]);
		break;
	case 4:
		code = code | (CODE_TRAN_ARRAY[mode] << 8);
		break;
	case 5:
		code = code ^ CODE_TRAN_ARRAY[mode];
		break;
	case 6:
		code = code | (~ CODE_TRAN_ARRAY[mode]);
		break;
	case 7:
		code = code + CODE_TRAN_ARRAY[mode];
		break;
	default:
		code = - code;
		break;
	}

	return code;
}

void generate_code( int cookie )
{
	int i;

	CODE = cookie;
	for( i=0; i<sizeof(CODE_TRAN_ARRAY)/sizeof(CODE_TRAN_ARRAY[0]); i++ )
	{
		CODE = transform_code( CODE, i );
	}
}

//
// Encoding
//
typedef int (*CODER)(char*);

const char FDICT[] = FDICTDAT;

int encode_1( char* str )
{
	int n, i;

	n = strlen(str);
	for(i=0; i<n; i++)
	{
		str[i] = (FDICT[str[i]] ^ CODE) & 0x7F;
		if(str[i]<0x20 || str[i]>0x7E) str[i] = '?';
	}

	return n;
}

int encode_2( char* str )
{
	int n, i;

	n = strlen(str);
	for(i=0; i<n; i++)
	{
		str[i] = (FDICT[str[i]] + CODE) & 0x7F;
		if(str[i]<0x20 || str[i]>0x7E) str[i] = '*';
	}

	return n;
}

CODER encoder[] = { encode_1, encode_2 };

//
// Main Function
//

void do_phase()
{
	generate_code(PHASE6_COOKIE);

	encoder[ENCODER_ID](BUFVAR);

	printf("%s\n", BUFVAR);
}


//
// Interface
//

void (*phase)() = do_phase;
