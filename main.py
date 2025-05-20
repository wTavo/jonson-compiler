from lexical_analyzer import LexicalAnalyzer
from syntax_analyzer import SyntaxAnalyzer
from semantic_analyzer import SemanticAnalyzer
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
        print("\n" + "="*50)
        print("ANÁLISIS LÉXICO")
        print("="*50)
        
        print("| No.  | Unidades lexicas o lexema |   Token   |   Línea   | Columna |")
        print("|------|---------------------------|-----------|-----------|---------|")
        
        analyzer = LexicalAnalyzer()
        analyzer.tokenize(content)
        
        print("\n" + "="*50)
        print("ANÁLISIS SINTÁCTICO")
        print("="*50)
        
        syntax_analyzer = SyntaxAnalyzer(analyzer.tokens)
        syntax_success = syntax_analyzer.parse()
        
        if not syntax_success:
            print("\nEl análisis sintáctico falló. No se realizará el análisis semántico.")
            return 1
            
        print("\n" + "="*50)
        print("ANÁLISIS SEMÁNTICO")
        print("="*50)
        
        semantic_analyzer = SemanticAnalyzer()
        semantic_success = semantic_analyzer.analyze(syntax_analyzer.ast_root)
        
        # Mostrar errores y advertencias semánticas
        semantic_analyzer.print_errors()
        semantic_analyzer.print_warnings()
        
        # Mostrar árboles de análisis semántico
        semantic_analyzer.print_semantic_trees()
        
        print("\n" + "="*50)
        print("RESUMEN DEL ANÁLISIS")
        print("="*50)
        
        if syntax_success and semantic_success:
            print("✅ El análisis sintáctico se completó exitosamente.")
            print("✅ El análisis semántico se completó exitosamente.")
            print("✅ El archivo cumple con la sintaxis y semántica del lenguaje.")
        elif syntax_success:
            print("✅ El análisis sintáctico se completó exitosamente.")
            print("❌ El análisis semántico encontró errores.")
            print(f"❌ Se encontraron {len(semantic_analyzer.errors)} errores semánticos.")
            print("❌ El archivo NO cumple con la semántica del lenguaje.")
        else:
            print("❌ El análisis sintáctico encontró errores.")
            print(f"❌ Se encontraron {len(syntax_analyzer.errors)} errores sintácticos.")
            print("❌ El archivo NO cumple con la sintaxis del lenguaje.")
        
        return 0 if (syntax_success and semantic_success) else 1
        
    except FileNotFoundError:
        print(f"Error al abrir el archivo: {filename}")
        return 1

if __name__ == "__main__":
    sys.exit(main())