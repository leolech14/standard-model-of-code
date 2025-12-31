"""
Atom Definitions
================

Canonical list of all known atoms in the taxonomy.
This is the SINGLE SOURCE OF TRUTH for atom definitions.

Structure: List of tuples:
(id, name, ast_types, continent, fundamental, level, description, detection_rule)
"""

# =============================================================================
# DATA FOUNDATIONS (Cyan) — IDs 1-20
# =============================================================================

BITS = [
    (1, "BitFlag", ["binary_expression"], "Data Foundations", "Bits", "atom",
     "Bit operation with mask", "bit operation + constant mask"),
    (2, "BitMask", ["binary_literal"], "Data Foundations", "Bits", "atom",
     "Binary literal value", "binary literal 0b..."),
]

PRIMITIVES = [
    (5, "Boolean", ["true", "false"], "Data Foundations", "Primitives", "atom",
     "Boolean true/false value", "type bool"),
    (6, "Integer", ["integer"], "Data Foundations", "Primitives", "atom",
     "Integer numeric value", "integer type"),
    (7, "Float", ["float"], "Data Foundations", "Primitives", "atom",
     "Floating point value", "float type"),
    (8, "StringLiteral", ["string", "concatenated_string"], "Data Foundations", "Primitives", "atom",
     "String literal value", "string literal"),
    (9, "NoneLiteral", ["none"], "Data Foundations", "Primitives", "atom",
     "None/null value", "None/null literal"),
    (10, "ListLiteral", ["list"], "Data Foundations", "Primitives", "atom",
     "List literal []", "list brackets"),
    (11, "DictLiteral", ["dictionary"], "Data Foundations", "Primitives", "atom",
     "Dictionary literal {}", "dict braces"),
    (12, "TupleLiteral", ["tuple"], "Data Foundations", "Primitives", "atom",
     "Tuple literal ()", "tuple parens"),
]

VARIABLES = [
    (13, "LocalVar", ["identifier"], "Data Foundations", "Variables", "atom",
     "Local variable reference", "local declaration"),
    (14, "Parameter", ["typed_parameter", "default_parameter"], "Data Foundations", "Variables", "atom",
     "Function parameter", "function parameter"),
    (15, "InstanceField", ["attribute"], "Data Foundations", "Variables", "atom",
     "Instance field access", "this/self field access"),
    (16, "IndexAccess", ["subscript"], "Data Foundations", "Variables", "atom",
     "Array/dict index access", "bracket access"),
    (17, "SliceAccess", ["slice"], "Data Foundations", "Variables", "atom",
     "Slice access [a:b]", "slice notation"),
]

# =============================================================================
# LOGIC & FLOW (Magenta) — IDs 18-55
# =============================================================================

EXPRESSIONS = [
    (18, "BinaryExpr", ["binary_operator"], "Logic & Flow", "Expressions", "atom",
     "Binary operation a + b", "arithmetic/bitwise ops"),
    (19, "UnaryExpr", ["unary_operator", "not_operator"], "Logic & Flow", "Expressions", "atom",
     "Unary operation -x, !x", "unary prefix"),
    (20, "ComparisonExpr", ["comparison_operator"], "Logic & Flow", "Expressions", "atom",
     "Comparison a == b", "comparison ops"),
    (21, "LogicalExpr", ["boolean_operator"], "Logic & Flow", "Expressions", "atom",
     "Logical and/or", "boolean ops"),
    (22, "CallExpr", ["call"], "Logic & Flow", "Expressions", "atom",
     "Function call f(x)", "function call"),
    (23, "TernaryExpr", ["conditional_expression"], "Logic & Flow", "Expressions", "atom",
     "Ternary a ? b : c", "conditional expression"),
    (24, "Closure", ["lambda"], "Logic & Flow", "Expressions", "atom",
     "Lambda/closure", "lambda keyword"),
    (25, "AwaitExpr", ["await"], "Logic & Flow", "Expressions", "atom",
     "Await expression", "await keyword"),
]

