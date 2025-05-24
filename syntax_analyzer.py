import ply.yacc as yacc
from tokens import *

class Node:
    def __init__(self, type, children=None, leaf=None, line=0, column=0):
        self.type = type
        self.children = children if children else []
        self.leaf = leaf
        self.line = line      # Línea donde se encuentra el nodo
        self.column = column  # Columna donde se encuentra el nodo

    def __str__(self, level=0, is_last=False):
        # Prefijo para el nivel actual (espacios o líneas verticales)
        prefix = ""
        for i in range(level):
            if i == level - 1:
                prefix += "└── " if is_last else "├── "
            else:
                prefix += "    " if i < level - 1 else "│   "
        
        # Nodo actual
        ret = prefix + self.type
        if self.leaf is not None:
            ret += f": {self.leaf}"
        ret += f" (línea: {self.line}, col: {self.column})" if self.line > 0 else ""
        ret += "\n"
        
        # Procesar hijos
        num_children = len(self.children)
        for i, child in enumerate(self.children):
            is_last_child = (i == num_children - 1)
            ret += child.__str__(level + 1, is_last_child)
        
        return ret
        
    def print_tree(self):
        """Método para imprimir el árbol desde la raíz"""
        print(self.__str__(0, True))

class SyntaxAnalyzer:
    # Definimos todos los tokens que usará el parser
    tokens = [
        'TIPO_DATO', 'ID', 'SUMA', 'RESTA', 'MULT', 'DIV', 'MOD', 'ASIG', 'ASIG_SUMA',
        'IGUAL', 'DISTINTO', 'MENOR_IGUAL', 'MAYOR_IGUAL', 'MENOR', 'MAYOR', 
        'AND', 'OR', 'NOT', 'CICLO', 'CONDICIONAL', 'CARAC_T', 'PUNTO_COMA', 
        'COMA', 'PUNTO', 'DOS_PUNTOS', 'CORCHETE_IZQ', 'CORCHETE_DER', 
        'PAREN_IZQ', 'PAREN_DER', 'LLAVE_IZQ', 'LLAVE_DER', 'PAL_RES', 
        'NUM_ENTERO', 'NUM_FLOTANTE', 'CADENA', 'ERROR', 'PRINCIPAL', 
        'CLASE', 'PUBLICO', 'PRIVADO', 'RETORNAR', 'IMPRIMIR', 'SI', 
        'SINO', 'MIENTRAS', 'HACER', 'PARA', 'CAMBIO', 'CASO', 
        'PREDETERMINADO', 'ROMPER', 'VERDADERO', 'FALSO'
    ]
    
    # Precedencia de operadores (de menor a mayor)
    precedence = (
        ('left', 'OR'),
        ('left', 'AND'),
        ('left', 'IGUAL', 'DISTINTO'),
        ('left', 'MENOR', 'MAYOR', 'MENOR_IGUAL', 'MAYOR_IGUAL'),
        ('left', 'SUMA', 'RESTA'),
        ('left', 'MULT', 'DIV', 'MOD'),
        ('right', 'NOT')
    )
    
    def __init__(self, tokens_list=None):
        self.tokens_list = tokens_list if tokens_list else []
        self.lexer = self._build_lexer_from_tokens()
        self.parser = None
        self.errors = []
        self.ast_root = None
        self.build_parser()

    def build_parser(self):
        self.parser = yacc.yacc(module=self, debug=True)
        return self.parser
    
    # Reglas de la gramática simplificadas
    def p_programa(self, p):
        '''programa : declaraciones_clases principal
                    | principal'''
        p[0] = Node('programa', [p[1]] if len(p) == 2 else [p[1], p[2]])
        self.ast_root = p[0]

    def p_declaraciones_clases(self, p):
        '''declaraciones_clases : declaracion_clase
                               | declaraciones_clases declaracion_clase'''
        if len(p) == 2:
            p[0] = Node('declaraciones_clases', [p[1]])
        else:
            p[1].children.append(p[2])
            p[0] = p[1]

    def p_declaracion_clase(self, p):
        '''declaracion_clase : CLASE ID LLAVE_IZQ miembros_clase LLAVE_DER
                            | modificador_acceso CLASE ID LLAVE_IZQ miembros_clase LLAVE_DER'''
        if len(p) == 6:
            p[0] = Node('declaracion_clase', [p[4]], p[2])
        else:
            p[0] = Node('declaracion_clase', [p[1], p[5]], p[3])

    def p_miembros_clase(self, p):
        '''miembros_clase : miembro_clase
                         | miembros_clase miembro_clase
                         | empty'''
        if len(p) == 2 and p[1] is None:
            p[0] = Node('miembros_clase', [])
        elif len(p) == 2:
            p[0] = Node('miembros_clase', [p[1]])
        else:
            p[1].children.append(p[2])
            p[0] = p[1]

    def p_miembro_clase(self, p):
        '''miembro_clase : modificador_acceso declaracion_variable
                        | modificador_acceso declaracion_metodo
                        | tipo_dato lista_ids CARAC_T
                        | tipo_dato ID ASIG expresion CARAC_T'''
        if len(p) == 3:
            p[0] = Node('miembro_clase', [p[1], p[2]])
        elif len(p) == 4:
            p[0] = Node('miembro_clase', [p[1], p[2]])
        else:
            p[0] = Node('miembro_clase', [p[1], Node('id', [], p[2]), p[4]])

    def p_modificador_acceso(self, p):
        '''modificador_acceso : PUBLICO
                             | PRIVADO'''
        p[0] = Node('modificador_acceso', [], p[1])

    def p_principal(self, p):
        '''principal : PRINCIPAL PAREN_IZQ PAREN_DER bloque'''
        p[0] = Node('principal', [p[4]])

    def p_bloque(self, p):
        '''bloque : LLAVE_IZQ sentencias LLAVE_DER'''
        p[0] = Node('bloque', [p[2]])

    def p_sentencias(self, p):
        '''sentencias : sentencia
                     | sentencias sentencia
                     | empty'''
        if len(p) == 2 and p[1] is None:
            p[0] = Node('sentencias', [])
        elif len(p) == 2:
            p[0] = Node('sentencias', [p[1]])
        else:
            p[1].children.append(p[2])
            p[0] = p[1]

    def p_sentencia(self, p):
        '''sentencia : declaracion_variable
                    | asignacion
                    | llamada_funcion
                    | sentencia_if
                    | sentencia_switch
                    | sentencia_while
                    | sentencia_do_while
                    | sentencia_for
                    | sentencia_return
                    | sentencia_break
                    | sentencia_print'''
        p[0] = Node('sentencia', [p[1]])

    def p_declaracion_variable(self, p):
        '''declaracion_variable : tipo_dato lista_ids CARAC_T
                               | tipo_dato ID ASIG expresion CARAC_T
                               | tipo_dato lista_ids_inicializadas CARAC_T
                               | tipo_dato ID ASIG array_literal CARAC_T'''
        if len(p) == 4 and isinstance(p[2], Node) and p[2].type == 'lista_ids':
            p[0] = Node('declaracion_variable', [p[1], p[2]], None, p.lineno(1), p.lexpos(1))
        elif len(p) == 6 and isinstance(p[4], Node) and p[4].type == 'array_literal':
            p[0] = Node('declaracion_array', [p[1], Node('id', [], p[2], p.lineno(2), p.lexpos(2)), p[4]], None, p.lineno(1), p.lexpos(1))
        elif len(p) == 6:
            p[0] = Node('declaracion_variable', [p[1], Node('id', [], p[2], p.lineno(2), p.lexpos(2)), p[4]], None, p.lineno(1), p.lexpos(1))
        else:
            p[0] = Node('declaracion_variable', [p[1], p[2]], None, p.lineno(1), p.lexpos(1))

    def p_lista_ids(self, p):
        '''lista_ids : ID
                    | lista_ids COMA ID'''
        if len(p) == 2:
            p[0] = Node('lista_ids', [Node('id', [], p[1], p.lineno(1), p.lexpos(1))], None, p.lineno(1), p.lexpos(1))
        else:
            p[1].children.append(Node('id', [], p[3], p.lineno(3), p.lexpos(3)))
            p[0] = p[1]

    def p_lista_ids_inicializadas(self, p):
        '''lista_ids_inicializadas : ID ASIG expresion
                                  | lista_ids_inicializadas COMA ID ASIG expresion'''
        if len(p) == 4:
            p[0] = Node('lista_ids_inicializadas', [Node('id', [], p[1]), p[3]])
        else:
            p[1].children.append(Node('id', [], p[3]))
            p[1].children.append(p[5])
            p[0] = p[1]

    def p_tipo_dato(self, p):
        '''tipo_dato : TIPO_DATO
                    | ID
                    | TIPO_DATO CORCHETE_IZQ CORCHETE_DER
                    | ID CORCHETE_IZQ CORCHETE_DER'''
        if len(p) == 2:
            p[0] = Node('tipo_dato', [], p[1], p.lineno(1), p.lexpos(1))
        else:
            p[0] = Node('tipo_array', [], p[1], p.lineno(1), p.lexpos(1))  # Tipo de array

    def p_asignacion(self, p):
        '''asignacion : ID ASIG expresion CARAC_T
                     | ID acceso_objeto ASIG expresion CARAC_T
                     | ID ASIG_SUMA expresion CARAC_T
                     | ID CORCHETE_IZQ expresion CORCHETE_DER ASIG expresion CARAC_T'''
        if len(p) == 5:
            p[0] = Node('asignacion', [Node('id', [], p[1], p.lineno(1), p.lexpos(1)), p[3]], None, p.lineno(1), p.lexpos(1))
        elif len(p) == 6 and isinstance(p[2], Node) and p[2].type == 'acceso_objeto':
            id_node = Node('id', [], p[1], p.lineno(1), p.lexpos(1))
            id_node.children.append(p[2])
            p[0] = Node('asignacion', [id_node, p[4]], None, p.lineno(1), p.lexpos(1))
        elif len(p) == 8:  # Asignación a elemento de array
            acceso_array = Node('acceso_array', [Node('id', [], p[1], p.lineno(1), p.lexpos(1)), p[3]], None, p.lineno(1), p.lexpos(1))
            p[0] = Node('asignacion', [acceso_array, p[6]], None, p.lineno(1), p.lexpos(1))
        else:
            p[0] = Node('asignacion_compuesta', [Node('id', [], p[1], p.lineno(1), p.lexpos(1)), p[3]], p[2], p.lineno(1), p.lexpos(1))

    def p_acceso_objeto(self, p):
        '''acceso_objeto : PUNTO ID
                        | PUNTO ID acceso_objeto'''
        if len(p) == 3:
            p[0] = Node('acceso_objeto', [Node('id', [], p[2])])
        else:
            p[0] = Node('acceso_objeto', [Node('id', [], p[2]), p[3]])

    def p_llamada_funcion(self, p):
        '''llamada_funcion : ID PAREN_IZQ argumentos PAREN_DER CARAC_T
                          | ID acceso_objeto PAREN_IZQ argumentos PAREN_DER CARAC_T'''
        if len(p) == 6:
            p[0] = Node('llamada_funcion', [Node('id', [], p[1]), p[3]])
        else:
            id_node = Node('id', [], p[1])
            id_node.children.append(p[2])
            p[0] = Node('llamada_funcion', [id_node, p[4]])

    def p_argumentos(self, p):
        '''argumentos : lista_expresiones
                     | empty'''
        p[0] = Node('argumentos', [] if p[1] is None else [p[1]])

    def p_lista_expresiones(self, p):
        '''lista_expresiones : expresion
                            | lista_expresiones COMA expresion'''
        if len(p) == 2:
            p[0] = Node('lista_expresiones', [p[1]])
        else:
            p[1].children.append(p[3])
            p[0] = p[1]

    def p_sentencia_if(self, p):
        '''sentencia_if : SI PAREN_IZQ expresion PAREN_DER bloque
                       | SI PAREN_IZQ expresion PAREN_DER bloque SINO bloque'''
        if len(p) == 6:
            p[0] = Node('sentencia_if', [p[3], p[5]], None, p.lineno(1), p.lexpos(1))
        else:
            p[0] = Node('sentencia_if', [p[3], p[5], p[7]], None, p.lineno(1), p.lexpos(1))

    def p_sentencia_switch(self, p):
        '''sentencia_switch : CAMBIO PAREN_IZQ expresion PAREN_DER LLAVE_IZQ casos_switch LLAVE_DER'''
        p[0] = Node('sentencia_switch', [p[3], p[6]])

    def p_casos_switch(self, p):
        '''casos_switch : caso_switch
                       | casos_switch caso_switch
                       | empty'''
        if len(p) == 2 and p[1] is None:
            p[0] = Node('casos_switch', [])
        elif len(p) == 2:
            p[0] = Node('casos_switch', [p[1]])
        else:
            p[1].children.append(p[2])
            p[0] = p[1]

    def p_caso_switch(self, p):
        '''caso_switch : CASO expresion DOS_PUNTOS sentencias sentencia_break
                      | CASO expresion DOS_PUNTOS sentencias
                      | PREDETERMINADO DOS_PUNTOS sentencias'''
        if len(p) == 6:
            p[0] = Node('caso_switch', [p[2], p[4], p[5]])
        elif len(p) == 5:
            p[0] = Node('caso_switch', [p[2], p[4]])
        else:
            p[0] = Node('caso_default', [p[3]])

    def p_sentencia_while(self, p):
        '''sentencia_while : MIENTRAS PAREN_IZQ expresion PAREN_DER bloque'''
        p[0] = Node('sentencia_while', [p[3], p[5]], None, p.lineno(1), p.lexpos(1))

    def p_sentencia_do_while(self, p):
        '''sentencia_do_while : HACER bloque MIENTRAS PAREN_IZQ expresion PAREN_DER CARAC_T'''
        p[0] = Node('sentencia_do_while', [p[2], p[5]])

    def p_sentencia_for(self, p):
        '''sentencia_for : PARA PAREN_IZQ asignacion_for expresion PUNTO_COMA actualizacion_for PAREN_DER bloque'''
        p[0] = Node('sentencia_for', [p[3], p[4], p[6], p[8]])

    def p_asignacion_for(self, p):
        '''asignacion_for : tipo_dato ID ASIG expresion PUNTO_COMA
                         | ID ASIG expresion PUNTO_COMA'''
        if len(p) == 6:
            p[0] = Node('asignacion_for', [p[1], Node('id', [], p[2]), p[4]])
        else:
            p[0] = Node('asignacion_for', [Node('id', [], p[1]), p[3]])

    def p_actualizacion_for(self, p):
        '''actualizacion_for : ID ASIG expresion
                           | ID ASIG_SUMA expresion'''
        p[0] = Node('actualizacion_for', [Node('id', [], p[1]), p[3]], p[2])

    def p_sentencia_return(self, p):
        '''sentencia_return : RETORNAR expresion CARAC_T
                           | RETORNAR CARAC_T'''
        p[0] = Node('sentencia_return', [p[2]] if len(p) == 4 else [])

    def p_sentencia_break(self, p):
        '''sentencia_break : ROMPER CARAC_T'''
        p[0] = Node('sentencia_break', [])

    def p_sentencia_print(self, p):
        '''sentencia_print : IMPRIMIR PAREN_IZQ expresion PAREN_DER CARAC_T'''
        p[0] = Node('sentencia_print', [p[3]], None, p.lineno(1), p.lexpos(1))

    def p_declaracion_metodo(self, p):
        '''declaracion_metodo : tipo_dato ID PAREN_IZQ parametros PAREN_DER bloque
                             | ID PAREN_IZQ parametros PAREN_DER bloque'''
        if len(p) == 7 and isinstance(p[1], Node):  # Con tipo_dato
            p[0] = Node('declaracion_metodo', [p[1], Node('id', [], p[2]), p[4], p[6]])
        else:  # Sin tipo de retorno especificado (ID directo)
            p[0] = Node('declaracion_metodo', [Node('id', [], p[1]), p[3], p[5]])

    def p_parametros(self, p):
        '''parametros : lista_parametros
                     | empty'''
        p[0] = Node('parametros', [] if p[1] is None else [p[1]])

    def p_lista_parametros(self, p):
        '''lista_parametros : tipo_dato ID
                           | lista_parametros COMA tipo_dato ID'''
        if len(p) == 3:
            p[0] = Node('lista_parametros', [p[1], Node('id', [], p[2])])
        else:
            p[1].children.append(p[3])
            p[1].children.append(Node('id', [], p[4]))
            p[0] = p[1]

    # Expresiones
    def p_expresion(self, p):
        '''expresion : expresion_logica'''
        p[0] = p[1]

    def p_expresion_logica(self, p):
        '''expresion_logica : expresion_relacional
                           | expresion_logica AND expresion_relacional
                           | expresion_logica OR expresion_relacional
                           | NOT expresion_relacional'''
        if len(p) == 2:
            p[0] = p[1]
        elif p[1] == 'NOT':
            p[0] = Node('expresion_logica', [p[2]], p[1])
        else:
            p[0] = Node('expresion_logica', [p[1], p[3]], p[2])

    def p_expresion_relacional(self, p):
        '''expresion_relacional : expresion_aritmetica
                               | expresion_relacional IGUAL expresion_aritmetica
                               | expresion_relacional DISTINTO expresion_aritmetica
                               | expresion_relacional MENOR expresion_aritmetica
                               | expresion_relacional MAYOR expresion_aritmetica
                               | expresion_relacional MENOR_IGUAL expresion_aritmetica
                               | expresion_relacional MAYOR_IGUAL expresion_aritmetica'''
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = Node('expresion_relacional', [p[1], p[3]], p[2], p.lineno(2), p.lexpos(2))

    def p_expresion_aritmetica(self, p):
        '''expresion_aritmetica : termino
                               | expresion_aritmetica SUMA termino
                               | expresion_aritmetica RESTA termino'''
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = Node('expresion_aritmetica', [p[1], p[3]], p[2], p.lineno(2), p.lexpos(2))

    def p_termino(self, p):
        '''termino : factor
                   | termino MULT factor
                   | termino DIV factor
                   | termino MOD factor'''
        if len(p) == 2:
            p[0] = p[1]
        else:
            p[0] = Node('termino', [p[1], p[3]], p[2])

    def p_factor(self, p):
        '''factor : PAREN_IZQ expresion PAREN_DER
                  | NUM_ENTERO
                  | NUM_FLOTANTE
                  | CADENA
                  | ID
                  | llamada_metodo
                  | ID acceso_objeto
                  | ID CORCHETE_IZQ expresion CORCHETE_DER
                  | array_literal
                  | VERDADERO
                  | FALSO'''
        if len(p) == 4 and p[1] == '(':  # Paréntesis
            p[0] = p[2]
        elif len(p) == 5:  # Acceso a array
            p[0] = Node('acceso_array', [Node('id', [], p[1], p.lineno(1), p.lexpos(1)), p[3]], None, p.lineno(1), p.lexpos(1))
        elif len(p) == 2:
            if p.slice[1].type in ('NUM_ENTERO', 'NUM_FLOTANTE', 'CADENA'):
                p[0] = Node('factor', [], p[1], p.lineno(1), p.lexpos(1))
            elif p.slice[1].type in ('VERDADERO', 'FALSO'):
                p[0] = Node('booleano', [], p[1], p.lineno(1), p.lexpos(1))
            elif isinstance(p[1], Node) and p[1].type == 'array_literal':
                p[0] = p[1]
            elif p.slice[1].type == 'ID':
                p[0] = Node('factor', [Node('id', [], p[1], p.lineno(1), p.lexpos(1))], None, p.lineno(1), p.lexpos(1))
            else:
                p[0] = Node('factor', [p[1]], None, p.lineno(1), p.lexpos(1))
        elif len(p) == 3:  # Acceso a objeto
            id_node = Node('id', [], p[1], p.lineno(1), p.lexpos(1))
            id_node.children.append(p[2])
            p[0] = Node('factor', [id_node], None, p.lineno(1), p.lexpos(1))

    def p_llamada_metodo(self, p):
        '''llamada_metodo : ID PAREN_IZQ argumentos PAREN_DER
                         | ID acceso_objeto PAREN_IZQ argumentos PAREN_DER'''
        if len(p) == 5:
            p[0] = Node('llamada_metodo', [Node('id', [], p[1]), p[3]])
        else:
            id_node = Node('id', [], p[1])
            id_node.children.append(p[2])
            p[0] = Node('llamada_metodo', [id_node, p[4]])

    def p_array_literal(self, p):
        '''array_literal : CORCHETE_IZQ lista_expresiones CORCHETE_DER
                        | CORCHETE_IZQ CORCHETE_DER'''
        if len(p) == 4:
            p[0] = Node('array_literal', [p[2]])
        else:
            p[0] = Node('array_literal', [])  # Array vacío

    def p_empty(self, p):
        'empty :'
        p[0] = None

    def p_error(self, p):
        if p:
            # Obtener el contexto de tokens para dar un error más descriptivo
            expected_tokens = []
            
            # Intentar determinar qué tokens se esperaban
            if hasattr(self.parser, 'symstack'):
                state = self.parser.state
                try:
                    action = self.parser.action[state]
                    for token_type, next_state in action.items():
                        if next_state > 0:  # Solo consideramos acciones de shift
                            if token_type in self.tokens:
                                expected_tokens.append(token_type)
                except:
                    pass
            
            # Formatear mensaje de error
            error_msg = f"Error de sintaxis en '{p.value}' (línea {p.lineno}, columna {p.lexpos})"
            
            # Añadir información sobre tokens esperados si está disponible
            if expected_tokens:
                error_msg += f"\nSe esperaba uno de los siguientes: {', '.join(expected_tokens)}"
            
            # Casos especiales de errores comunes
            if p.type == 'ERROR' and p.value == '~':
                error_msg = f"Error: Espacio antes del carácter de terminación '~' en la línea {p.lineno}"
            elif p.type == 'CARAC_T' and p.lexpos > 0:
                error_msg = f"Error: Se encontró '{p.value}' en posición inesperada en la línea {p.lineno}"
            elif p.type == 'LLAVE_DER' and self.parser.symstack[-2].type == 'bloque':
                error_msg = f"Error: Posible falta de terminador '~' en alguna sentencia dentro del bloque (línea {p.lineno})"
            
            self.errors.append(error_msg)
            print(error_msg)
        else:
            error_msg = "Error de sintaxis al final del archivo. Posiblemente falta un terminador '~' o una llave de cierre '}'."
            self.errors.append(error_msg)
            print(error_msg)
            
    def parse(self):
        """Realiza el análisis sintáctico con los tokens proporcionados"""
        if not self.parser:
            self.build_parser()
        
        # Analizamos la entrada
        self.ast_root = self.parser.parse(lexer=self.lexer)
        
        # Mostramos resultados
        if not self.errors:
            print("Análisis sintáctico completado exitosamente.")
            if self.ast_root:
                print("\nÁrbol de derivación:")
                self.ast_root.print_tree()
            return True
        else:
            print("\nErrores encontrados durante el análisis sintáctico:")
            for error in self.errors:
                print(f"  - {error}")
            return False
    
    def _build_lexer_from_tokens(self):
        """Construye un objeto lexer compatible con PLY a partir de los tokens"""
        class CustomLexer:
            def __init__(self, tokens_list):
                self.tokens_list = tokens_list
                self.index = 0
                
                # Mapeos predefinidos de tokens
                self.token_map = {
                    TOK_TIPO_DATO: 'TIPO_DATO', TOK_ID: 'ID', TOK_NUM_ENTERO: 'NUM_ENTERO',
                    TOK_NUM_FLOTANTE: 'NUM_FLOTANTE', TOK_CADENA: 'CADENA', TOK_SUMA: 'SUMA',
                    TOK_RESTA: 'RESTA', TOK_MULT: 'MULT', TOK_DIV: 'DIV', TOK_MOD: 'MOD',
                    TOK_ASIG: 'ASIG', TOK_ASIG_SUMA: 'ASIG_SUMA', TOK_IGUAL: 'IGUAL',
                    TOK_DISTINTO: 'DISTINTO', TOK_MENOR_IGUAL: 'MENOR_IGUAL',
                    TOK_MAYOR_IGUAL: 'MAYOR_IGUAL', TOK_MENOR: 'MENOR', TOK_MAYOR: 'MAYOR',
                    TOK_AND: 'AND', TOK_OR: 'OR', TOK_NOT: 'NOT', TOK_CARAC_T: 'CARAC_T',
                    TOK_PUNTO_COMA: 'PUNTO_COMA', TOK_COMA: 'COMA', TOK_PUNTO: 'PUNTO',
                    TOK_DOS_PUNTOS: 'DOS_PUNTOS', TOK_CORCHETE_IZQ: 'CORCHETE_IZQ',
                    TOK_CORCHETE_DER: 'CORCHETE_DER', TOK_PAREN_IZQ: 'PAREN_IZQ',
                    TOK_PAREN_DER: 'PAREN_DER', TOK_LLAVE_IZQ: 'LLAVE_IZQ',
                    TOK_LLAVE_DER: 'LLAVE_DER', TOK_ERROR: 'ERROR'
                }
                
                # Mapeos de palabras reservadas
                self.palabras_reservadas = {
                    'principal': 'PRINCIPAL', 'clase': 'CLASE', 'publico': 'PUBLICO',
                    'privado': 'PRIVADO', 'retornar': 'RETORNAR', 'imprimir': 'IMPRIMIR',
                    'romper': 'ROMPER', 'cambio': 'CAMBIO', 'caso': 'CASO',
                    'predeterminado': 'PREDETERMINADO', 'verdadero': 'VERDADERO',
                    'falso': 'FALSO'
                }
                
                # Mapeos para ciclos y condicionales
                self.ciclos = {'mientras': 'MIENTRAS', 'hacer': 'HACER', 'para': 'PARA'}
                self.condicionales = {'si': 'SI', 'sino': 'SINO', 'caso': 'CASO'}
                
            def token(self):
                if self.index < len(self.tokens_list):
                    token_dict = self.tokens_list[self.index]
                    self.index += 1
                    
                    # Clase Token simplificada para PLY
                    class Token:
                        def __init__(self, tipo, valor, linea, lexpos):
                            self.type = tipo
                            self.value = valor
                            self.lineno = linea
                            self.lexpos = lexpos
                    
                    tipo_token = token_dict['tipo']
                    valor_token = token_dict['lexema']
                    linea = token_dict['linea']
                    columna = token_dict['columna']
                    
                    # Determinar el tipo de token para el parser
                    if tipo_token in self.token_map:
                        tipo_parser = self.token_map[tipo_token]
                    elif tipo_token == TOK_PAL_RES and valor_token in self.palabras_reservadas:
                        tipo_parser = self.palabras_reservadas[valor_token]
                    elif tipo_token == TOK_CICLO and valor_token in self.ciclos:
                        tipo_parser = self.ciclos[valor_token]
                    elif tipo_token == TOK_CONDICIONAL and valor_token in self.condicionales:
                        tipo_parser = self.condicionales[valor_token]
                    else:
                        tipo_parser = tipo_token
                    
                    return Token(tipo_parser, valor_token, linea, columna)
                return None
        
        return CustomLexer(self.tokens_list)

