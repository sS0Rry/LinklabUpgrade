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

const char* phase_id = "1";

static char BUFVAR[] = BUFDAT;


//
// Main Function
//

void do_phase()
{
#ifdef _SOLUTION_
	strcpy(BUFVAR+BUFPOS, MYID);
#endif
	printf("%s\n", BUFVAR+BUFPOS);
}


//
// Interface
//

void (*phase)() = do_phase;
