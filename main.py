from lexical_analyzer import LexicalAnalyzer
from syntax_analyzer import SyntaxAnalyzer
from semantic_analyzer import SemanticAnalyzer
from code_generator import CodeGenerator
import sys
import os

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
        ast = syntax_analyzer.ast_root
        
        if not syntax_success:
            print("\nEl análisis sintáctico falló. No se realizará el análisis semántico.")
            return 1
            
        print("\n" + "="*50)
        print("ANÁLISIS SEMÁNTICO")
        print("="*50)
        
        semantic_analyzer = SemanticAnalyzer()
        semantic_success = semantic_analyzer.analyze(ast)
        
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
            
            # Generar código C
            print("\n" + "="*50)
            print("GENERACIÓN DE CÓDIGO C")
            print("="*50)
            
            code_generator = CodeGenerator()
            c_code = code_generator.generate(ast)
            
            # Crear el archivo de salida .c
            output_filename = os.path.splitext(filename)[0] + ".c"
            with open(output_filename, 'w') as c_file:
                c_file.write(c_code)
                
            print(f"✅ Código C generado exitosamente en: {output_filename}")
            print("\nCódigo C generado:")
            print("-" * 30)
            print(c_code)
            print("-" * 30)
            
        elif syntax_success:
            print("✅ El análisis sintáctico se completó exitosamente.")
            print("❌ El análisis semántico encontró errores.")
            print(f"❌ Se encontraron {len(semantic_analyzer.errors)} errores semánticos.")
            print("❌ El archivo NO cumple con la semántica del lenguaje.")
            print("❌ No se generará código C debido a errores semánticos.")
        else:
            print("❌ El análisis sintáctico encontró errores.")
            print(f"❌ Se encontraron {len(syntax_analyzer.errors)} errores sintácticos.")
            print("❌ El archivo NO cumple con la sintaxis del lenguaje.")
            print("❌ No se generará código C debido a errores sintácticos.")
        
        return 0 if (syntax_success and semantic_success) else 1
        
    except FileNotFoundError:
        print(f"Error al abrir el archivo: {filename}")
        return 1

if __name__ == "__main__":
    sys.exit(main())