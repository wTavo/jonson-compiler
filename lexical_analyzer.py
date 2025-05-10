from tokens import *  # Importa todas las constantes de tokens
import re
import sys

class LexicalAnalyzer:
    def __init__(self):
        self.num_token = 1
        self.tokens = []  # Lista para almacenar los tokens como diccionarios
        self.line = 1     # Rastreo de línea actual
        self.column = 1   # Rastreo de columna actual
        
    def imprimir_tabla(self, lexema, token_type):
        """Print token information in a table format"""
        print(f"| {self.num_token:<4} | {lexema:<25} | {token_type:<9} | {self.line:^9} | {self.column:^7} |")
        
        # Convertir tipos numéricos a tokens constantes
        if token_type == 'int_num':
            token_type = TOK_NUM_ENTERO
        elif token_type == 'float_num':
            token_type = TOK_NUM_FLOTANTE
            
        # Almacenar el token con información completa
        self.tokens.append({
            'lexema': lexema,
            'tipo': token_type,
            'linea': self.line,
            'columna': self.column
        })
        
        # Actualizar posición de columna
        self.column += len(lexema)
        self.num_token += 1
        
    def tokenize(self, text):
        """Process the input text and extract tokens"""
        position = 0
        self.line = 1
        self.column = 1
        espacio_antes_carac_t = False
        self.tokens = []  # Reiniciar la lista de tokens
        self.num_token = 1  # Reiniciar el contador
        
        # Compilar patrones regex una sola vez para mayor eficiencia
        patterns = [
            # Comments (should be first to handle them properly)
            (re.compile(r'^//.*'), None),  # Single-line comment
            (re.compile(r'^/\*(?:[^*]|\*+[^*/])*\*+/'), None),  # Multi-line comment
            
            # Whitespace
            (re.compile(r'^[ \t]+'), 'space'),  # Espacios y tabs
            (re.compile(r'^\n'), None),      # Saltos de línea
            
            # Keywords for loops and conditionals with special handling
            (re.compile(r'^mientras'), TOK_CICLO),
            (re.compile(r'^hacer'), TOK_CICLO),
            (re.compile(r'^para'), TOK_CICLO),
            
            # Data types
            (re.compile(r'^(entero|flotante|booleano|caracter|cadena|vacio)'), TOK_TIPO_DATO),
            
            # Reserved words
            (re.compile(r'^(principal|publico|privado|clase|imprimir|escribir|romper|retornar|predeterminado|cambio)'), TOK_PAL_RES),
            
            # Boolean literals
            (re.compile(r'^(verdadero|falso)'), TOK_PAL_RES),

            # Conditional
            (re.compile(r'^sino'), TOK_CONDICIONAL),
            (re.compile(r'^(si|caso)'), TOK_CONDICIONAL),
            
            # Operators
            (re.compile(r'^=='), TOK_IGUAL),
            (re.compile(r'^!='), TOK_DISTINTO),
            (re.compile(r'^<='), TOK_MENOR_IGUAL),
            (re.compile(r'^>='), TOK_MAYOR_IGUAL),
            (re.compile(r'^\+='), TOK_ASIG_SUMA),
            (re.compile(r'^\+'), TOK_SUMA),
            (re.compile(r'^-'), TOK_RESTA),
            (re.compile(r'^\*'), TOK_MULT),
            (re.compile(r'^/'), TOK_DIV),
            (re.compile(r'^%'), TOK_MOD),
            (re.compile(r'^<'), TOK_MENOR),
            (re.compile(r'^>'), TOK_MAYOR),
            (re.compile(r'^='), TOK_ASIG),
            (re.compile(r'^AND'), TOK_AND),
            (re.compile(r'^OR'), TOK_OR),
            (re.compile(r'^NOT'), TOK_NOT),
            
            # Special characters
            (re.compile(r'^~'), TOK_CARAC_T),
            (re.compile(r'^;'), TOK_PUNTO_COMA),
            (re.compile(r'^,'), TOK_COMA),
            (re.compile(r'^:'), TOK_DOS_PUNTOS),
            (re.compile(r'^\.'), TOK_PUNTO),
            (re.compile(r'^\['), TOK_CORCHETE_IZQ),
            (re.compile(r'^\]'), TOK_CORCHETE_DER),
            (re.compile(r'^\('), TOK_PAREN_IZQ),
            (re.compile(r'^\)'), TOK_PAREN_DER),
            (re.compile(r'^{'), TOK_LLAVE_IZQ),
            (re.compile(r'^}'), TOK_LLAVE_DER),
            
            # Numbers
            (re.compile(r'^\d+\.\d*'), 'float_num'),
            (re.compile(r'^\d+'), 'int_num'),
            
            # Strings
            (re.compile(r'^"[^"]*"'), TOK_CADENA),
            
            # Identifiers
            (re.compile(r'^[a-zA-Z_][a-zA-Z0-9_]*'), TOK_ID),
            
            # Catch-all for errors
            (re.compile(r'^.'), TOK_ERROR),
        ]
        
        text_length = len(text)
        
        while position < text_length:
            # Manejo especial para saltos de línea
            if text[position] == '\n':
                self.line += 1
                self.column = 1
                position += 1
                espacio_antes_carac_t = False  # Resetear al cambiar de línea
                continue
                
            match = None
            
            for regex, token_type in patterns:
                match = regex.search(text[position:])
                if match:
                    lexeme = match.group(0)
                    position += len(lexeme)
                    
                    # Manejar espacios para detectar espacios antes de ~
                    if token_type == 'space':
                        espacio_antes_carac_t = True
                        break
                    
                    # Detectar error específico: espacio antes de ~
                    if token_type == TOK_CARAC_T and espacio_antes_carac_t:
                        error_msg = f"Error: Espacio antes del carácter de terminación '~' en línea {self.line}, columna {self.column}"
                        self.warnings.append(error_msg)
                        self.imprimir_tabla(lexeme, TOK_ERROR)
                        espacio_antes_carac_t = False
                        break
                    
                    # Skip if None (comments, whitespace)
                    if token_type is None:
                        espacio_antes_carac_t = False
                        break
                        
                    self.imprimir_tabla(lexeme, token_type)
                    espacio_antes_carac_t = False
                    break
            
            if not match:
                # Carácter no reconocido (aunque esto no debería ocurrir debido al patrón catch-all)
                self.imprimir_tabla(text[position], TOK_ERROR)
                position += 1
                self.column += 1
                espacio_antes_carac_t = False

    def tokenize_file(self, filename):
        """Convenience method to tokenize a file directly"""
        with open(filename, 'r') as f:
            content = f.read()
        return self.tokenize(content)