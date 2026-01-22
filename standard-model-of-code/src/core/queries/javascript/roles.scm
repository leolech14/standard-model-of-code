; =============================================================================
; JAVASCRIPT/TYPESCRIPT ROLES QUERY (D3_ROLE)
; Tree-sitter-based role detection via structural patterns
; =============================================================================

; =============================================================================
; REPOSITORY PATTERN
; CRUD-like classes with data access methods
; =============================================================================

; Class with repository-like methods
(class_declaration
  name: (identifier) @role.repository.class
  body: (class_body
    (method_definition
      name: (property_identifier) @_method
      (#match? @_method "^(find|get|save|delete|create|update|list|fetch)"))))

; Class extending repository base
(class_declaration
  name: (identifier) @role.repository.extends
  (class_heritage
    (identifier) @_base
    (#match? @_base "(Repository|Store|DAO|DataAccess)")))

; =============================================================================
; SERVICE PATTERN
; Business logic coordinators
; =============================================================================

; Class with Service naming
(class_declaration
  name: (identifier) @role.service.naming
  (#match? @role.service.naming "Service$"))

; NestJS/Angular @Injectable decorator
(class_declaration
  (decorator
    (call_expression
      function: (identifier) @_dec
      (#eq? @_dec "Injectable")))
  name: (identifier) @role.service.injectable)

; =============================================================================
; CONTROLLER PATTERN
; HTTP/API request handlers
; =============================================================================

; Express route handlers
(call_expression
  function: (member_expression
    object: (identifier) @_app
    property: (property_identifier) @_method
    (#match? @_method "^(get|post|put|delete|patch)$"))
  arguments: (arguments
    (string) @_path
    [(arrow_function) (function_expression)] @role.controller.express))

; NestJS @Controller decorator
(class_declaration
  (decorator
    (call_expression
      function: (identifier) @_dec
      (#eq? @_dec "Controller")))
  name: (identifier) @role.controller.nestjs)

; Class with Controller naming
(class_declaration
  name: (identifier) @role.controller.naming
  (#match? @role.controller.naming "(Controller|Handler|Resource|Endpoint)$"))

; =============================================================================
; FACTORY PATTERN
; Object creation methods that return new instances
; =============================================================================

; Factory function pattern
(function_declaration
  name: (identifier) @role.factory.function
  (#match? @role.factory.function "^(create|make|build|new)[A-Z]")
  body: (statement_block
    (return_statement)))

; Arrow function factory
(variable_declarator
  name: (identifier) @role.factory.arrow
  (#match? @role.factory.arrow "^(create|make|build)[A-Z]")
  value: (arrow_function
    body: [(object) (call_expression) (new_expression)]))

; Class with Factory naming
(class_declaration
  name: (identifier) @role.factory.class
  (#match? @role.factory.class "Factory$"))

; Static factory method
(method_definition
  "static"
  name: (property_identifier) @role.factory.static
  (#match? @role.factory.static "^(create|from|build)"))

; =============================================================================
; HANDLER PATTERN
; Event/message processors
; =============================================================================

; Event handler function
(function_declaration
  name: (identifier) @role.handler.function
  (#match? @role.handler.function "(handler|Handler|on[A-Z]|handle[A-Z])"))

; Event listener callback
(call_expression
  function: (member_expression
    property: (property_identifier) @_method
    (#match? @_method "^(addEventListener|on|once)$"))
  arguments: (arguments
    (string)
    [(arrow_function) (function_expression)] @role.handler.listener))

; Handler class
(class_declaration
  name: (identifier) @role.handler.class
  (#match? @role.handler.class "Handler$"))

; =============================================================================
; VALIDATOR PATTERN
; Input validation
; =============================================================================

; Validator class
(class_declaration
  name: (identifier) @role.validator.class
  (#match? @role.validator.class "(Validator|Schema|Dto)$"))

; Validation function
(function_declaration
  name: (identifier) @role.validator.function
  (#match? @role.validator.function "^(validate|check|verify|ensure|is[A-Z])"))

; Zod schema
(variable_declarator
  name: (identifier) @role.validator.zod
  value: (call_expression
    function: (member_expression
      object: (identifier) @_z
      (#eq? @_z "z"))))

; =============================================================================
; TRANSFORMER/MAPPER PATTERN
; Data transformation
; =============================================================================

; Mapper class
(class_declaration
  name: (identifier) @role.mapper.class
  (#match? @role.mapper.class "(Mapper|Converter|Transformer|Serializer)$"))

; Transform function
(function_declaration
  name: (identifier) @role.mapper.function
  (#match? @role.mapper.function "^(map|convert|transform|serialize|deserialize|to[A-Z]|from[A-Z])"))

; Array map callback (data transformation)
(call_expression
  function: (member_expression
    property: (property_identifier) @_map
    (#eq? @_map "map"))
  arguments: (arguments
    (arrow_function) @role.mapper.array_map))

; =============================================================================
; UTILITY PATTERN
; General-purpose helpers
; =============================================================================

; Utility class
(class_declaration
  name: (identifier) @role.utility.class
  (#match? @role.utility.class "(Utils?|Helper|Tools?)$"))

; Utility module function (top-level export)
(export_statement
  declaration: (function_declaration
    name: (identifier) @role.utility.export))

; =============================================================================
; TEST/ASSERTER PATTERN
; =============================================================================

; Jest/Mocha test function
(call_expression
  function: (identifier) @_test
  (#match? @_test "^(test|it|describe)$")
  arguments: (arguments
    (string)
    [(arrow_function) (function_expression)] @role.asserter.test))

; Test class
(class_declaration
  name: (identifier) @role.asserter.class
  (#match? @role.asserter.class "(Test|Spec)$"))

; =============================================================================
; LIFECYCLE PATTERN
; Initialization, cleanup
; =============================================================================

; Constructor
(method_definition
  name: (property_identifier) @role.lifecycle.constructor
  (#eq? @role.lifecycle.constructor "constructor"))

; Lifecycle methods (React, Angular, etc.)
(method_definition
  name: (property_identifier) @role.lifecycle.method
  (#match? @role.lifecycle.method "^(componentDidMount|componentWillUnmount|ngOnInit|ngOnDestroy|mounted|unmounted|created|destroyed|setup|teardown)$"))

; =============================================================================
; INTERNAL/DTO PATTERN
; Data containers with minimal logic
; =============================================================================

; NOTE: interface_declaration and type_alias_declaration are TypeScript-only
; They are handled in typescript/roles.scm which inherits from this file

; Plain class (entity-like naming, no suffix)
(class_declaration
  name: (identifier) @role.internal.entity
  (#match? @role.internal.entity "^[A-Z][a-z]+([A-Z][a-z]+)*$")
  (#not-match? @role.internal.entity "(Service|Controller|Factory|Handler|Validator|Mapper|Utils?|Helper|Repository|Store)$"))

; =============================================================================
; GUARD PATTERN
; Access control, permissions
; =============================================================================

; Guard class (NestJS pattern)
(class_declaration
  name: (identifier) @role.guard.class
  (#match? @role.guard.class "(Guard|Auth|Permission|Policy)$"))

; Guard decorator
(class_declaration
  (decorator
    (call_expression
      function: (identifier) @_dec
      (#match? @_dec "^(UseGuards|CanActivate)$")))
  name: (identifier) @role.guard.decorated)

; Permission check function
(function_declaration
  name: (identifier) @role.guard.function
  (#match? @role.guard.function "^(check|has|can|isAllowed|require)"))

; =============================================================================
; EMITTER PATTERN
; Event emission
; =============================================================================

; EventEmitter class extension
(class_declaration
  name: (identifier) @role.emitter.class
  (class_heritage
    (identifier) @_base
    (#match? @_base "EventEmitter")))

; Emit function
(function_declaration
  name: (identifier) @role.emitter.function
  (#match? @role.emitter.function "^(emit|publish|broadcast|notify|dispatch)"))

; Class with Emitter/Publisher naming
(class_declaration
  name: (identifier) @role.emitter.naming
  (#match? @role.emitter.naming "(Emitter|Publisher|Producer|Broadcaster)$"))

; =============================================================================
; REACT COMPONENT PATTERN
; =============================================================================

; Function component (JSX return)
(function_declaration
  name: (identifier) @role.component.function
  (#match? @role.component.function "^[A-Z]")
  body: (statement_block
    (return_statement
      (jsx_element))))

; Arrow function component
(variable_declarator
  name: (identifier) @role.component.arrow
  (#match? @role.component.arrow "^[A-Z]")
  value: (arrow_function
    body: [(jsx_element) (parenthesized_expression (jsx_element))]))

; React.memo wrapped component
(variable_declarator
  name: (identifier) @role.component.memo
  (#match? @role.component.memo "^[A-Z]")
  value: (call_expression
    function: (member_expression
      object: (identifier) @_react
      (#eq? @_react "React")
      property: (property_identifier) @_memo
      (#eq? @_memo "memo"))))

; Class component
(class_declaration
  name: (identifier) @role.component.class
  (#match? @role.component.class "^[A-Z]")
  (class_heritage
    (member_expression
      object: (identifier) @_react
      (#eq? @_react "React")
      property: (property_identifier) @_component
      (#match? @_component "^(Component|PureComponent)$"))))

; =============================================================================
; HOOK PATTERN (React)
; =============================================================================

; Custom hook function
(function_declaration
  name: (identifier) @role.hook.function
  (#match? @role.hook.function "^use[A-Z]"))

; Custom hook arrow
(variable_declarator
  name: (identifier) @role.hook.arrow
  (#match? @role.hook.arrow "^use[A-Z]")
  value: (arrow_function))

; =============================================================================
; MIDDLEWARE PATTERN
; =============================================================================

; Express middleware signature (req, res, next)
(function_declaration
  name: (identifier) @role.middleware.function
  parameters: (formal_parameters
    (identifier) @_req
    (identifier) @_res
    (identifier) @_next
    (#eq? @_next "next")))

; Middleware class
(class_declaration
  name: (identifier) @role.middleware.class
  (#match? @role.middleware.class "Middleware$"))
