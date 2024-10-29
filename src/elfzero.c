/*
* ELF file reading & writing utility for NJU:ICS course and LinkLab
* 
* Su Feng, Nanjing University
*/

#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <ctype.h>


typedef unsigned int	Elf32_Addr;		//4 Unsigned program address
typedef unsigned short	Elf32_Half;		//2 Unsigned medium integer
typedef unsigned int	Elf32_Off;		//4 Unsigned file offset
typedef int				Elf32_Sword;	//4 Signed large integer
typedef unsigned int	Elf32_Word;		//4 Unsigned large integer

#define EI_NIDENT 16
typedef struct {
	unsigned char	e_ident[EI_NIDENT];
	Elf32_Half 		e_type;
	Elf32_Half 		e_machine;
	Elf32_Word 		e_version;
	Elf32_Addr 		e_entry;
	Elf32_Off  		e_phoff;
	Elf32_Off  		e_shoff;
	Elf32_Word 		e_flags;
	Elf32_Half 		e_ehsize;
	Elf32_Half 		e_phentsize;
	Elf32_Half 		e_phnum;
	Elf32_Half 		e_shentsize;
	Elf32_Half 		e_shnum;
	Elf32_Half 		e_shstrndx;
} Elf32Ehdr;

typedef struct {
	Elf32_Word	sh_name;
	Elf32_Word	sh_type;
	Elf32_Word	sh_flags;
	Elf32_Addr	sh_addr;
	Elf32_Off	sh_offset;
	Elf32_Word	sh_size;
	Elf32_Word	sh_link;
	Elf32_Word	sh_info;
	Elf32_Word	sh_addralign;
	Elf32_Word	sh_entsize;
} Elf32_Shdr;

#define SHT_SYMTAB	2
#define SHT_STRTAB	3
#define SHT_RELA	4
#define SHT_REL		9

typedef struct {
	Elf32_Word		st_name;
	Elf32_Addr		st_value;
	Elf32_Word		st_size;
	unsigned char	st_info;
	unsigned char	st_other;
	Elf32_Half		st_shndx;
} Elf32_Sym;

#define ELF32_ST_BIND(i)	((i) >> 4)
#define ELF32_ST_TYPE(i)	((i) & 0xf)
#define ELF32_ST_INFO(b,t)	(((b) << 4) + ((t) & 0xf))

#define ELF32_STB_LOCAL		0
#define ELF32_STB_GLOBAL	1
#define ELF32_STB_WEAK		2
#define ELF32_STB_LOOS		10
#define ELF32_STB_HIOS		12
#define ELF32_STB_LOPROC	13
#define ELF32_STB_HIPROC	15

#define ELF32_STT_NOTYPE	0
#define ELF32_STT_OBJECT	1
#define ELF32_STT_FUNC		2
#define ELF32_STT_SECTION	3
#define ELF32_STT_FILE		4
#define ELF32_STT_COMMON	5
#define ELF32_STT_TLS		6
#define ELF32_STT_LOOS		10
#define ELF32_STT_HIOS		12
#define ELF32_STT_LOPROC	13
#define ELF32_STT_HIPROC	15

typedef struct{
	Elf32_Addr	r_offset;
	Elf32_Word	r_info;
} Elf32_Rel;

typedef struct{
	Elf32_Addr	r_offset;
	Elf32_Word	r_info;
	Elf32_Sword	r_addend;
} Elf32_Rela;

#define ELF32_R_SYM(i)		((i) >> 8)
#define ELF32_R_TYPE(i)		((unsigned char)(i))
#define ELF32_R_INFO(s,t)	(((s) << 8) + (unsigned char)(t))

typedef unsigned int BOOL;
#define TRUE	1
#define FALSE	0


