#include <stdio.h>
#include <string.h>
#include <stdlib.h>

char *vvv(char un[], char pw[])
{
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
            int pw_ord = pw[adv%pw_l];
            adv = (i + pair_i + adv + pw_ord)%99;
            un_ord = (un_ord - ani + adv)%62;
            pair_i = abs(un_ord + un_ord - 61);
            un_ord = (185 - un_ord - adv)%62;
            un_ord += un_ord<=9 ? 48 : un_ord<=35 ? 55 : 61;
        }
        out[i] = un_ord;
    }
    return out;
}


int main()
{
    printf("Hello World");

    char un[] = "h4ck3r0n5t3r01d5";
    char pw[] = "t3hpvv4n1d10tvv0u1du530nh151u6646310ck";
    char cont[] = "0123456789.ABCDEFGHIJKLMNOPQRSTUVWXYZ_abcdefghijklmnopqrstuvwxyz!@#$\%^&*()";
    
    printf("\nFilename: %s_%s\n", vvv(un,pw), vvv(pw,un));
    printf("Encrypted Contents: %s\n\n", vvv(cont,pw));
    printf("Retrieve from file:\nDecrypted Contents: %s", vvv(vvv(cont,pw),pw));
}