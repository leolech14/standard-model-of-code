; =============================================================================
; GO LAYER QUERY (D2_LAYER)
; Tree-sitter-based Clean Architecture layer detection
; =============================================================================
; Layers: Interface | Application | Core | Infrastructure | Test | Unknown

; =============================================================================
; INFRASTRUCTURE LAYER
; Database, file I/O, external services, HTTP clients
; =============================================================================

; Database operations (sql, gorm, sqlx)
(call_expression
  function: (selector_expression
    operand: (identifier) @_obj
    (#match? @_obj "^(db|tx|conn|sql|gorm|sqlx)$"))
  @layer.infrastructure.database)

(call_expression
  function: (selector_expression
    field: (field_identifier) @_method
    (#match? @_method "^(Query|QueryRow|Exec|Prepare|Begin|Commit|Rollback|Find|Create|Update|Delete|First|Where)$"))
  @layer.infrastructure.database)

; Repository pattern
(type_declaration
  (type_spec
    name: (type_identifier) @_name
    (#match? @_name "(Repository|Store|DAO|Storage|Persistence)$"))
  @layer.infrastructure.repository)

; HTTP clients
(call_expression
  function: (selector_expression
    operand: (identifier) @_obj
    (#match? @_obj "^(http|client|resty)$"))
  @layer.infrastructure.http)

(call_expression
  function: (selector_expression
    field: (field_identifier) @_method
    (#match? @_method "^(Get|Post|Put|Delete|Do|NewRequest)$"))
  @layer.infrastructure.http)

; File I/O
(call_expression
  function: (selector_expression
    operand: (identifier) @_obj
    (#match? @_obj "^(os|io|ioutil|bufio)$"))
  @layer.infrastructure.file_io)

; Cache/Redis
(call_expression
  function: (selector_expression
    operand: (identifier) @_obj
    (#match? @_obj "^(redis|cache|memcache)$"))
  @layer.infrastructure.cache)

; =============================================================================
; INTERFACE LAYER
; HTTP handlers, gRPC, CLI
; =============================================================================

; HTTP handlers (net/http, gin, echo, fiber, chi)
(function_declaration
  parameters: (parameter_list
    (parameter_declaration
      type: (pointer_type
        (qualified_type
          package: (package_identifier) @_pkg
          (#eq? @_pkg "http")
          name: (type_identifier) @_type
          (#eq? @_type "Request")))))
  @layer.interface.http_handler)

(function_declaration
  parameters: (parameter_list
    (parameter_declaration
      type: (qualified_type
        package: (package_identifier) @_pkg
        (#match? @_pkg "^(gin|echo|fiber|chi)$"))))
  @layer.interface.http_handler)

; Handler/Controller naming
(function_declaration
  name: (identifier) @_name
  (#match? @_name "(Handler|Controller|Endpoint)$")
  @layer.interface.naming)

(type_declaration
  (type_spec
    name: (type_identifier) @_name
    (#match? @_name "(Handler|Controller|Router|Server)$"))
  @layer.interface.naming)

; gRPC server implementations
(method_declaration
  receiver: (parameter_list
    (parameter_declaration
      type: (pointer_type
        (type_identifier) @_type
        (#match? @_type "Server$"))))
  @layer.interface.grpc)

; CLI commands (cobra, urfave/cli)
(call_expression
  function: (selector_expression
    operand: (identifier) @_obj
    (#match? @_obj "^(cobra|cli)$"))
  @layer.interface.cli)

; =============================================================================
; APPLICATION LAYER
; Services, use cases, business logic orchestration
; =============================================================================

; Service pattern
(type_declaration
  (type_spec
    name: (type_identifier) @_name
    (#match? @_name "(Service|UseCase|Interactor|Orchestrator|Application)$"))
  @layer.application.service)

; Interface with service methods
(type_declaration
  (type_spec
    name: (type_identifier) @_name
    (#match? @_name "(Service|UseCase)$")
    type: (interface_type))
  @layer.application.service_interface)

; =============================================================================
; CORE/DOMAIN LAYER
; Entities, value objects, domain logic
; =============================================================================

; Domain entities
(type_declaration
  (type_spec
    name: (type_identifier) @_name
    (#match? @_name "(Entity|Aggregate|ValueObject|Domain|Model)$"))
  @layer.core.entity)

; Struct definitions (potential domain objects)
(type_declaration
  (type_spec
    type: (struct_type))
  @layer.core.struct)

; Interface definitions (domain contracts)
(type_declaration
  (type_spec
    type: (interface_type))
  @layer.core.interface)

; Constants/Enums (iota patterns)
(const_declaration
  (const_spec
    value: (expression_list
      (iota)))
  @layer.core.enum)

; =============================================================================
; TEST LAYER
; Test files, fixtures, mocks
; =============================================================================

; Test functions
(function_declaration
  name: (identifier) @_name
  (#match? @_name "^Test")
  parameters: (parameter_list
    (parameter_declaration
      type: (pointer_type
        (qualified_type
          package: (package_identifier) @_pkg
          (#eq? @_pkg "testing")))))
  @layer.test.function)

; Benchmark functions
(function_declaration
  name: (identifier) @_name
  (#match? @_name "^Benchmark")
  @layer.test.benchmark)

; Example functions
(function_declaration
  name: (identifier) @_name
  (#match? @_name "^Example")
  @layer.test.example)

; Test helper functions
(function_declaration
  name: (identifier) @_name
  (#match? @_name "^(setup|teardown|mock|stub|fake)"))
  @layer.test.helper)

; testify/gomock patterns
(call_expression
  function: (selector_expression
    operand: (identifier) @_obj
    (#match? @_obj "^(assert|require|mock|suite)$"))
  @layer.test.assertion)
