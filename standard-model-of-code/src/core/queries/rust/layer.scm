; =============================================================================
; RUST LAYER QUERY (D2_LAYER)
; Tree-sitter-based Clean Architecture layer detection
; =============================================================================
; Layers: Interface | Application | Core | Infrastructure | Test | Unknown

; =============================================================================
; INFRASTRUCTURE LAYER
; Database, file I/O, external services, HTTP clients
; =============================================================================

; Database operations (diesel, sqlx, sea-orm)
(call_expression
  function: (scoped_identifier
    path: (identifier) @_mod
    (#match? @_mod "^(diesel|sqlx|sea_orm|rusqlite|tokio_postgres)$"))
  @layer.infrastructure.database)

(macro_invocation
  macro: (identifier) @_macro
  (#match? @_macro "^(query|query_as|sql_query)$")
  @layer.infrastructure.database)

; Repository pattern
(struct_item
  name: (type_identifier) @_name
  (#match? @_name "(Repository|Store|DAO|Storage|Persistence)$")
  @layer.infrastructure.repository)

(impl_item
  trait: (type_identifier) @_trait
  (#match? @_trait "(Repository|Store|DAO)$")
  @layer.infrastructure.repository)

; HTTP clients (reqwest, hyper, surf)
(call_expression
  function: (scoped_identifier
    path: (identifier) @_mod
    (#match? @_mod "^(reqwest|hyper|surf|isahc)$"))
  @layer.infrastructure.http)

; File I/O
(call_expression
  function: (scoped_identifier
    path: (identifier) @_mod
    (#match? @_mod "^(std::fs|tokio::fs|async_std::fs)$"))
  @layer.infrastructure.file_io)

(macro_invocation
  macro: (scoped_identifier
    name: (identifier) @_macro
    (#match? @_macro "^(include_str|include_bytes)$"))
  @layer.infrastructure.file_io)

; Cache/Redis
(call_expression
  function: (scoped_identifier
    path: (identifier) @_mod
    (#match? @_mod "^(redis|cached|moka)$"))
  @layer.infrastructure.cache)

; =============================================================================
; INTERFACE LAYER
; HTTP handlers, CLI, API endpoints
; =============================================================================

; Actix-web handlers
(attribute_item
  (meta_item
    (identifier) @_attr
    (#match? @_attr "^(get|post|put|delete|patch|route)$"))
  @layer.interface.actix)

; Axum handlers
(function_item
  parameters: (parameters
    (parameter
      type: (type_identifier) @_type
      (#match? @_type "^(Json|Query|Path|State|Extension)$")))
  @layer.interface.axum)

; Rocket handlers
(attribute_item
  (meta_item
    (identifier) @_attr
    (#match? @_attr "^(get|post|put|delete|patch)$"))
  @layer.interface.rocket)

; Handler/Controller naming
(function_item
  name: (identifier) @_name
  (#match? @_name "(handler|controller|endpoint)$")
  @layer.interface.naming)

(struct_item
  name: (type_identifier) @_name
  (#match? @_name "(Handler|Controller|Router|Server)$")
  @layer.interface.naming)

; CLI (clap, structopt)
(attribute_item
  (meta_item
    (identifier) @_attr
    (#match? @_attr "^(command|clap|structopt)$"))
  @layer.interface.cli)

; tonic gRPC
(attribute_item
  (meta_item
    (identifier) @_attr
    (#match? @_attr "^tonic$"))
  @layer.interface.grpc)

; =============================================================================
; APPLICATION LAYER
; Services, use cases, business logic orchestration
; =============================================================================

; Service pattern
(struct_item
  name: (type_identifier) @_name
  (#match? @_name "(Service|UseCase|Interactor|Orchestrator|Application)$")
  @layer.application.service)

(impl_item
  type: (type_identifier) @_type
  (#match? @_type "(Service|UseCase|Interactor)$")
  @layer.application.service)

; =============================================================================
; CORE/DOMAIN LAYER
; Entities, value objects, domain logic
; =============================================================================

; Domain entities
(struct_item
  name: (type_identifier) @_name
  (#match? @_name "(Entity|Aggregate|ValueObject|Domain|Model)$")
  @layer.core.entity)

; Enums (domain values)
(enum_item
  @layer.core.enum)

; Traits (domain interfaces)
(trait_item
  @layer.core.trait)

; Type aliases
(type_item
  @layer.core.type_alias)

; Derive macros for domain objects
(attribute_item
  (meta_item
    (identifier) @_attr
    (#match? @_attr "^(Serialize|Deserialize|Clone|Debug|PartialEq|Eq|Hash)$"))
  @layer.core.derive)

; =============================================================================
; TEST LAYER
; Test files, fixtures, mocks
; =============================================================================

; Test functions
(attribute_item
  (meta_item
    (identifier) @_attr
    (#eq? @_attr "test"))
  @layer.test.function)

; Test modules
(mod_item
  (attribute_item
    (meta_item
      (identifier) @_attr
      (#eq? @_attr "cfg")))
  name: (identifier) @_name
  (#eq? @_name "tests")
  @layer.test.module)

; Benchmark tests
(attribute_item
  (meta_item
    (identifier) @_attr
    (#eq? @_attr "bench"))
  @layer.test.benchmark)

; Mock patterns (mockall, etc.)
(macro_invocation
  macro: (identifier) @_macro
  (#match? @_macro "^(mock|automock)$")
  @layer.test.mock)

; Assert macros
(macro_invocation
  macro: (identifier) @_macro
  (#match? @_macro "^(assert|assert_eq|assert_ne|debug_assert)$")
  @layer.test.assertion)
