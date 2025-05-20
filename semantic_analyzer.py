from syntax_analyzer import Node

class Symbol:
    def __init__(self, name, type, scope, line, column):
        self.name = name        # Nombre del símbolo
        self.type = type        # Tipo de dato
        self.scope = scope      # Ámbito (global, local, clase, etc.)
        self.line = line        # Línea donde se declaró
        self.column = column    # Columna donde se declaró
        self.is_initialized = False  # Si ha sido inicializada
        self.is_used = False    # Si ha sido utilizada

    def __str__(self):
        return f"{self.name} ({self.type}) en ámbito {self.scope}, línea {self.line}"

class SymbolTable:
    def __init__(self):
        self.symbols = {}       # Tabla de símbolos por ámbito
        self.current_scope = "global"
        
    def enter_scope(self, scope_name):
        """Entrar en un nuevo ámbito"""
        parent_scope = self.current_scope
        new_scope = f"{parent_scope}.{scope_name}"
        self.current_scope = new_scope
        if new_scope not in self.symbols:
            self.symbols[new_scope] = {}
        return new_scope
        
    def exit_scope(self):
        """Salir del ámbito actual y volver al ámbito padre"""
        if "." in self.current_scope:
            self.current_scope = self.current_scope.rsplit(".", 1)[0]
        return self.current_scope
        
    def add_symbol(self, name, type, line, column):
        """Añadir un símbolo a la tabla en el ámbito actual"""
        if name in self.symbols.get(self.current_scope, {}):
            return False  # El símbolo ya existe en este ámbito
        
        if self.current_scope not in self.symbols:
            self.symbols[self.current_scope] = {}
            
        self.symbols[self.current_scope][name] = Symbol(name, type, self.current_scope, line, column)
        return True
        
    def lookup(self, name):
        """Buscar un símbolo en el ámbito actual y en ámbitos superiores"""
        scope = self.current_scope
        
        while scope:
            if scope in self.symbols and name in self.symbols[scope]:
                return self.symbols[scope][name]
            
            # Subir al ámbito padre
            if "." in scope:
                scope = scope.rsplit(".", 1)[0]
            else:
                scope = None
                
        return None  # No se encontró el símbolo

class SemanticError:
    def __init__(self, message, line, column):
        self.message = message
        self.line = line
        self.column = column
        
    def __str__(self):
        return f"Error semántico en línea {self.line}, columna {self.column}: {self.message}"

class SemanticNode:
    """Nodo para el árbol de análisis semántico"""
    def __init__(self, type, value=None, data_type=None, children=None, line=0, column=0):
        self.type = type              # Tipo de nodo (declaración, asignación, etc.)
        self.value = value            # Valor del nodo (nombre de variable, valor literal, etc.)
        self.data_type = data_type    # Tipo de dato (entero, flotante, etc.)
        self.children = children if children else []
        self.line = line
        self.column = column
        self.errors = []              # Errores semánticos asociados a este nodo
        
    def add_child(self, child):
        """Añade un hijo al nodo"""
        if child:
            self.children.append(child)
            
    def add_error(self, message):
        """Añade un error semántico al nodo"""
        self.errors.append(SemanticError(message, self.line, self.column))
        
    def __str__(self, level=0, is_last=False):
        """Representación en texto del nodo para visualización"""
        # Prefijo para el nivel actual (espacios o líneas verticales)
        prefix = ""
        for i in range(level):
            if i == level - 1:
                prefix += "└── " if is_last else "├── "
            else:
                prefix += "    " if i < level - 1 else "│   "
        
        # Nodo actual
        ret = prefix + self.type
        if self.value is not None:
            ret += f": {self.value}"
        if self.data_type:
            ret += f" [{self.data_type}]"
        ret += "\n"
        
        # Procesar hijos
        num_children = len(self.children)
        for i, child in enumerate(self.children):
            is_last_child = (i == num_children - 1)
            ret += child.__str__(level + 1, is_last_child)
        
        return ret
        
    def print_tree(self):
        """Imprime el árbol desde la raíz"""
        print(self.__str__(0, True))
        
    def collect_errors(self):
        """Recopila todos los errores en este nodo y sus hijos"""
        all_errors = list(self.errors)
        
        for child in self.children:
            all_errors.extend(child.collect_errors())
            
        return all_errors

