; JAVASCRIPT D7_LIFECYCLE QUERIES - Lifecycle phase detection
; Detects object lifecycle patterns for D7:LIFECYCLE dimension classification
; Values: create, use, destroy, manage

; -----------------------------------------------------------------------------
; CREATE PHASE - Object instantiation and initialization
; -----------------------------------------------------------------------------

; Constructor method definition
(method_definition
  name: (property_identifier) @_name
  (#eq? @_name "constructor")) @lifecycle.create.constructor

; new ClassName() instantiation
(new_expression
  constructor: (identifier) @lifecycle.class_instantiation
  (#match? @lifecycle.class_instantiation "^[A-Z]")) @lifecycle.create.instantiation

; new ClassName.X() member instantiation
(new_expression
  constructor: (member_expression)) @lifecycle.create.member_instantiation

; Factory function pattern - create*, make*, build*
(function_declaration
  name: (identifier) @_name
  (#match? @_name "^(create|make|build|new|construct|initialize|init|setup|spawn|generate)")) @lifecycle.create.factory

; Arrow factory
(variable_declarator
  name: (identifier) @_name
  (#match? @_name "^(create|make|build)"))
  @lifecycle.create.arrow_factory

; Object.create()
(call_expression
  function: (member_expression
    object: (identifier) @_obj
    (#eq? @_obj "Object")
    property: (property_identifier) @_method
    (#eq? @_method "create"))) @lifecycle.create.object_create

; Object.assign() (shallow clone)
(call_expression
  function: (member_expression
    object: (identifier) @_obj
    (#eq? @_obj "Object")
    property: (property_identifier) @_method
    (#eq? @_method "assign"))) @lifecycle.create.object_assign

; Spread copy { ...obj }
(spread_element) @lifecycle.create.spread_copy

; Array.from()
(call_expression
  function: (member_expression
    object: (identifier) @_arr
    (#eq? @_arr "Array")
    property: (property_identifier) @_method
    (#eq? @_method "from"))) @lifecycle.create.array_from

; structuredClone()
(call_expression
  function: (identifier) @_func
  (#eq? @_func "structuredClone")) @lifecycle.create.structured_clone

; JSON.parse (deserialization creates new object)
(call_expression
  function: (member_expression
    object: (identifier) @_json
    (#eq? @_json "JSON")
    property: (property_identifier) @_method
    (#eq? @_method "parse"))) @lifecycle.create.json_parse

; -----------------------------------------------------------------------------
; DESTROY PHASE - Object cleanup and teardown
; -----------------------------------------------------------------------------

; close() method call
(call_expression
  function: (member_expression
    property: (property_identifier) @_method
    (#eq? @_method "close"))) @lifecycle.destroy.close

; dispose() method call
(call_expression
  function: (member_expression
    property: (property_identifier) @_method
    (#eq? @_method "dispose"))) @lifecycle.destroy.dispose

; destroy() method call
(call_expression
  function: (member_expression
    property: (property_identifier) @_method
    (#eq? @_method "destroy"))) @lifecycle.destroy.destroy

; cleanup/teardown function definitions
(function_declaration
  name: (identifier) @_name
  (#match? @_name "^(destroy|cleanup|teardown|dispose|finalize|release|free|clear|reset|remove|unmount)")) @lifecycle.destroy.cleanup_func

; delete operator
(unary_expression
  operator: "delete") @lifecycle.destroy.delete_operator

; abort() - AbortController
(call_expression
  function: (member_expression
    property: (property_identifier) @_method
    (#eq? @_method "abort"))) @lifecycle.destroy.abort

; disconnect() - Observer/WebSocket
(call_expression
  function: (member_expression
    property: (property_identifier) @_method
    (#eq? @_method "disconnect"))) @lifecycle.destroy.disconnect

; removeEventListener
(call_expression
  function: (member_expression
    property: (property_identifier) @_method
    (#eq? @_method "removeEventListener"))) @lifecycle.destroy.remove_listener

; clearInterval/clearTimeout
(call_expression
  function: (identifier) @_func
  (#match? @_func "^(clearInterval|clearTimeout|cancelAnimationFrame)$")) @lifecycle.destroy.clear_timer

; -----------------------------------------------------------------------------
; REACT LIFECYCLE - Component mounting/unmounting
; -----------------------------------------------------------------------------

; componentDidMount
(method_definition
  name: (property_identifier) @_method
  (#eq? @_method "componentDidMount")) @lifecycle.create.mount

; componentWillUnmount
(method_definition
  name: (property_identifier) @_method
  (#eq? @_method "componentWillUnmount")) @lifecycle.destroy.unmount

; useEffect cleanup (return function)
(call_expression
  function: (identifier) @_hook
  (#eq? @_hook "useEffect")
  arguments: (arguments
    (arrow_function
      body: (statement_block
        (return_statement
          [(arrow_function) (function_expression)]))))) @lifecycle.manage.effect_cleanup

; useLayoutEffect
(call_expression
  function: (identifier) @_hook
  (#eq? @_hook "useLayoutEffect")) @lifecycle.manage.layout_effect

; useInsertionEffect
(call_expression
  function: (identifier) @_hook
  (#eq? @_hook "useInsertionEffect")) @lifecycle.manage.insertion_effect

; componentDidUpdate
(method_definition
  name: (property_identifier) @_method
  (#eq? @_method "componentDidUpdate")) @lifecycle.manage.update

; shouldComponentUpdate
(method_definition
  name: (property_identifier) @_method
  (#eq? @_method "shouldComponentUpdate")) @lifecycle.manage.should_update

; getDerivedStateFromProps
(method_definition
  name: (property_identifier) @_method
  (#eq? @_method "getDerivedStateFromProps")) @lifecycle.manage.derive_state

; getSnapshotBeforeUpdate
(method_definition
  name: (property_identifier) @_method
  (#eq? @_method "getSnapshotBeforeUpdate")) @lifecycle.manage.snapshot

; -----------------------------------------------------------------------------
; MANAGE PHASE - Lifecycle orchestration
; -----------------------------------------------------------------------------

; Context manager pattern - with statement
; (JavaScript doesn't have 'with' for resource management, but we can detect patterns)

; try/finally cleanup pattern
(try_statement
  finalizer: (finally_clause)) @lifecycle.manage.try_finally

; async/await with cleanup
(await_expression
  (call_expression
    function: (member_expression
      property: (property_identifier) @_method
      (#match? @_method "^(close|dispose|cleanup|destroy)$")))) @lifecycle.manage.async_cleanup

; Promise.finally
(call_expression
  function: (member_expression
    property: (property_identifier) @_method
    (#eq? @_method "finally"))) @lifecycle.manage.promise_finally

; AbortController creation (signal management)
(new_expression
  constructor: (identifier) @_ctrl
  (#eq? @_ctrl "AbortController")) @lifecycle.manage.abort_controller

; Observer pattern (MutationObserver, IntersectionObserver, etc.)
(new_expression
  constructor: (identifier) @_observer
  (#match? @_observer "(Observer)$")) @lifecycle.manage.observer

; EventEmitter management
(call_expression
  function: (member_expression
    property: (property_identifier) @_method
    (#match? @_method "^(on|once|addListener|prependListener)$"))) @lifecycle.manage.event_listener

; WeakRef creation (weak reference management)
(new_expression
  constructor: (identifier) @_weak
  (#eq? @_weak "WeakRef")) @lifecycle.manage.weak_ref

; FinalizationRegistry (cleanup callback registration)
(new_expression
  constructor: (identifier) @_registry
  (#eq? @_registry "FinalizationRegistry")) @lifecycle.manage.finalization

; -----------------------------------------------------------------------------
; USE PHASE - Active usage patterns
; -----------------------------------------------------------------------------

; Method invocation on object
(call_expression
  function: (member_expression
    property: (property_identifier) @lifecycle.use.method_call)) @lifecycle.use.invocation

; Property access
(member_expression
  property: (property_identifier) @lifecycle.use.property_read) @lifecycle.use.access

; await expression (async usage)
(await_expression) @lifecycle.use.await

; yield expression (generator usage)
(yield_expression) @lifecycle.use.yield
