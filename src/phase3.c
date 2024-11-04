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

const char* phase_id = "4";


//
// Main Function
//

void do_phase()
{
#ifdef _SOLUTION_
	printf("%s\n", MYID);
#else
	const char cookie[] = PHASE4_COOKIE;
	char c;
	int i;

	for(i = 0; i < sizeof(cookie)-1; i++ )
	{
		c = cookie[i];
		switch (c)
		{
		case 'A': DO_CASE_A
		case 'B': DO_CASE_B
		case 'C': DO_CASE_C
		case 'D': DO_CASE_D
		case 'E': DO_CASE_E
		case 'F': DO_CASE_F
		case 'G': DO_CASE_G
		case 'H': DO_CASE_H
		case 'I': DO_CASE_I
		case 'J': DO_CASE_J
		case 'K': DO_CASE_K
		case 'L': DO_CASE_L
		case 'M': DO_CASE_M
		case 'N': DO_CASE_N
		case 'O': DO_CASE_O
		case 'P': DO_CASE_P
		case 'Q': DO_CASE_Q
		case 'R': DO_CASE_R
		case 'S': DO_CASE_S
		case 'T': DO_CASE_T
		case 'U': DO_CASE_U
		case 'V': DO_CASE_V
		case 'W': DO_CASE_W
		case 'X': DO_CASE_X
		case 'Y': DO_CASE_Y
		case 'Z': DO_CASE_Z
		}
		printf("%c", c);
	}

	printf("\n");
#endif
}


//
// Interface
//

void (*phase)() = do_phase;

