#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

// Código generado automáticamente desde un archivo .jonson

// Definición de la clase Persona
typedef struct Persona {
    char nombre[256];  // Asignar tamaño fijo para cadenas
    int edad;
} Persona;

int Persona_obtenerEdad(Persona* this
) {
    return this->edad;
}

void Persona_establecerEdad(Persona* this
, int nuevaEdad
) {
    this->edad = nuevaEdad;
}

int main() {
    float resultado;
    int i;
    int k;
    Persona p;
    int edadPersona;
    bool condicion;
    int a = 5;
    int b = 10;
    int j;
    
    resultado = ((a + b) * 2.5);
    if ((resultado > 30)) {
        printf("%s\n", "El resultado es mayor que 30");
    } else {
        printf("%s\n", "El resultado es menor o igual que 30");
    }
    i = 0;
    while ((i < 5)) {
        printf("%s\n", "IteraciÃ³n nÃºmero: ");
        printf("%d\n", i);
        i = (i + 1);
    }
    for (int j = 0; (j < 3); j = (j + 1)) {
        printf("%s\n", "Ciclo para: ");
        printf("%d\n", j);
    }
    k = 0;
    do {
        printf("%s\n", "Hacer mientras: ");
        printf("%d\n", k);
        k = (k + 1);
    } while ((k < 3));
    switch (a) {
    case 1:
        printf("%s\n", "a es 1");
        break;
        break;
    case 5:
        printf("%s\n", "a es 5");
        break;
        break;
    default:
        printf("%s\n", "a no es ni 1 ni 5");
    }
    // Asignación a miembro nombre del objeto
    strcpy(p.nombre, "Juan");
    Persona_establecerEdad(&p, 25);
    Persona_establecerEdad(&p, 25);
    edadPersona = Persona_obtenerEdad(&p);
    condicion = ((a > 0) && (b < 20));
    return 0;
    return 0;
}