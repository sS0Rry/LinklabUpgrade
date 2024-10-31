/*
* C Module of LinkLAB.
*
* Su Feng, Nanjing University.
*/

#include <stdio.h>
#include <string.h>
#include "config.h"

//
// Global Data
//

const char* phase_id = "2";

#define NOP_INST_LIST_64 "nop\n\tnop\n\tnop\n\tnop\n\tnop\n\tnop\n\tnop\n\tnop\n\tnop\n\tnop\n\tnop\n\tnop\n\tnop\n\tnop\n\tnop\n\tnop\n\tnop\n\tnop\n\tnop\n\tnop\n\tnop\n\tnop\n\tnop\n\tnop\n\tnop\n\tnop\n\tnop\n\tnop\n\tnop\n\tnop\n\tnop\n\tnop\n\tnop\n\tnop\n\tnop\n\tnop\n\tnop\n\tnop\n\tnop\n\tnop\n\tnop\n\tnop\n\tnop\n\tnop\n\tnop\n\tnop\n\tnop\n\tnop\n\tnop\n\tnop\n\tnop\n\tnop\n\tnop\n\tnop\n\tnop\n\tnop\n\tnop\n\tnop\n\tnop\n\tnop\n\tnop\n\tnop\n\tnop\n\tnop\n\t"

/*
* To add more variable and function definitions to confuse students
*/

char DECOY_FUNC_NAME( int index )
{
	char buf[] = PHASE2_COOKIE;
	int n = strlen(buf);

	return (index>=0 && index<n)? buf[index] : 0;
} 

static void OUTPUT_FUNC_NAME( const char *key, const char *output )
{
	if( strcmp(key,PHASE2_KEYSTR) != 0 ) return;
		
	printf("%s\n", output);
}


//
// Main Function
//

void do_phase()
{
#ifdef _SOLUTION_
	char key[] = PHASE2_KEYSTR;
	char id[] = MYID;
	OUTPUT_FUNC_NAME( key, id );
#else
	asm( NOP_INST_LIST_64 );
#endif
}


//
// Interface
//

void (*phase)() = do_phase;