STATEMENTS = [
    (26, "Assignment", ["assignment"], "Logic & Flow", "Statements", "atom",
     "Variable assignment", "= operator"),
    (27, "AugmentedAssignment", ["augmented_assignment"], "Logic & Flow", "Statements", "atom",
     "Augmented assignment +=", "+= operator"),
    (28, "ExpressionStmt", ["expression_statement"], "Logic & Flow", "Statements", "atom",
     "Standalone expression", "expression as statement"),
    (29, "ReturnStmt", ["return_statement"], "Logic & Flow", "Statements", "atom",
     "Return statement", "return keyword"),
    (30, "RaiseStmt", ["raise_statement"], "Logic & Flow", "Statements", "atom",
     "Raise/throw exception", "raise keyword"),
    (31, "AssertStmt", ["assert_statement"], "Logic & Flow", "Statements", "atom",
     "Assert statement", "assert keyword"),
    (32, "PassStmt", ["pass_statement"], "Logic & Flow", "Statements", "atom",
     "Pass/no-op statement", "pass keyword"),
    (33, "BreakStmt", ["break_statement"], "Logic & Flow", "Statements", "atom",
     "Break loop", "break keyword"),
    (34, "ContinueStmt", ["continue_statement"], "Logic & Flow", "Statements", "atom",
     "Continue loop", "continue keyword"),
    (35, "DeleteStmt", ["delete_statement"], "Logic & Flow", "Statements", "atom",
     "Delete statement", "del keyword"),
]

CONTROL_STRUCTURES = [
    (36, "IfBranch", ["if_statement"], "Logic & Flow", "Control Structures", "atom",
     "If conditional", "if/else"),
    (37, "ElifBranch", ["elif_clause"], "Logic & Flow", "Control Structures", "atom",
     "Elif branch", "elif keyword"),
    (38, "ElseBranch", ["else_clause"], "Logic & Flow", "Control Structures", "atom",
     "Else branch", "else keyword"),
    (39, "LoopFor", ["for_statement"], "Logic & Flow", "Control Structures", "atom",
     "For loop", "for loop"),
    (40, "LoopWhile", ["while_statement"], "Logic & Flow", "Control Structures", "atom",
     "While loop", "while loop"),
    (41, "TryCatch", ["try_statement"], "Logic & Flow", "Control Structures", "atom",
     "Try/catch block", "try/except"),
    (42, "ExceptHandler", ["except_clause"], "Logic & Flow", "Control Structures", "atom",
     "Exception handler", "except clause"),
    (43, "FinallyBlock", ["finally_clause"], "Logic & Flow", "Control Structures", "atom",
     "Finally block", "finally clause"),
    (44, "ContextManager", ["with_statement"], "Logic & Flow", "Control Structures", "atom",
     "With context manager", "with statement"),
    (45, "PatternMatch", ["match_statement", "case_clause"], "Logic & Flow", "Control Structures", "atom",
     "Pattern matching", "match/case"),
]

FUNCTIONS = [
    (46, "Function", ["function_definition"], "Logic & Flow", "Functions", "molecule",
     "Function definition", "def keyword"),
    (47, "AsyncFunction", ["async_function_definition"], "Logic & Flow", "Functions", "molecule",
     "Async function", "async def"),
    (48, "DecoratedFunction", ["decorated_definition"], "Logic & Flow", "Functions", "molecule",
     "Decorated function", "@decorator"),
    (49, "Generator", ["generator_expression"], "Logic & Flow", "Functions", "molecule",
     "Generator expression", "yield keyword"),
    (50, "ListComprehension", ["list_comprehension"], "Logic & Flow", "Functions", "atom",
     "List comprehension", "[x for x in]"),
    (51, "DictComprehension", ["dictionary_comprehension"], "Logic & Flow", "Functions", "atom",
     "Dict comprehension", "{k:v for}"),
    (52, "SetComprehension", ["set_comprehension"], "Logic & Flow", "Functions", "atom",
     "Set comprehension", "{x for x}"),
    (53, "Decorator", ["decorator"], "Logic & Flow", "Functions", "atom",
     "Decorator", "@symbol"),
    (54, "ParameterList", ["parameters"], "Logic & Flow", "Functions", "atom",
     "Parameter list", "(params)"),
    (55, "ArgumentList", ["argument_list"], "Logic & Flow", "Functions", "atom",
     "Argument list", "(args)"),
]