class SemanticAnalyzer:
    def __init__(self):
        self.symbol_table = SymbolTable()
        self.errors = []
        self.warnings = []
        self.semantic_trees = []  # Lista de árboles semánticos generados
        self.user_defined_types = {}  # Diccionario de tipos definidos por el usuario
        
        # Definir tipos de datos básicos del lenguaje
        self.basic_types = ["entero", "flotante", "booleano", "caracter", "cadena", "vacio"]
        
        # Tabla simplificada de compatibilidad de tipos para operaciones
        self.type_compatibility = {
            # Operaciones aritméticas
            "+": {
                "entero": {"entero": "entero", "flotante": "flotante"},
                "flotante": {"entero": "flotante", "flotante": "flotante"},
                "cadena": {"cadena": "cadena"}
            },
            "-": {"entero": {"entero": "entero", "flotante": "flotante"},
                 "flotante": {"entero": "flotante", "flotante": "flotante"}},
            "*": {"entero": {"entero": "entero", "flotante": "flotante"},
                 "flotante": {"entero": "flotante", "flotante": "flotante"}},
            "/": {"entero": {"entero": "flotante", "flotante": "flotante"},
                 "flotante": {"entero": "flotante", "flotante": "flotante"}},
            "%": {"entero": {"entero": "entero"}},
            
            # Operaciones relacionales (todas retornan booleano)
            "==": {"entero": {"entero": "booleano", "flotante": "booleano"},
                  "flotante": {"entero": "booleano", "flotante": "booleano"},
                  "booleano": {"booleano": "booleano"},
                  "cadena": {"cadena": "booleano"},
                  "caracter": {"caracter": "booleano"}},
            "!=": {"entero": {"entero": "booleano", "flotante": "booleano"},
                  "flotante": {"entero": "booleano", "flotante": "booleano"},
                  "booleano": {"booleano": "booleano"},
                  "cadena": {"cadena": "booleano"},
                  "caracter": {"caracter": "booleano"}},
            "<": {"entero": {"entero": "booleano", "flotante": "booleano"},
                 "flotante": {"entero": "booleano", "flotante": "booleano"}},
            ">": {"entero": {"entero": "booleano", "flotante": "booleano"},
                 "flotante": {"entero": "booleano", "flotante": "booleano"}},
            "<=": {"entero": {"entero": "booleano", "flotante": "booleano"},
                  "flotante": {"entero": "booleano", "flotante": "booleano"}},
            ">=": {"entero": {"entero": "booleano", "flotante": "booleano"},
                  "flotante": {"entero": "booleano", "flotante": "booleano"}},
            
            # Operadores lógicos
            "AND": {"booleano": {"booleano": "booleano"}},
            "OR": {"booleano": {"booleano": "booleano"}},
            "NOT": {"booleano": "booleano"}
        }
    
    def analyze(self, ast_root):
        """Analiza el árbol sintáctico y realiza verificaciones semánticas"""
        if not ast_root:
            return True
            
        # Reiniciar el estado
        self.symbol_table = SymbolTable()
        self.errors = []
        self.warnings = []
        self.semantic_trees = []
        self.user_defined_types = {}
        
        # Primera pasada: recopilar declaraciones de clases
        self._collect_class_declarations(ast_root)
        
        # Realizar el análisis semántico
        semantic_root = self._analyze_node(ast_root)
        if semantic_root:
            self.semantic_trees.append(semantic_root)
            
            # Recopilar errores de todos los nodos del árbol
            self.errors = semantic_root.collect_errors()
        
        # Verificar variables no utilizadas (como advertencia)
        self._check_unused_variables()
        
        return len(self.errors) == 0
    
    def _check_unused_variables(self):
        """Verifica si hay variables declaradas pero no utilizadas y genera advertencias"""
        for scope, symbols in self.symbol_table.symbols.items():
            for name, symbol in symbols.items():
                if not symbol.is_used:
                    self.warnings.append(
                        SemanticError(f"La variable '{name}' está declarada pero nunca se utiliza", 
                                     symbol.line, symbol.column)
                    )
    
    def _collect_class_declarations(self, node):
        """Recopila las declaraciones de clases para registrarlas como tipos definidos por el usuario"""
        if not hasattr(node, 'type'):
            return
            
        if node.type == "declaracion_clase" and node.leaf:
            # Registrar la clase como un tipo definido por el usuario
            class_name = node.leaf
            self.user_defined_types[class_name] = {
                "members": {},
                "methods": {}
            }
            
            # Analizar miembros y métodos de la clase
            self._process_class_members(class_name, node)
            
        elif node.type == "declaraciones_clases":
            # Procesar cada declaración de clase
            for child in node.children:
                self._collect_class_declarations(child)
        
        # Procesar recursivamente los hijos
        elif hasattr(node, 'children'):
            for child in node.children:
                if child:
                    self._collect_class_declarations(child)
    
    def _process_class_members(self, class_name, node):
        """Procesa los miembros y métodos de una clase"""
        if len(node.children) < 1:
            return
            
        members_node = node.children[0]
        if not members_node or members_node.type != "miembros_clase":
            return
            
        for member in members_node.children:
            if member.type != "miembro_clase" or len(member.children) < 2:
                continue
                
            # Obtener el modificador de acceso y la declaración
            access_modifier = member.children[0].leaf if member.children[0].type == "modificador_acceso" else "publico"
            declaration = member.children[1]
            
            # Procesar según el tipo de declaración
            if declaration.type == "declaracion_variable":
                self._process_class_variable(class_name, declaration)
            elif declaration.type == "declaracion_metodo":
                self._process_class_method(class_name, declaration)
    
    def _process_class_variable(self, class_name, declaration):
        """Procesa una declaración de variable dentro de una clase"""
        if len(declaration.children) < 2:
            return
            
        tipo = declaration.children[0].leaf
        
        # Manejar lista de IDs o un solo ID
        if declaration.children[1].type == "lista_ids":
            for id_node in declaration.children[1].children:
                if id_node.type == "id":
                    self.user_defined_types[class_name]["members"][id_node.leaf] = tipo
        elif declaration.children[1].type == "id":
            self.user_defined_types[class_name]["members"][declaration.children[1].leaf] = tipo
    
    def _process_class_method(self, class_name, declaration):
        """Procesa una declaración de método dentro de una clase"""
        if len(declaration.children) < 2:
            return
            
        return_type = declaration.children[0].leaf
        method_name = declaration.children[1].leaf
        
        # Crear entrada para el método
        self.user_defined_types[class_name]["methods"][method_name] = {
            "return_type": return_type,
            "parameters": []
        }
        
        # Procesar parámetros si existen
        if len(declaration.children) >= 3 and declaration.children[2].type == "parametros":
            params_node = declaration.children[2]
            for param_node in params_node.children:
                if param_node.type == "lista_parametros" and len(param_node.children) >= 2:
                    self.user_defined_types[class_name]["methods"][method_name]["parameters"].append({
                        "type": param_node.children[0].leaf,
                        "name": param_node.children[1].leaf
                    })
    
    def _analyze_node(self, node):
        """Analiza un nodo del AST recursivamente y genera un nodo semántico"""
        if not hasattr(node, 'type'):
            return None
            
        # Crear un nodo semántico base
        semantic_node = SemanticNode(node.type, value=node.leaf, line=node.line, column=node.column)
        
        # Manejar tipos de nodos específicos
        if node.type == "programa":
            self._process_children(node, semantic_node)
            
        elif node.type == "principal":
            # Entrar en el ámbito de la función principal
            self.symbol_table.enter_scope("principal")
            self._process_children(node, semantic_node)
            self.symbol_table.exit_scope()
            
        elif node.type == "id":
            # Buscar el identificador en la tabla de símbolos
            symbol = self.symbol_table.lookup(node.leaf)
            if symbol:
                semantic_node.data_type = symbol.type
                symbol.is_used = True
            
        elif node.type == "acceso_objeto":
            # Analizar acceso a miembro de objeto
            if len(node.children) >= 1:
                id_node = self._analyze_node(node.children[0])
                semantic_node.add_child(id_node)
                
                # Verificar si el objeto es de un tipo definido por el usuario
                object_type = id_node.data_type if id_node else None
                if object_type in self.user_defined_types and len(node.children) >= 2:
                    member_name = node.children[1].leaf if hasattr(node.children[1], 'leaf') else None
                    if member_name:
                        # Verificar si el miembro existe en la clase
                        if member_name in self.user_defined_types[object_type]["members"]:
                            semantic_node.data_type = self.user_defined_types[object_type]["members"][member_name]
                        else:
                            self._add_error(semantic_node, f"La clase '{object_type}' no tiene un miembro llamado '{member_name}'")
                elif object_type:
                    self._add_error(semantic_node, f"No se puede acceder a miembros de un objeto de tipo '{object_type}'")
            
        elif node.type == "factor" and len(node.children) == 1 and node.children[0].type == "id":
            # Caso especial para factor que contiene un id
            id_node = self._analyze_node(node.children[0])
            semantic_node.add_child(id_node)
            if id_node and id_node.data_type:
                semantic_node.data_type = id_node.data_type
                
        elif node.type == "factor" and node.leaf is not None:
            # Determinar el tipo de dato del factor basado en su valor
            self._infer_data_type(semantic_node, node.leaf)
            
        elif node.type == "llamada_metodo":
            self._analyze_method_call(node, semantic_node)
            
        elif node.type == "booleano":
            semantic_node.data_type = "booleano"
            
        elif node.type in ["bloque", "sentencias", "sentencia"]:
            self._process_children(node, semantic_node)
                
        elif node.type == "declaracion_variable":
            return self._analyze_declaration(node)
            
        elif node.type == "asignacion":
            return self._analyze_assignment(node)
            
        elif node.type == "expresion_aritmetica":
            return self._analyze_arithmetic_expression(node)
            
        elif node.type == "expresion_relacional":
            return self._analyze_relational_expression(node)
            
        elif node.type == "expresion_logica":
            return self._analyze_logical_expression(node)
            
        elif node.type == "sentencia_if":
            return self._analyze_if_statement(node)
            
        elif node.type == "sentencia_while":
            return self._analyze_while_statement(node)
            
        elif node.type == "sentencia_for":
            return self._analyze_for_statement(node)
            
        elif node.type == "llamada_funcion":
            return self._analyze_function_call(node)
            
        elif node.type == "sentencia_print":
            return self._analyze_print_statement(node)
            
        # Por defecto, procesar los hijos
        elif node.children:
            self._process_children(node, semantic_node)
            
        return semantic_node
    
    def _process_children(self, node, semantic_node):
        """Procesa recursivamente los hijos de un nodo"""
        for child in node.children:
            if child:  # Asegurarse de que el hijo no es None
                child_node = self._analyze_node(child)
                if child_node:
                    semantic_node.add_child(child_node)
    
    def _infer_data_type(self, semantic_node, value):
        """Infiere el tipo de dato basado en un valor"""
        if isinstance(value, int):
            semantic_node.data_type = "entero"
        elif isinstance(value, float):
            semantic_node.data_type = "flotante"
        elif isinstance(value, str):
            if value.startswith('"') or value.startswith("'"):
                semantic_node.data_type = "cadena"
            elif value.lower() in ["verdadero", "falso"]:
                semantic_node.data_type = "booleano"
            else:
                # Intentar convertir a número si es posible
                try:
                    float_val = float(value)
                    if '.' in value:
                        semantic_node.data_type = "flotante"
                    else:
                        semantic_node.data_type = "entero"
                except ValueError:
                    # Si no es un número, puede ser un identificador
                    symbol = self.symbol_table.lookup(value)
                    if symbol:
                        semantic_node.data_type = symbol.type
    
    def _add_error(self, node, message):
        """Añade un error al nodo y a la lista global de errores"""
        self.errors.append(SemanticError(message, node.line, node.column))
        node.add_error(message)
        
    def _analyze_method_call(self, node, semantic_node):
        """Analiza una llamada a método"""
        if len(node.children) >= 1:
            obj_node = self._analyze_node(node.children[0])
            semantic_node.add_child(obj_node)
            
            # Verificar si el objeto tiene un acceso a objeto
            if obj_node and obj_node.type == "id" and len(obj_node.children) >= 1 and obj_node.children[0].type == "acceso_objeto":
                obj_type = obj_node.data_type
                method_name = obj_node.children[0].children[0].value if len(obj_node.children[0].children) >= 1 else None
                
                if obj_type in self.user_defined_types and method_name:
                    # Verificar si el método existe en la clase
                    if method_name in self.user_defined_types[obj_type]["methods"]:
                        method_info = self.user_defined_types[obj_type]["methods"][method_name]
                        semantic_node.data_type = method_info["return_type"]
                        
                        # Verificar argumentos si hay
                        if len(node.children) >= 2 and node.children[1].type == "argumentos":
                            # Aquí se podría implementar la verificación de tipos de argumentos
                            pass
                    else:
                        self._add_error(semantic_node, f"La clase '{obj_type}' no tiene un método llamado '{method_name}'")
        
    def _analyze_declaration(self, node):
        """Analiza una declaración de variable y genera un nodo semántico"""
        semantic_node = SemanticNode("declaracion_variable", line=node.line, column=node.column)
        
        # Obtener el tipo de dato
        tipo_dato_node = node.children[0]
        tipo = tipo_dato_node.leaf
        
        # Verificar si es un tipo válido
        if tipo not in self.basic_types and not self._is_user_defined_type(tipo):
            error_msg = f"Tipo de dato '{tipo}' no definido"
            self.errors.append(
                SemanticError(error_msg, 
                             tipo_dato_node.line if hasattr(tipo_dato_node, 'line') else 0,
                             tipo_dato_node.column if hasattr(tipo_dato_node, 'column') else 0)
            )
            semantic_node.add_error(error_msg)
            return semantic_node
            
        # Añadir el tipo al nodo semántico
        tipo_node = SemanticNode("tipo_dato", value=tipo, line=tipo_dato_node.line, column=tipo_dato_node.column)
        semantic_node.add_child(tipo_node)
            
        # Procesar la lista de identificadores
        if len(node.children) >= 2:
            if node.children[1].type == "lista_ids":
                # Declaración simple: tipo id1, id2, ...
                ids_node = SemanticNode("lista_ids", line=node.children[1].line, column=node.children[1].column)
                semantic_node.add_child(ids_node)
                
                for id_node in node.children[1].children:
                    nombre = id_node.leaf
                    linea = id_node.line if hasattr(id_node, 'line') else 0
                    columna = id_node.column if hasattr(id_node, 'column') else 0
                    
                    var_node = SemanticNode("variable", value=nombre, data_type=tipo, line=linea, column=columna)
                    ids_node.add_child(var_node)
                    
                    # Verificar si ya existe en el ámbito actual
                    if not self.symbol_table.add_symbol(nombre, tipo, linea, columna):
                        error_msg = f"Variable '{nombre}' ya declarada en este ámbito"
                        self.errors.append(SemanticError(error_msg, linea, columna))
                        var_node.add_error(error_msg)
                    
            elif len(node.children) >= 3 and node.children[1].type == "id":
                # Declaración con inicialización: tipo id = expresion
                nombre = node.children[1].leaf
                linea = node.children[1].line if hasattr(node.children[1], 'line') else 0
                columna = node.children[1].column if hasattr(node.children[1], 'column') else 0
                
                var_node = SemanticNode("variable", value=nombre, data_type=tipo, line=linea, column=columna)
                semantic_node.add_child(var_node)
                
                # Verificar si ya existe en el ámbito actual
                if not self.symbol_table.add_symbol(nombre, tipo, linea, columna):
                    error_msg = f"Variable '{nombre}' ya declarada en este ámbito"
                    self.errors.append(SemanticError(error_msg, linea, columna))
                    var_node.add_error(error_msg)
                else:
                    # Marcar como inicializada
                    symbol = self.symbol_table.lookup(nombre)
                    if symbol:
                        symbol.is_initialized = True
                        
                    # Verificar compatibilidad de tipos en la inicialización
                    if len(node.children) >= 3:
                        expr_node = self._analyze_node(node.children[2])
                        
                        # Inferencia de tipos para literales
                        if expr_node and expr_node.type == "factor" and expr_node.value is not None:
                            if isinstance(expr_node.value, int) or (
                                isinstance(expr_node.value, str) and 
                                expr_node.value.isdigit()
                            ):
                                expr_node.data_type = "entero"
                            elif isinstance(expr_node.value, float) or (
                                isinstance(expr_node.value, str) and 
                                '.' in expr_node.value and 
                                all(c.isdigit() or c == '.' for c in expr_node.value)
                            ):
                                expr_node.data_type = "flotante"
                            elif isinstance(expr_node.value, str) and (
                                expr_node.value.startswith('"') or 
                                expr_node.value.startswith("'")
                            ):
                                expr_node.data_type = "cadena"
                            elif expr_node.value in ["verdadero", "falso"]:
                                expr_node.data_type = "booleano"
                                
                        expr_type = expr_node.data_type if expr_node else None
                        
                        # Añadir la expresión al nodo semántico
                        if expr_node:
                            semantic_node.add_child(expr_node)
                        
                        if expr_type and expr_type != tipo:
                            # Permitir asignaciones compatibles (entero a flotante, etc.)
                            is_compatible = False
                            
                            if tipo == "flotante" and expr_type == "entero":
                                is_compatible = True
                            elif tipo == expr_type:
                                is_compatible = True
                            
                            if not is_compatible:
                                error_msg = f"No se puede asignar un valor de tipo '{expr_type}' a una variable de tipo '{tipo}'"
                                self.errors.append(SemanticError(error_msg, linea, columna))
                                var_node.add_error(error_msg)
        
        return semantic_node
    
    def _analyze_assignment(self, node):
        """Analiza una asignación y genera un nodo semántico"""
        semantic_node = SemanticNode("asignacion", line=node.line, column=node.column)
        
        # Obtener el identificador
        id_node = node.children[0]
        
        if id_node.type == "id":
            nombre = id_node.leaf
            linea = id_node.line if hasattr(id_node, 'line') else 0
            columna = id_node.column if hasattr(id_node, 'column') else 0
            
            # Verificar si es una asignación a un miembro de objeto (p.nombre = "Juan")
            if len(id_node.children) > 0 and id_node.children[0].type == "acceso_objeto":
                # Es una asignación a un miembro de objeto
                var_node = SemanticNode("variable", value=nombre, line=linea, column=columna)
                semantic_node.add_child(var_node)
                
                # Verificar si la variable (objeto) está declarada
                symbol = self.symbol_table.lookup(nombre)
                if not symbol:
                    error_msg = f"Variable '{nombre}' no declarada"
                    self.errors.append(SemanticError(error_msg, linea, columna))
                    var_node.add_error(error_msg)
                    return semantic_node
                
                # Establecer el tipo de la variable en el nodo semántico
                var_node.data_type = symbol.type
                
                # Marcar la variable como inicializada y utilizada
                symbol.is_initialized = True
                symbol.is_used = True
                
                # Obtener el acceso al miembro
                acceso_obj = id_node.children[0]
                member_name = acceso_obj.children[0].leaf if len(acceso_obj.children) > 0 else None
                
                # Verificar si el tipo es una clase definida por el usuario
                if symbol.type in self.user_defined_types and member_name:
                    # Verificar si el miembro existe en la clase
                    if member_name in self.user_defined_types[symbol.type]["members"]:
                        member_type = self.user_defined_types[symbol.type]["members"][member_name]
                        
                        # Analizar la expresión a asignar
                        expr_node = self._analyze_node(node.children[1])
                        expr_type = expr_node.data_type if expr_node else None
                        
                        # Añadir la expresión al nodo semántico
                        if expr_node:
                            semantic_node.add_child(expr_node)
                        
                        # Verificar compatibilidad de tipos para la asignación al miembro
                        if expr_type and expr_type != member_type:
                            # Permitir asignaciones compatibles (entero a flotante, etc.)
                            is_compatible = False
                            
                            if member_type == "flotante" and expr_type == "entero":
                                is_compatible = True
                            elif member_type == expr_type:
                                is_compatible = True
                            
                            if not is_compatible:
                                error_msg = f"No se puede asignar un valor de tipo '{expr_type}' al miembro '{member_name}' de tipo '{member_type}'"
                                self.errors.append(SemanticError(error_msg, linea, columna))
                                semantic_node.add_error(error_msg)
                    else:
                        error_msg = f"La clase '{symbol.type}' no tiene un miembro llamado '{member_name}'"
                        self.errors.append(SemanticError(error_msg, linea, columna))
                        semantic_node.add_error(error_msg)
                else:
                    error_msg = f"El tipo '{symbol.type}' no es una clase definida o no tiene miembros"
                    self.errors.append(SemanticError(error_msg, linea, columna))
                    semantic_node.add_error(error_msg)
                    
                return semantic_node
            
            # Es una asignación normal a una variable
            var_node = SemanticNode("variable", value=nombre, line=linea, column=columna)
            semantic_node.add_child(var_node)
            
            # Verificar si la variable está declarada
            symbol = self.symbol_table.lookup(nombre)
            if not symbol:
                error_msg = f"Variable '{nombre}' no declarada"
                self.errors.append(SemanticError(error_msg, linea, columna))
                var_node.add_error(error_msg)
                return semantic_node
            
            # Establecer el tipo de la variable en el nodo semántico
            var_node.data_type = symbol.type
                
            # Marcar la variable como inicializada y utilizada
            symbol.is_initialized = True
            symbol.is_used = True
            
            # Verificar compatibilidad de tipos
            expr_node = self._analyze_node(node.children[1])
            expr_type = expr_node.data_type if expr_node else None
            
            # Añadir la expresión al nodo semántico
            if expr_node:
                semantic_node.add_child(expr_node)
            
            # Verificar asignación a tipos definidos por el usuario
            if symbol.type in self.user_defined_types:
                # Si es un tipo definido por el usuario, solo permitir asignaciones de objetos del mismo tipo
                if expr_type != symbol.type:
                    error_msg = f"No se puede asignar un valor de tipo '{expr_type}' a una variable de tipo '{symbol.type}'"
                    self.errors.append(SemanticError(error_msg, linea, columna))
                    semantic_node.add_error(error_msg)
            elif expr_type and expr_type != symbol.type:
                # Para tipos básicos, verificar compatibilidad normal
                # Permitir asignaciones compatibles (entero a flotante, etc.)
                is_compatible = False
                
                if symbol.type == "flotante" and expr_type == "entero":
                    is_compatible = True
                elif symbol.type == expr_type:
                    is_compatible = True
                
                if not is_compatible:
                    error_msg = f"No se puede asignar un valor de tipo '{expr_type}' a una variable de tipo '{symbol.type}'"
                    self.errors.append(SemanticError(error_msg, linea, columna))
                    semantic_node.add_error(error_msg)
            
            return semantic_node
        
        # Para otros tipos de asignación (acceso a arrays, etc.)
        return semantic_node
    
    def _analyze_binary_operation(self, node, left_node, right_node, operator, operation_type):
        """Analiza una operación binaria y verifica la compatibilidad de tipos"""
        semantic_node = SemanticNode(operation_type, value=operator, line=node.line, column=node.column)
        
        # Añadir los operandos al nodo semántico
        if left_node:
            semantic_node.add_child(left_node)
        if right_node:
            semantic_node.add_child(right_node)
            
        left_type = left_node.data_type if left_node else None
        right_type = right_node.data_type if right_node else None
        
        # Verificar compatibilidad de tipos según el operador
        if operation_type == "expresion_aritmetica":
            self._check_arithmetic_compatibility(semantic_node, left_type, right_type, operator)
        elif operation_type == "expresion_relacional":
            semantic_node.data_type = "booleano"  # Las expresiones relacionales siempre devuelven booleano
            self._check_relational_compatibility(semantic_node, left_type, right_type, operator)
        elif operation_type == "expresion_logica":
            semantic_node.data_type = "booleano"  # Las expresiones lógicas siempre devuelven booleano
            self._check_logical_compatibility(semantic_node, left_type, right_type, operator)
            
        return semantic_node
        
    def _check_arithmetic_compatibility(self, node, left_type, right_type, operator):
        """Verifica la compatibilidad de tipos para operaciones aritméticas"""
        # Caso en que falta información de tipos
        if left_type is None and right_type is None:
            node.data_type = "entero"  # Por defecto asumimos entero
            return
        elif left_type is None:
            node.data_type = right_type
            return
        elif right_type is None:
            node.data_type = left_type
            return
            
        # Verificar si la operación es compatible según la tabla de compatibilidad
        if (operator in self.type_compatibility and 
            left_type in self.type_compatibility[operator] and 
            right_type in self.type_compatibility[operator][left_type]):
            node.data_type = self.type_compatibility[operator][left_type][right_type]
        else:
            self._add_error(node, f"Operación '{operator}' no compatible entre tipos '{left_type}' y '{right_type}'")
    
    def _check_relational_compatibility(self, node, left_type, right_type, operator):
        """Verifica la compatibilidad de tipos para operaciones relacionales"""
        if left_type and right_type:
            if operator in ["==", "!="]:
                # Igualdad y desigualdad funcionan con cualquier par de tipos iguales
                if left_type != right_type:
                    self._add_error(node, f"Comparación '{operator}' no compatible entre tipos diferentes '{left_type}' y '{right_type}'")
            elif operator in [">", "<", ">=", "<="]:
                # Comparaciones de orden solo funcionan con tipos numéricos
                if left_type not in ["entero", "flotante"] or right_type not in ["entero", "flotante"]:
                    self._add_error(node, f"Comparación '{operator}' requiere operandos numéricos")
    
    def _check_logical_compatibility(self, node, left_type, right_type, operator):
        """Verifica la compatibilidad de tipos para operaciones lógicas"""
        if left_type and right_type:
            if left_type != "booleano" or right_type != "booleano":
                self._add_error(node, f"Operador '{operator}' requiere operandos de tipo booleano")
    
    def _analyze_arithmetic_expression(self, node):
        """Analiza una expresión aritmética y devuelve un nodo semántico"""
        if len(node.children) == 1:
            # Es un término simple
            child_node = self._analyze_node(node.children[0])
            if child_node:
                semantic_node = SemanticNode("expresion_aritmetica", line=node.line, column=node.column)
                semantic_node.add_child(child_node)
                semantic_node.data_type = child_node.data_type
                return semantic_node
            
        elif len(node.children) == 2 and node.leaf == "-":
            # Es una operación unaria (negación)
            operand_node = self._analyze_node(node.children[1])
            if operand_node:
                semantic_node = SemanticNode("expresion_aritmetica", value=node.leaf, line=node.line, column=node.column)
                semantic_node.add_child(operand_node)
                
                # Verificar compatibilidad con operador unario
                if operand_node.data_type in ["entero", "flotante"]:
                    semantic_node.data_type = operand_node.data_type
                else:
                    self._add_error(semantic_node, f"Operador '-' no aplicable a tipo '{operand_node.data_type}'")
                return semantic_node
            
        elif len(node.children) >= 2:
            # Es una operación binaria
            left_node = self._analyze_node(node.children[0])
            right_node = self._analyze_node(node.children[1])
            return self._analyze_binary_operation(node, left_node, right_node, node.leaf, "expresion_aritmetica")
                
        # Por defecto
        return SemanticNode("expresion_aritmetica", line=node.line, column=node.column)
    
    def _analyze_relational_expression(self, node):
        """Analiza una expresión relacional y devuelve un nodo semántico"""
        if len(node.children) == 1:
            # Es una expresión aritmética simple
            child_node = self._analyze_node(node.children[0])
            if child_node:
                semantic_node = SemanticNode("expresion_relacional", line=node.line, column=node.column)
                semantic_node.add_child(child_node)
                semantic_node.data_type = child_node.data_type
                return semantic_node
            
        elif len(node.children) >= 2:
            # Es una comparación
            left_node = self._analyze_node(node.children[0])
            right_node = self._analyze_node(node.children[1])
            return self._analyze_binary_operation(node, left_node, right_node, node.leaf, "expresion_relacional")
                
        # Por defecto
        return SemanticNode("expresion_relacional", line=node.line, column=node.column)
    
    def _analyze_logical_expression(self, node):
        """Analiza una expresión lógica y devuelve un nodo semántico"""
        if len(node.children) == 1:
            # Es una expresión relacional simple
            child_node = self._analyze_node(node.children[0])
            if child_node:
                semantic_node = SemanticNode("expresion_logica", line=node.line, column=node.column)
                semantic_node.add_child(child_node)
                semantic_node.data_type = child_node.data_type
                
                # Si es una expresión relacional, el resultado es booleano
                if child_node.type == "expresion_relacional":
                    semantic_node.data_type = "booleano"
                return semantic_node
            
        elif node.leaf == "NOT" and len(node.children) >= 1:
            # Es una negación
            operand_node = self._analyze_node(node.children[0])
            if operand_node:
                semantic_node = SemanticNode("expresion_logica", value=node.leaf, line=node.line, column=node.column)
                semantic_node.add_child(operand_node)
                
                if operand_node.data_type == "booleano":
                    semantic_node.data_type = "booleano"
                else:
                    self._add_error(semantic_node, f"Operador 'NOT' requiere un operando de tipo booleano, se encontró '{operand_node.data_type}'")
                return semantic_node
            
        elif len(node.children) >= 2:
            # Es una operación lógica binaria (AND, OR)
            left_node = self._analyze_node(node.children[0])
            right_node = self._analyze_node(node.children[1])
            return self._analyze_binary_operation(node, left_node, right_node, node.leaf, "expresion_logica")
                
        # Por defecto
        return SemanticNode("expresion_logica", line=node.line, column=node.column)
    
    def _check_boolean_condition(self, node, condition_node, structure_name):
        """Verifica que una condición sea de tipo booleano"""
        # Si la condición es una expresión relacional, es de tipo booleano
        if condition_node.type == "expresion_relacional":
            condition_node.data_type = "booleano"
        
        condition_type = condition_node.data_type
        
        if condition_type and condition_type != "booleano":
            error_msg = f"La condición de la sentencia '{structure_name}' debe ser de tipo booleano, se encontró '{condition_type}'"
            self._add_error(node, error_msg)
            
    def _analyze_if_statement(self, node):
        """Analiza una sentencia if y genera un nodo semántico"""
        semantic_node = SemanticNode("sentencia_if", line=node.line, column=node.column)
        
        # Verificar que la condición sea de tipo booleano
        if len(node.children) >= 1:
            condition_node = self._analyze_node(node.children[0])
            if condition_node:
                semantic_node.add_child(condition_node)
                self._check_boolean_condition(semantic_node, condition_node, "if")
        
        # Procesar los bloques then y else
        for i in range(1, len(node.children)):
            child_node = self._analyze_node(node.children[i])
            if child_node:
                semantic_node.add_child(child_node)
                
        return semantic_node
    
    def _analyze_while_statement(self, node):
        """Analiza una sentencia while y genera un nodo semántico"""
        semantic_node = SemanticNode("sentencia_while", line=node.line, column=node.column)
        
        # Verificar que la condición sea de tipo booleano
        if len(node.children) >= 1:
            condition_node = self._analyze_node(node.children[0])
            if condition_node:
                semantic_node.add_child(condition_node)
                self._check_boolean_condition(semantic_node, condition_node, "while")
        
        # Analizar el bloque del ciclo
        if len(node.children) >= 2:
            body_node = self._analyze_node(node.children[1])
            if body_node:
                semantic_node.add_child(body_node)
                
        return semantic_node
    
    def _analyze_for_statement(self, node):
        """Analiza una sentencia for y genera un nodo semántico"""
        semantic_node = SemanticNode("sentencia_for", line=node.line, column=node.column)
        
        # Procesar componentes del for (inicialización, condición, actualización, bloque)
        for i, component in enumerate(node.children[:min(4, len(node.children))]):
            child_node = self._analyze_node(component)
            if child_node:
                semantic_node.add_child(child_node)
                
                # Verificar que la condición (índice 1) sea de tipo booleano
                if i == 1:
                    self._check_boolean_condition(semantic_node, child_node, "for")
                
        return semantic_node
    
    def _analyze_function_call(self, node):
        """Analiza una llamada a función y genera un nodo semántico"""
        semantic_node = SemanticNode("llamada_funcion", line=node.line, column=node.column)
        
        # Obtener el nombre de la función
        if len(node.children) >= 1 and node.children[0].type == "id":
            function_name = node.children[0].leaf
            
            # Procesar el identificador de la función
            function_node = SemanticNode("id", value=function_name, line=node.children[0].line, column=node.children[0].column)
            semantic_node.add_child(function_node)
            
            # Verificar si la función está definida
            symbol = self.symbol_table.lookup(function_name)
            if not symbol:
                self._add_error(semantic_node, f"Función '{function_name}' no declarada")
            else:
                semantic_node.data_type = symbol.type
            
            # Procesar los argumentos si existen
            if len(node.children) >= 2:
                args_node = self._analyze_node(node.children[1])
                if args_node:
                    semantic_node.add_child(args_node)
            
        return semantic_node
    
    def _analyze_print_statement(self, node):
        """Analiza una sentencia print y genera un nodo semántico"""
        semantic_node = SemanticNode("sentencia_print", line=node.line, column=node.column)
        
        # Procesar los hijos (expresión a imprimir)
        self._process_children(node, semantic_node)
                
        return semantic_node
    
    def _is_user_defined_type(self, tipo):
        """Verifica si un tipo es definido por el usuario (clase)"""
        return tipo in self.user_defined_types
    
    def print_errors(self):
        """Imprime todos los errores semánticos encontrados"""
        if self.errors:
            print("\nErrores semánticos encontrados:")
            for error in self.errors:
                print(f"  - {error}")
        else:
            print("\nNo se encontraron errores semánticos.")
            
    def print_warnings(self):
        """Imprime todas las advertencias semánticas encontradas"""
        if self.warnings:
            print("\nAdvertencias semánticas:")
            for warning in self.warnings:
                print(f"  - {warning}")
                
    def print_semantic_trees(self):
        """Imprime los árboles de análisis semántico"""
        if self.semantic_trees:
            print("\nÁrboles de análisis semántico:")
            for i, tree in enumerate(self.semantic_trees):
                print(f"\nÁrbol semántico {i+1}:")
                tree.print_tree()
        else:
            print("\nNo se generaron árboles de análisis semántico.") 
            