; =============================================================================
; JAVASCRIPT D5_STATE QUERIES - Statefulness detection
; =============================================================================
; Detects state maintenance patterns for D5:STATE dimension classification
; Values: stateless, stateful
; =============================================================================

; -----------------------------------------------------------------------------
; STATEFUL INDICATORS - Instance/this state
; -----------------------------------------------------------------------------

; this.attr access (reading instance state)
(member_expression
  object: (this) @_this
  property: (property_identifier) @state.instance_read) @state.this_access

; this.attr = value (writing instance state)
(assignment_expression
  left: (member_expression
    object: (this)
    property: (property_identifier) @state.instance_write)) @state.this_mutation

; this.attr += value (mutating instance state)
(augmented_assignment_expression
  left: (member_expression
    object: (this))) @state.this_augmented

; Constructor assigning to this
(method_definition
  name: (property_identifier) @_constructor
  (#eq? @_constructor "constructor")
  body: (statement_block
    (expression_statement
      (assignment_expression
        left: (member_expression
          object: (this)))))) @state.constructor_state

; -----------------------------------------------------------------------------
; CLASS FIELDS (ES2022) - Class-level state
; -----------------------------------------------------------------------------

; Public field definition
(field_definition
  property: (property_identifier) @state.class_field) @state.public_field

; Private field definition (#field)
(field_definition
  property: (private_property_identifier) @state.private_field) @state.private_field_def

; Static field
(field_definition
  "static"
  property: (property_identifier) @state.static_field) @state.static_field_def

; -----------------------------------------------------------------------------
; MODULE-LEVEL STATE - Module variables
; -----------------------------------------------------------------------------

; let/const at module level with mutable reference
(program
  (lexical_declaration
    kind: "let"
    (variable_declarator
      name: (identifier) @state.module_let))) @state.module_let_decl

; var at module level (hoisted, mutable)
(program
  (variable_declaration
    (variable_declarator
      name: (identifier) @state.module_var))) @state.module_var_decl

; Module-level assignment to existing variable
(program
  (expression_statement
    (assignment_expression
      left: (identifier) @state.module_reassign))) @state.module_mutation

; -----------------------------------------------------------------------------
; CLOSURE STATE - Captured variables
; -----------------------------------------------------------------------------

; Function inside function (potential closure)
(function_declaration
  body: (statement_block
    (function_declaration) @state.nested_function)) @state.closure_parent

; Arrow function inside function
(function_declaration
  body: (statement_block
    (_
      (arrow_function) @state.nested_arrow))) @state.arrow_closure

; Method returning arrow function (closure factory)
(method_definition
  body: (statement_block
    (return_statement
      (arrow_function)))) @state.closure_factory

; -----------------------------------------------------------------------------
; REACT STATE - useState, useReducer
; -----------------------------------------------------------------------------

; useState hook
(call_expression
  function: (identifier) @_hook
  (#eq? @_hook "useState")) @state.react_state

; useReducer hook
(call_expression
  function: (identifier) @_hook
  (#eq? @_hook "useReducer")) @state.react_reducer

; useRef hook (mutable ref)
(call_expression
  function: (identifier) @_hook
  (#eq? @_hook "useRef")) @state.react_ref

; Class component state initialization
(assignment_expression
  left: (member_expression
    object: (this)
    property: (property_identifier) @_state
    (#eq? @_state "state"))) @state.react_class_state

; this.setState call
(call_expression
  function: (member_expression
    object: (this)
    property: (property_identifier) @_setState
    (#eq? @_setState "setState"))) @state.react_set_state

; -----------------------------------------------------------------------------
; MEMOIZATION STATE - Cached computation
; -----------------------------------------------------------------------------

; useMemo hook
(call_expression
  function: (identifier) @_hook
  (#eq? @_hook "useMemo")) @state.memo

; useCallback hook
(call_expression
  function: (identifier) @_hook
  (#eq? @_hook "useCallback")) @state.callback_memo

; memo() HOC
(call_expression
  function: (identifier) @_memo
  (#eq? @_memo "memo")) @state.component_memo

; React.memo
(call_expression
  function: (member_expression
    object: (identifier) @_react
    (#eq? @_react "React")
    property: (property_identifier) @_memo
    (#eq? @_memo "memo"))) @state.react_memo

; -----------------------------------------------------------------------------
; REDUX/STORE STATE - External state management
; -----------------------------------------------------------------------------

; useSelector hook
(call_expression
  function: (identifier) @_hook
  (#eq? @_hook "useSelector")) @state.redux_selector

; useDispatch hook
(call_expression
  function: (identifier) @_hook
  (#eq? @_hook "useDispatch")) @state.redux_dispatch

; connect HOC
(call_expression
  function: (identifier) @_connect
  (#eq? @_connect "connect")) @state.redux_connect

; createStore
(call_expression
  function: (identifier) @_create
  (#eq? @_create "createStore")) @state.redux_store

; configureStore
(call_expression
  function: (identifier) @_configure
  (#eq? @_configure "configureStore")) @state.toolkit_store

; -----------------------------------------------------------------------------
; ZUSTAND/JOTAI/RECOIL STATE - Modern state libraries
; -----------------------------------------------------------------------------

; zustand create
(call_expression
  function: (identifier) @_create
  (#eq? @_create "create")
  arguments: (arguments
    (arrow_function))) @state.zustand

; atom() creation
(call_expression
  function: (identifier) @_atom
  (#match? @_atom "^(atom|atomWithStorage|atomFamily)$")) @state.jotai_atom

; useAtom hook
(call_expression
  function: (identifier) @_hook
  (#eq? @_hook "useAtom")) @state.jotai_use

; selector() recoil
(call_expression
  function: (identifier) @_selector
  (#eq? @_selector "selector")) @state.recoil_selector

; -----------------------------------------------------------------------------
; SINGLETON/GLOBAL STATE
; -----------------------------------------------------------------------------

; window.X assignment (global browser state)
(assignment_expression
  left: (member_expression
    object: (identifier) @_window
    (#eq? @_window "window"))) @state.window_global

; globalThis assignment
(assignment_expression
  left: (member_expression
    object: (identifier) @_global
    (#eq? @_global "globalThis"))) @state.global_this

; global assignment (Node.js)
(assignment_expression
  left: (member_expression
    object: (identifier) @_global
    (#eq? @_global "global"))) @state.node_global

; -----------------------------------------------------------------------------
; MAP/SET/WEAKMAP STATE - Collection state
; -----------------------------------------------------------------------------

; new Map/Set/WeakMap/WeakSet
(new_expression
  constructor: (identifier) @_collection
  (#match? @_collection "^(Map|Set|WeakMap|WeakSet)$")) @state.collection

; Map/Set method calls (mutation)
(call_expression
  function: (member_expression
    property: (property_identifier) @_method
    (#match? @_method "^(set|add|delete|clear)$"))) @state.collection_mutation
