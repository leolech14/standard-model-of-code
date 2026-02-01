; TYPESCRIPT ROLES (D3_ROLE)

; TypeScript-specific patterns

; NOTE: The query loader will first look for typescript-specific patterns,
; then fall back to javascript patterns. This file only contains patterns
; unique to TypeScript grammar.

; INTERNAL/DTO PATTERN (TypeScript-specific)
; Data containers and type definitions

; Interface (data shape definition)
(interface_declaration
  name: (type_identifier) @role.internal.interface)

; Type alias
(type_alias_declaration
  name: (type_identifier) @role.internal.type)

; Enum definition
(enum_declaration
  name: (identifier) @role.internal.enum)

; CLASS PATTERNS (TypeScript syntax uses type_identifier)

; Class with Service naming (TS uses type_identifier for class names)
(class_declaration
  name: (type_identifier) @role.service.naming
  (#match? @role.service.naming "Service$"))

; Class with Controller naming
(class_declaration
  name: (type_identifier) @role.controller.naming
  (#match? @role.controller.naming "(Controller|Handler|Resource|Endpoint)$"))

; Class with Repository naming
(class_declaration
  name: (type_identifier) @role.repository.naming
  (#match? @role.repository.naming "(Repository|Store|DAO)$"))

; Factory class
(class_declaration
  name: (type_identifier) @role.factory.class
  (#match? @role.factory.class "Factory$"))

; Mapper class
(class_declaration
  name: (type_identifier) @role.mapper.class
  (#match? @role.mapper.class "(Mapper|Converter|Transformer|Serializer)$"))

; Validator class
(class_declaration
  name: (type_identifier) @role.validator.class
  (#match? @role.validator.class "(Validator|Schema|Dto)$"))

; Handler class
(class_declaration
  name: (type_identifier) @role.handler.class
  (#match? @role.handler.class "Handler$"))

; Guard class
(class_declaration
  name: (type_identifier) @role.guard.class
  (#match? @role.guard.class "(Guard|Auth|Permission|Policy)$"))

; Utility class
(class_declaration
  name: (type_identifier) @role.utility.class
  (#match? @role.utility.class "(Utils?|Helper|Tools?)$"))

; Emitter/Publisher class
(class_declaration
  name: (type_identifier) @role.emitter.naming
  (#match? @role.emitter.naming "(Emitter|Publisher|Producer|Broadcaster)$"))

; Middleware class
(class_declaration
  name: (type_identifier) @role.middleware.class
  (#match? @role.middleware.class "Middleware$"))

; Test class
(class_declaration
  name: (type_identifier) @role.asserter.class
  (#match? @role.asserter.class "(Test|Spec)$"))

; CLASS WITH INHERITANCE (TypeScript syntax)

; Class extending repository base
(class_declaration
  name: (type_identifier) @role.repository.extends
  (class_heritage
    (extends_clause
      (identifier) @_base
      (#match? @_base "(Repository|Store|DAO|DataAccess)"))))

; Class extending EventEmitter
(class_declaration
  name: (type_identifier) @role.emitter.extends
  (class_heritage
    (extends_clause
      (identifier) @_base
      (#match? @_base "EventEmitter"))))

; DECORATOR PATTERNS (TypeScript/NestJS)

; Injectable decorator
(class_declaration
  (decorator
    (call_expression
      function: (identifier) @_dec
      (#eq? @_dec "Injectable")))
  name: (type_identifier) @role.service.injectable)

; Controller decorator
(class_declaration
  (decorator
    (call_expression
      function: (identifier) @_dec
      (#eq? @_dec "Controller")))
  name: (type_identifier) @role.controller.nestjs)

; Guard decorator
(class_declaration
  (decorator
    (call_expression
      function: (identifier) @_dec
      (#match? @_dec "^(UseGuards|CanActivate)$")))
  name: (type_identifier) @role.guard.decorated)

; Method decorator (e.g., @Get, @Post)
(method_definition
  (decorator
    (call_expression
      function: (identifier) @_dec
      (#match? @_dec "^(Get|Post|Put|Delete|Patch|Query|Mutation)$")))
  name: (property_identifier) @role.controller.method)

; REACT COMPONENT (TSX only - see tsx alias)

; NOTE: JSX patterns (jsx_element) are only valid in TSX grammar
; They are handled via javascript/roles.scm when using tsx alias

; HOOK PATTERN (React)

; Custom hook function
(function_declaration
  name: (identifier) @role.hook.function
  (#match? @role.hook.function "^use[A-Z]"))

; Custom hook arrow
(variable_declarator
  name: (identifier) @role.hook.arrow
  (#match? @role.hook.arrow "^use[A-Z]")
  value: (arrow_function))

; -- LIFECYCLE --

; Constructor
(method_definition
  name: (property_identifier) @role.lifecycle.constructor
  (#eq? @role.lifecycle.constructor "constructor"))

; Lifecycle methods
(method_definition
  name: (property_identifier) @role.lifecycle.method
  (#match? @role.lifecycle.method "^(componentDidMount|componentWillUnmount|ngOnInit|ngOnDestroy|mounted|unmounted)$"))

; -- VALIDATOR/FACTORY FUNCTIONS --

; Validation function
(function_declaration
  name: (identifier) @role.validator.function
  (#match? @role.validator.function "^(validate|check|verify|ensure|is[A-Z])"))

; Factory function
(function_declaration
  name: (identifier) @role.factory.function
  (#match? @role.factory.function "^(create|make|build|new)[A-Z]")
  body: (statement_block
    (return_statement)))

; Handler function
(function_declaration
  name: (identifier) @role.handler.function
  (#match? @role.handler.function "(handler|Handler|on[A-Z]|handle[A-Z])"))

; Emit function
(function_declaration
  name: (identifier) @role.emitter.function
  (#match? @role.emitter.function "^(emit|publish|broadcast|notify|dispatch)"))
