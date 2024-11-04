/*
* C Module of LinkLAB.
*
* Su Feng, Nanjing University.
*/

#include <stdio.h>
#include "config.h"


//
// Global Data
//

void (*phase)();

const char* phase_id;

const char challenge[] = "suf@nju.edu.cn";


//
// Declarations
//

//
// Main Proc
//
int main( int argc, const char* argv[] )
{
	if( phase )
		(*phase)();
	else
		printf("Welcome to this small lab of linking. To begin lab, please link the relevant object module(s) with the main module.\n");

	return 0;
}
