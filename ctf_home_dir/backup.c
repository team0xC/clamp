#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#include <sys/types.h>
#include <sys/uio.h>
#include <unistd.h>

unsigned int num_files;
char name[100];
char password[100];

struct temp_files {
   char* contents;
   unsigned int size;
   struct temp_files* next;
};

struct temp_files* head = NULL;

//added
char *vvv(char un[], char pw[]){
    //USES STR LEN 1000
    int pw_l = strlen(pw);
    int un_l = strlen(un);
    if (un_l >= 1000) {un_l = 1000;}
    char * out;
    out = malloc(sizeof(char)*1000);
    int adv = 0;
    int pair_i = 0;
    for (int i = 0; i < un_l; i++) {
        int un_ord = un[i];
        int ani;
        ani = un_ord>=48&&un_ord<=57 ? 48 : un_ord>=65&&un_ord<=90 ? 55 : un_ord>=97&&un_ord<=122 ? 61 : -1;
        if (ani >= 0) {
            adv = (i + pair_i + adv + pw[adv%pw_l] + pw[i%pw_l])%99;
            un_ord = (un_ord - ani + adv)%62;
            pair_i = abs(un_ord + un_ord - 61);
            un_ord = (185 - un_ord - adv)%62;
            un_ord += un_ord<=9 ? 48 : un_ord<=35 ? 55 : 61;
        }
        out[i] = un_ord;
    }
    return out;
}
//========

int readline(char *buf, int size) {
  int i;
  for(i = 0; i < size; i++) {
    if(read(0, buf+i, 1) <= 0) {
      exit(1);
    }
    if (buf[i] == '\n') {
      buf[i] = '\x00';
      return i;
    }
  }
  buf[size-1] = '\x00';
  return size-1;
}

void read_in_bytes(char* new_file, unsigned int the_size)
{
   int i = 0;
   while (i < the_size)
   {
	  if (read(0, new_file+i, 1) != 1)
	  {
		 exit(0);
	  }
	  i += 1;
   }
}

void printmenu()
{
   printf("Hello, welcome to the secure data storage system.\n");
   printf("(1) Securely start backup.\n");
   printf("(2) Retrieve secure backup.\n");
   printf("(3) Exit.\n");
   printf("> ");
   fflush(stdout);
}

void print_backup_menu()
{
   printf("You currently have %d files ready to be stored for backup.\n", num_files);
   printf("(1) Add a file.\n");
   printf("(2) Remove all files.\n");
   printf("(3) Store files.\n");
   printf("(4) Return to menu without saving.\n");
   fflush(stdout);	  
}

void add_file()
{
   char size[20];
   unsigned int the_size;
   char* new_file;
   struct temp_files* tmp;
   printf("How big (in bytes) is your file? ");
   fflush(stdout);   
   readline(size, 20);

   the_size = atoi(size);
   new_file = malloc(the_size);
   
   printf("Go ahead, send your file\n");
   fflush(stdout);

   read_in_bytes(new_file, the_size);

   if (head == NULL)
   {
	  head = (struct temp_files*) malloc(sizeof(struct temp_files));
	  head->contents = NULL;
	  head->next = NULL;
   }
   tmp = head;
   while (tmp->next != NULL)
   {
	  tmp = tmp->next;
   }

   tmp->next = (struct temp_files*) malloc(sizeof(struct temp_files));
   tmp->next->next = NULL;
   tmp->next->contents = new_file;
   tmp->next->size = the_size;

   num_files += 1;

   printf("File successfully added.\n");
   fflush(stdout);
}


void free_list(struct temp_files* cur)
{
   if (cur == NULL)
   {
	  return;
   }
   if (cur->next != NULL)
   {
	  free_list(cur->next);
   }

   if (cur->contents != NULL)
   {
	  free(cur->contents);
   }
   free(cur);
}

void remove_all_files()
{
   free_list(head);

   head = NULL;
   num_files = 0;
}

void store_all_files()
{
   char filename[120];
   FILE* new_file;
   struct temp_files* tmp;
   filename[0] = '\0';
   strcat(filename, vvv(name,password)); //modified
   strcat(filename, "_");
   strcat(filename, vvv(password,name)); //modified
   strcat(filename, ".secure.bak");

   if (head == NULL)
   {
	  printf("ERROR, no files to store.\n");
	  fflush(stdout);
	  return;
   }

   new_file = fopen(filename, "w+");

   char filecont[1000]; //added
   filecont[0] = '\0'; //added

   tmp = head->next;
   while(tmp != NULL)
   {
	  //fwrite(tmp->contents, tmp->size, 1, new_file);
	  strcat(filecont, tmp->contents); //added; does it matter if it gets null terminated?
	  tmp = tmp->next;
   }

   fputs(vvv(filecont,password), new_file); //added

   fclose(new_file);
   remove_all_files();
}

void get_info()
{
   printf("Select a name for your backup: ");
   fflush(stdout);
   readline(name, 100);
   printf("\n");
   
   printf("Choose a secure password for your backup: ");
   fflush(stdout);
   readline(password, 100);
   printf("\n");
}

void start_backup()
{
   char input[40];
   num_files = 0;
   head = NULL;
   get_info();
   
   while (1)
   {
	  print_backup_menu();
	  readline(input, 40);
	  if (!strcmp(input, "1"))
	  {
		 add_file();
	  }
	  else if (!strcmp(input, "2"))
	  {
		 remove_all_files();
	  }
	  else if (!strcmp(input, "3"))
	  {
		 store_all_files();
		 break;
	  }
	  else
	  {
		 break;
	  }
   }
}

void retrieve_backup()
{
   //char cmd[1000];
   get_info();

   printf("Here is your backup data that was stored securely:\n");
   fflush(stdout);
   //snprintf(cmd, 200, "%s_%s.secure.bak", vvv(name,password), vvv(password,name));
   //system(cmd); //why

   char filename[120]; //added
   filename[0] = '\0'; //added
   strcat(filename, vvv(name,password)); //modified
   strcat(filename, "_"); //added
   strcat(filename, vvv(password,name)); //modified
   strcat(filename, ".secure.bak"); //added

   FILE *open_file = fopen(filename, "r"); //added
   if (open_file == NULL) {
      return;
   }

   char out[1000]; //added
   int i=0; //added
   while((out[i++] = fgetc(open_file)) != EOF) { //added	
   } //added
   out[i-1]='\0'; //added
   fclose(open_file); //added
   puts(vvv(out,password)); //added
}

int main(int argc, char** argv)
{
   char input[40];
   chdir("../append/");
   while (1)
   {
	  printmenu();
	  readline(input, 40);
	  if (!strcmp(input, "1"))
	  {
		 start_backup();
	  }
	  else if (!strcmp(input, "2"))
	  {
		 retrieve_backup();
	  }
	  else
	  {
		 printf("Goodbye!\n");
		 fflush(stdout);
		 exit(0);
	  }
   }
   
}
