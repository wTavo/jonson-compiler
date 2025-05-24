#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Código generado automáticamente desde un archivo .jonson

int main() {
    float temperatura;
    bool activo;
    char mensaje[256];  // Cadena con tamaño suficiente
    int opcion;
    int numeros[] = {1, 2, 3};  // Array inicializado
    int i;
    int a = 5;
    int b = 10;
    
    temperatura = 36.5;
    activo = true;
    strcpy(mensaje, "Hola Mundo");
    if ((temperatura >= "37.5")) {
        printf("%s\n", "Temperatura alta");
    } else {
        printf("%s\n", "Temperatura normal");
    }
    while (activo) {
        for (int i = 0; (i != 3); i += 1) {
            numeros[i] = (numeros[i] * 2);
        }
        activo = false;
    }
    printf("%s\n", mensaje);
    opcion = 2;
    switch (opcion) {
    case 1:
        printf("%s\n", "Opcion 1 seleccionada");
        break;
        break;
    case 2:
        printf("%s\n", "Opcion 2 seleccionada");
        break;
        break;
    case 3:
        printf("%s\n", "Opcion 3 seleccionada");
        break;
        break;
    default:
        printf("%s\n", "Opcion no valida");
    }
    // Asignación de cadena usando strcpy
    strcpy(mensaje, "Fin del programa");
    printf("%s\n", mensaje);
    return 0;
}