Elf32_Shdr* load_section_header_table( FILE* fp, const Elf32Ehdr* hdr )
{
	char* buf = 0;
	int count = 0;
	int fpos = ftell(fp);
	
	count = hdr->e_shentsize * hdr->e_shnum;
	buf = calloc(count+1, sizeof(char));
	if(! buf) {
		printf("ERROR - Unable to allocate memory for loading the whole Section Header Table.\n");
		return 0;
	}

	////
	fseek(fp, hdr->e_shoff, SEEK_SET);

	if(fread(buf,sizeof(char),count,fp) < count) {
		printf("ERROR - Unable to read the whole Section Header Table.\n");
		free(buf);  buf = 0;
	}
	buf[count] = 0;
	
	fseek(fp, fpos, SEEK_SET);
	return (Elf32_Shdr*) buf;
}


void* load_section_by_type( FILE* fp, const Elf32Ehdr* hdr, int type, int num, const int* skip, int nskip )
{
	char* buf = 0;
	int fpos = ftell(fp);
	int count = 0;
	Elf32_Shdr shdr;
	BOOL skipping;
	int s, i;
	
	for(s=0; s<hdr->e_shnum; s++)
	{
		// skip specified entries
		if(skip && nskip>0) {
			skipping = FALSE;
			for(i=0; i<nskip; i++)
				if(skip[i] == s) skipping = TRUE;
			if(skipping) continue;
		}
		
		if(fseek(fp,hdr->e_shoff+s*hdr->e_shentsize,SEEK_SET) != 0) {
			printf("ERROR - Unable to locate the %u-th entry of Section Header Table.\n", s+1);
			break;
		}
		if(fread(&shdr,sizeof(shdr),1,fp) < 1) {
			printf("ERROR - Unable to read the %u-th entry of Section Header Table.\n", s+1);
			break;
		}
		
		if(shdr.sh_type != type)
			continue;

		// target at the num-th section of the same specified type
		count ++;
		if(num>0 && count!=num)
			continue;
			
		// read in the target section
		if(fseek(fp,shdr.sh_offset,SEEK_SET) != 0) {
			printf("ERROR - Unable to locate the %u-th section.\n", s+1);
			break;
		}
		
		buf = calloc(shdr.sh_size+1, sizeof(char));
		if( ! buf ) {
			printf("ERROR - Unable to allocate memory for loading the %u-th section.\n", s+1);
			break;
		}
		
		if(fread(buf,sizeof(char),shdr.sh_size,fp) < shdr.sh_size) {
			printf("ERROR - Unable to read the %u-th section.\n", s+1);
			free(buf); buf = 0;
			break;
		}
		
		buf[shdr.sh_size] = 0;
		break;
	}
	
	fseek(fp, fpos, SEEK_SET);
	return buf;
}


void* load_section_by_header( FILE* fp, const Elf32_Shdr* shdr )
{
	char* buf = 0;
	int fpos = ftell(fp);

	//
	buf = calloc(shdr->sh_size+1, sizeof(char));
	if( ! buf ) {
		printf("ERROR - Unable to allocate memory for loading the specified section.\n");
		return buf;
	}
	
	// read in the target section
	if(fseek(fp,shdr->sh_offset,SEEK_SET) != 0) {
		printf("ERROR - Unable to locate the specified section.\n");
		
		free(buf); buf = 0;
		goto quit;
	}
		
	if(fread(buf,sizeof(char),shdr->sh_size,fp) < shdr->sh_size) {
		printf("ERROR - Unable to read the specified section.\n");
		
		free(buf); buf = 0;
		goto quit;
	}
		
	buf[shdr->sh_size] = 0;

quit:	
	fseek(fp, fpos, SEEK_SET);
	return buf;
}


char* query_symbol_name( Elf32_Sym* symitem, char* strtab, Elf32_Shdr* sechdrtab, char* secnamtab )
{
	switch(ELF32_ST_TYPE(symitem->st_info))
	{
	case ELF32_STT_SECTION:
		return secnamtab + sechdrtab[symitem->st_shndx].sh_name;
		
	default:
		return strtab + symitem->st_name;
	}
}


#define RUN_MODE_DUMP	0
#define RUN_MODE_QUERY	1
#define RUN_MODE_ZERO	2
#define ELF32_STT_SECTION	3


