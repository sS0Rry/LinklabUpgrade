/*
* C Module of LinkLAB.
*
* Su Feng, Nanjing University.
*/

#include <stdio.h>
#include <string.h>
#include "config.h"


//
// Global data
//

const char* phase_id = "3";

char PHASE3_CODEBOOK[256];


//
// Declarations
//

//
// Main Function
//

void do_phase()
{
	char cookie[] = PHASE3_COOKIE;
	int i;

	// Call external function
	//i = PHASE3_FUNCNAME( cookie );

	// Coding to ID
	for( i=0; i<sizeof(cookie)-1; i++ )
		printf( "%c", PHASE3_CODEBOOK[(unsigned char)(cookie[i])] );
	printf( "\n" );
}


//
// Interface
//

void (*phase)() = do_phase;
