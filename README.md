# Compilador PLY para lenguaje Jonson

Este proyecto implementa un compilador para el lenguaje de programación "Jonson" utilizando la biblioteca PLY (Python Lex-Yacc). El compilador incluye un analizador léxico y un analizador sintáctico que genera un árbol de derivación visual.

## Características del lenguaje Jonson

- Tipos de datos: entero, flotante, booleano, cadena y arrays
- Estructuras de control: if-else, switch-case, while, do-while, for
- Funciones y métodos
- Clases con modificadores de acceso (público/privado)
- Operadores aritméticos, relacionales y lógicos
- Soporte para comentarios

## Estructura del proyecto

- `main.py`: Punto de entrada del compilador
- `tokens.py`: Definición de tokens para el analizador léxico
- `syntax_analyzer.py`: Implementación del analizador sintáctico
- `codigo4.jonson`: Ejemplo de código en lenguaje Jonson

## Requisitos

- Python 3.6+
- PLY (Python Lex-Yacc)

## Instalación

```bash
pip install ply
```

## Uso

Para analizar un archivo de código Jonson:

```bash
python main.py archivo.jonson
```

## Ejemplo de código Jonson

```
principal() {
    entero[] numeros = [1, 2, 3]~
    flotante temperatura = 36.5~
    booleano activo = verdadero~
    cadena mensaje = "Hola Mundo"~

    //este es un comentario

    si (temperatura >= 37.5) {
        imprimir("Temperatura alta")~
    } sino {
        imprimir("Temperatura normal")~
    }

    mientras(activo) {
        para(entero i = 0; i != 3; i += 1) {
            numeros[i] = numeros[i] * 2~
        }
        activo = falso~
    }

    imprimir(mensaje)~
}
```

## Árbol de derivación

El analizador sintáctico genera un árbol de derivación visual que muestra la estructura jerárquica del código analizado:

```
programa
└── principal
    └── bloque
        └── sentencias
            ├── sentencia
            │   └── declaracion_array
            │       ├── tipo_array: entero
            │       ├── id: numeros
            │       └── array_literal
            │           └── lista_expresiones
            │               ├── factor: 1
            │               ├── factor: 2
            │               └── factor: 3
            ├── sentencia
            │   └── declaracion_variable
            │       ├── tipo_dato: flotante
            │       ├── id: temperatura
            │       └── factor: 36.5
            └── ...
```

## Características del analizador

- Generación de árboles de derivación visuales con estructura jerárquica clara
- Detección y reporte de errores sintácticos
- Soporte para arrays y acceso a elementos
- Soporte para valores booleanos
- Manejo de precedencia de operadores

## Licencia

Este proyecto está bajo la Licencia MIT. 