# =============================================================================
# ORGANIZATION (Green) — IDs 56-75
# =============================================================================

AGGREGATES = [
    (56, "Class", ["class_definition"], "Organization", "Aggregates", "molecule",
     "Class definition", "class keyword"),
    (57, "ValueObject", [], "Organization", "Aggregates", "molecule",
     "Immutable value type", "class immutable + no id"),
    (58, "Entity", [], "Organization", "Aggregates", "molecule",
     "Entity with identity", "class with id field"),
    (59, "AggregateRoot", [], "Organization", "Aggregates", "organelle",
     "Aggregate root", "raises domain events"),
    (60, "DTO", [], "Organization", "Aggregates", "molecule",
     "Data transfer object", "data-only class"),
    (61, "Factory", [], "Organization", "Aggregates", "molecule",
     "Factory class/method", "static create method"),
]

MODULES = [
    (66, "Import", ["import_statement"], "Organization", "Modules", "atom",
     "Import statement", "import keyword"),
    (67, "ImportFrom", ["import_from_statement"], "Organization", "Modules", "atom",
     "From import", "from x import y"),
    (68, "ImportAlias", ["aliased_import"], "Organization", "Modules", "atom",
     "Import alias", "import as"),
    (69, "DottedName", ["dotted_name"], "Organization", "Modules", "atom",
     "Dotted module path", "a.b.c"),
    (70, "Comment", ["comment"], "Organization", "Files", "atom",
     "Code comment", "# or //"),
]

TYPES = [
    (71, "TypeAnnotation", ["type"], "Organization", "Types", "atom",
     "Type annotation", ": Type"),
    (72, "GenericType", ["generic_type"], "Organization", "Types", "atom",
     "Generic type", "List[T]"),
    (73, "UnionType", ["union_type"], "Organization", "Types", "atom",
     "Union type", "A | B"),
    (74, "KeywordArg", ["keyword_argument"], "Organization", "Types", "atom",
     "Keyword argument", "key=value"),
]

# =============================================================================
# EXECUTION (Amber) — IDs 76-96
# =============================================================================

EXECUTABLES = [
    (76, "MainEntry", [], "Execution", "Executables", "organelle",
     "Main entry point", "if __name__"),
    (77, "APIHandler", [], "Execution", "Executables", "organelle",
     "API route handler", "@app.get/post"),
    (78, "CommandHandler", [], "Execution", "Executables", "organelle",
     "Command handler (CQRS)", "handles *Command"),
    (79, "QueryHandler", [], "Execution", "Executables", "organelle",
     "Query handler (CQRS)", "handles *Query"),
    (80, "EventHandler", [], "Execution", "Executables", "organelle",
     "Event handler", "@Subscribe"),
    (81, "Middleware", [], "Execution", "Executables", "organelle",
     "Middleware function", "calls next()"),
    (82, "Validator", [], "Execution", "Executables", "organelle",
     "Validation function", "validate* + throws"),
    (83, "Repository", [], "Execution", "Executables", "organelle",
     "Repository pattern", "save/find methods"),
    (84, "UseCase", [], "Execution", "Executables", "organelle",
     "Use case handler", "single execute method"),
]

# =============================================================================
# ALL DEFINITIONS COMBINED
# =============================================================================

ALL_DEFINITIONS = (
    BITS +
    PRIMITIVES +
    VARIABLES +
    EXPRESSIONS +
    STATEMENTS +
    CONTROL_STRUCTURES +
    FUNCTIONS +
    AGGREGATES +
    MODULES +
    TYPES +
    EXECUTABLES
)
