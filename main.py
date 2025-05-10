from lexical_analyzer import LexicalAnalyzer
from syntax_analyzer import SyntaxAnalyzer
import sys

def main():
    if len(sys.argv) < 2:
        print(f"Uso: {sys.argv[0]} <archivo.jonson>")
        return 1
        
    filename = sys.argv[1]
    
    try:
        with open(filename, 'r') as file:
            content = file.read()
            
        print(f"Contenido del archivo {filename}:")
        print(content)
        print()
        
        print("| No.  | Unidades lexicas o lexema |   Token   |   Línea   | Columna |")
        print("|------|---------------------------|-----------|-----------|---------|")
        
        analyzer = LexicalAnalyzer()
        analyzer.tokenize(content)
        
        print("\nIniciando análisis sintáctico...\n")
        syntax_analyzer = SyntaxAnalyzer(analyzer.tokens)
        success = syntax_analyzer.parse()
        
        return 0 if success else 1
        
    except FileNotFoundError:
        print(f"Error al abrir el archivo: {filename}")
        return 1

if __name__ == "__main__":
    sys.exit(main())