int main( int argc, const char* argv[] )
{
	int run_mode = RUN_MODE_DUMP;
	char obj_type = 'a';
	int obj_index_first = -1, obj_index_last = -1;
	int obj_offset_start = -1, obj_offset_end = -1;
	const char* obj_name = 0;
	unsigned char fill_value[4] = {0,0,0,0};
	int fill_size = 0;
	char fillbuf[4] = {0,0,0,0};
	const char* file_path = 0;
	FILE* fp;
	Elf32Ehdr hdr;
	Elf32_Shdr shdr, *shdrp;
	Elf32_Sym sym, *symp;
	Elf32_Rel rel, *relp;
	Elf32_Shdr* sechdrtab = 0;
	size_t sechdrtab_length = 0;
	char* secnamtab = 0;
	size_t secnamtab_size = 0;
	char ch, *buf, *strp;
	const char *cptr;
	size_t buf_size;
	int data_offset, data_size;
	int s, n, i, index, count, offset;

	switch(argc)
	{
	case 5:
		obj_offset_start = atoi(argv[3]);
		
		cptr = strchr(argv[3],':');
		if(cptr)
			obj_offset_end = atoi(cptr+1);

	case 4:
		if(isdigit(argv[2][0]))
		{
			obj_index_first = obj_index_last = atoi(argv[2]);
			
			cptr = strchr(argv[2],':');
			if(cptr)
				obj_index_last = atoi(cptr+1);
				
			obj_name = 0;
		}
		else
		{
			obj_name = argv[2];
			obj_index_first = obj_index_last = -1;
		}

	case 3:
		obj_type = argv[1][0];
		
		run_mode = RUN_MODE_DUMP;
		
		switch(argv[1][1])
		{
		case 'z':
			run_mode = RUN_MODE_ZERO;
			cptr = & argv[1][2];
			
			memset(fill_value, 0, sizeof(fill_value));
			fill_size = 0;
			
			for(i=0; i<4; i++)
			{
				if(cptr[0]>=0x30 && cptr[0]<=0x66 && cptr[1]>=0x30 && cptr[1]<=0x66)
				{
					fillbuf[0] = cptr[0];  fillbuf[1] = cptr[1];
					if(sscanf(fillbuf,"%x",&n) == 1)
					{
						fill_value[fill_size] = n;  fill_size ++;
						cptr += 2;
						continue;
					}
				}
				break;
			}
			break;

		case 'q':
			run_mode = RUN_MODE_QUERY;
			break;
		}
		break;
		
	case 2:
		obj_type = 'a';
		break;
		
	default:
		printf("ERROR - Please input the right number of command line arguments.\n");
		return 0;
	}
		
	file_path = argv[argc-1];

	// ELF Header
	fp = fopen(file_path, "r+b");
	if(!fp) {
		printf("ERROR - Unable to open file '%s'.\n", file_path);
		return 0;
	}
	
	if(fread(&hdr,sizeof(hdr),1,fp) < 1) {
		printf("ERROR - Unable to read file header.\n");
		goto quit;
	}

	// Section Header Table
	sechdrtab = load_section_header_table(fp, &hdr);
	if(! sechdrtab)  {
		printf("ERROR - Unable to allocate memory for section header table.\n");
		goto quit;
	}
	sechdrtab_length = hdr.e_shnum;

	// Section Name Table
	if(fseek(fp,hdr.e_shoff+hdr.e_shstrndx*hdr.e_shentsize,SEEK_SET) != 0) {
		printf("ERROR - Unable to locate section header entry of section name table.\n");
		goto quit;
	}
	if(fread(&shdr,sizeof(shdr),1,fp) < 1) {
		printf("ERROR - Unable to read the section header entry of section name table.\n");
		goto quit;
	}
	secnamtab_size = shdr.sh_size+1;
	secnamtab = calloc(secnamtab_size, sizeof(char));
	if(! secnamtab) {
		printf("ERROR - Unable to allocate memory for section name table.\n");
		goto quit;
	}
	
	if(fseek(fp,shdr.sh_offset,SEEK_SET) != 0) {
		printf("ERROR - Unable to locate the section name table section.\n");
		goto quit;
	}
	if(fread(secnamtab,sizeof(char),shdr.sh_size,fp) < shdr.sh_size) {
		printf("ERROR - Unable to read the section name table section.\n");
		goto quit;
	}
	secnamtab[secnamtab_size-1] = '\0';
	
	////
	switch(obj_type)
	{
	case 'r': // Relocation Section
		symp = (Elf32_Sym*) load_section_by_type(fp, &hdr, SHT_SYMTAB, 0, 0, 0);
		if(!symp) {
			printf("ERROR - Unable to load symbol table.\n");
			break;
		}
		
		i = hdr.e_shstrndx;
		strp = load_section_by_type(fp, &hdr, SHT_STRTAB, 0, &i, 1);
		if(!strp) {
			printf("ERROR - Unable to load string table for symbol names.\n");
			free(symp); symp = 0;
			break;
		}
		
		index = 0;
		for(s=0; s<hdr.e_shnum; s++)
		{
			if(fseek(fp,hdr.e_shoff+s*hdr.e_shentsize,SEEK_SET) != 0) {
				printf("ERROR - Unable to locate the %u-th entry of Section Header Table.\n", s);
				break;
			}
			if(fread(&shdr,sizeof(shdr),1,fp) < 1) {
				printf("ERROR - Unable to read the %u-th entry of Section Header Table.\n", s);
				break;
			}
			if(shdr.sh_type != SHT_REL)
				continue;

			if(fseek(fp,shdr.sh_offset,SEEK_SET) != 0) {
				printf("ERROR - Unable to locate the relocation table section.\n");
				continue;
			}

			if (run_mode == RUN_MODE_DUMP)
				printf("Relocation Table Section [%d] (Name: %s) ---\n", s, secnamtab+shdr.sh_name);
			
			count = shdr.sh_size / sizeof(Elf32_Rel);
			for(i=0; i<count; i++)
			{
				switch( run_mode )
				{
				case RUN_MODE_ZERO:
					memset(&rel, fill_value[0], sizeof(rel));
					if( obj_index_first<0 || obj_index_first==index )
					{
						if(fwrite(&rel,sizeof(rel),1,fp) < 1)
							printf("ERROR - Unable to write to the %u-th entry of Relocation Table.\n", i);
					}
					else
					{
						if(fseek(fp,sizeof(rel),SEEK_CUR) != 0)
							printf("ERROR - Unable to locate the %u-th entry of Relocation Table.\n", i);
					}
					break;

				case RUN_MODE_QUERY:
					if(fread(&rel,sizeof(rel),1,fp) < 1)
						printf("ERROR - Unable to read the %u-th entry of Relocation Table.\n", i);
					else if(strcmp(obj_name,query_symbol_name(symp+ELF32_R_SYM(rel.r_info),strp,sechdrtab,secnamtab)) == 0)
						printf("%d ", index);
					break;

				default:
					if(fread(&rel,sizeof(rel),1,fp) < 1)
						printf("ERROR - Unable to read the %u-th entry of Relocation Table.\n", i);
					else
						printf("[%d] \t Relocation Offset: %#X, Type: %#X, Symbol(%u): %s\n", index, rel.r_offset, ELF32_R_TYPE(rel.r_info), ELF32_R_SYM(rel.r_info), query_symbol_name(symp+ELF32_R_SYM(rel.r_info),strp,sechdrtab,secnamtab));
					break;
				}
				
				index ++;
			}
		}
		
		free(symp);
		free(strp);
		break;
		
	case 'h':
		printf("File Identification: \t %s\n", hdr.e_ident);
		printf("Entry Point: \t %#X\n", hdr.e_entry);
		printf("Section Header Table offset: \t %#X\n", hdr.e_shoff);
		printf("Number of Entries in Section Header Table: \t %u\n", hdr.e_shnum);
		printf("Size of Entry in Section Header Table: \t %u\n", hdr.e_shentsize);
		break;
		
	default:
		printf("ERROR - Unrecognisable information.\n");
		break;
	}
	
quit:
	fclose(fp);
	
	if(sechdrtab) free(sechdrtab);
	if(secnamtab) free(secnamtab);
	
	return 0;
}

