; TYPESCRIPT LAYER (D2_LAYER)

; Layers: Interface | Application | Core | Infrastructure | Test | Unknown

; -- INFRASTRUCTURE --
;    Database, file I/O, external services, HTTP clients

; Database/ORM patterns (Prisma, TypeORM, etc.)
(call_expression
  function: (member_expression
    object: (identifier) @_obj
    (#match? @_obj "^(prisma|sequelize|mongoose|knex|typeorm|repository)$"))
  @layer.infrastructure.orm)

; Repository pattern
(class_declaration
  name: (type_identifier) @_name
  (#match? @_name "(Repository|Store|DAO|DataAccess|Persistence)$")
  @layer.infrastructure.repository)

; HTTP clients
(call_expression
  function: (identifier) @_func
  (#match? @_func "^fetch$")
  @layer.infrastructure.http)

(call_expression
  function: (member_expression
    object: (identifier) @_obj
    (#match? @_obj "^(axios|fetch|http|https|got|superagent|HttpClient)$"))
  @layer.infrastructure.http)

; File system operations
(call_expression
  function: (member_expression
    object: (identifier) @_obj
    (#match? @_obj "^(fs|path|fsp)$"))
  @layer.infrastructure.file_io)

; Cache/Redis
(call_expression
  function: (member_expression
    object: (identifier) @_obj
    (#match? @_obj "^(redis|cache|Redis|Cache)$"))
  @layer.infrastructure.cache)

; -- INTERFACE --
;    API endpoints, routes, controllers, React/Angular components

; Express/NestJS routes
(call_expression
  function: (member_expression
    object: (identifier) @_app
    property: (property_identifier) @_method
    (#match? @_method "^(get|post|put|delete|patch|use)$"))
  @layer.interface.express)

; NestJS decorators
(decorator
  (call_expression
    function: (identifier) @_deco
    (#match? @_deco "^(Controller|Get|Post|Put|Delete|Patch)$"))
  @layer.interface.nestjs)

; Next.js/Remix route handlers
(export_statement
  declaration: (function_declaration
    name: (identifier) @_name
    (#match? @_name "^(GET|POST|PUT|DELETE|PATCH|loader|action)$"))
  @layer.interface.route_handler)

; React components (function)
(function_declaration
  name: (identifier) @_name
  (#match? @_name "^[A-Z]")
  return_type: (type_annotation
    (type_identifier) @_type
    (#match? @_type "^(JSX|React)"))
  @layer.interface.react)

; React components with FC type
(lexical_declaration
  (variable_declarator
    name: (identifier) @_name
    (#match? @_name "^[A-Z]")
    type: (type_annotation
      (generic_type
        name: (type_identifier) @_type
        (#match? @_type "^(FC|FunctionComponent|React\\.FC)$"))))
  @layer.interface.react)

; Angular components
(decorator
  (call_expression
    function: (identifier) @_deco
    (#match? @_deco "^Component$"))
  @layer.interface.angular)

; Controller naming
(class_declaration
  name: (type_identifier) @_name
  (#match? @_name "(Controller|Handler|Router|Endpoint|Resource)$")
  @layer.interface.naming)

; GraphQL resolvers
(decorator
  (call_expression
    function: (identifier) @_deco
    (#match? @_deco "^(Query|Mutation|Resolver|Subscription)$"))
  @layer.interface.graphql)

; -- APPLICATION --
;    Services, use cases, business logic orchestration

; Service classes
(class_declaration
  name: (type_identifier) @_name
  (#match? @_name "(Service|UseCase|Interactor|Orchestrator|Application)$")
  @layer.application.service)

; NestJS Injectable services
(decorator
  (call_expression
    function: (identifier) @_deco
    (#match? @_deco "^Injectable$"))
  @layer.application.di)

; Use case pattern (execute method)
(class_declaration
  name: (type_identifier) @_name
  body: (class_body
    (method_definition
      name: (property_identifier) @_method
      (#match? @_method "^(execute|run|perform|handle)$")))
  @layer.application.usecase)

; -- CORE/DOMAIN --
;    Entities, value objects, domain logic, interfaces, types

; TypeScript interfaces (domain models)
(interface_declaration
  name: (type_identifier) @_name
  (#match? @_name "(Entity|Model|DTO|Props|State|Domain|Aggregate)$")
  @layer.core.interface)

; Type aliases
(type_alias_declaration
  name: (type_identifier) @_name
  (#match? @_name "(Entity|Model|DTO|Props|State|Domain|ValueObject)$")
  @layer.core.type)

; Domain classes
(class_declaration
  name: (type_identifier) @_name
  (#match? @_name "(Entity|Aggregate|ValueObject|DomainObject|DomainEvent)$")
  @layer.core.entity)

; Enums
(enum_declaration
  @layer.core.enum)

; Abstract classes (domain interfaces)
(abstract_class_declaration
  @layer.core.abstract)

; -- TEST --
;    Test files, fixtures, mocks

; Test functions (describe/it/test)
(call_expression
  function: (identifier) @_func
  (#match? @_func "^(describe|it|test|expect)$")
  @layer.test.function)

; Jest/Vitest patterns
(call_expression
  function: (member_expression
    object: (identifier) @_obj
    (#match? @_obj "^(jest|vi)$"))
  @layer.test.mock)

; beforeEach/afterEach
(call_expression
  function: (identifier) @_func
  (#match? @_func "^(beforeEach|afterEach|beforeAll|afterAll)$")
  @layer.test.lifecycle)
