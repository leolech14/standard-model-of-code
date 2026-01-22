; =============================================================================
; JAVASCRIPT DATA FLOW QUERIES - Assignment and mutation detection for D6:EFFECT
; =============================================================================
; Used by data_flow_analyzer.py to detect value flow and state mutations.
; =============================================================================

; -----------------------------------------------------------------------------
; SIMPLE ASSIGNMENT - x = value
; -----------------------------------------------------------------------------

(assignment_expression
  left: (identifier) @target.name
  right: (_) @source) @assignment

; Member assignment - obj.attr = value (mutation)
(assignment_expression
  left: (member_expression) @target.member
  right: (_) @source) @assignment.member

; Subscript assignment - arr[i] = value (mutation)
(assignment_expression
  left: (subscript_expression) @target.subscript
  right: (_) @source) @assignment.subscript

; Destructuring assignment - { a, b } = obj
(assignment_expression
  left: (object_pattern) @target.destructure_object
  right: (_) @source) @assignment.destructure

(assignment_expression
  left: (array_pattern) @target.destructure_array
  right: (_) @source) @assignment.destructure_array

; -----------------------------------------------------------------------------
; VARIABLE DECLARATIONS
; -----------------------------------------------------------------------------

; let/const declaration
(lexical_declaration
  (variable_declarator
    name: (identifier) @decl.name
    value: (_) @decl.value)) @declaration.lexical

; var declaration
(variable_declaration
  (variable_declarator
    name: (identifier) @decl.name
    value: (_) @decl.value)) @declaration.var

; Destructuring declaration
(lexical_declaration
  (variable_declarator
    name: (object_pattern) @decl.destructure)) @declaration.destructure

(lexical_declaration
  (variable_declarator
    name: (array_pattern) @decl.destructure_array)) @declaration.destructure_array

; -----------------------------------------------------------------------------
; AUGMENTED ASSIGNMENT - x += value (always mutation)
; -----------------------------------------------------------------------------

(augmented_assignment_expression
  left: (identifier) @target.name) @mutation.augmented

(augmented_assignment_expression
  left: (member_expression) @target.member) @mutation.augmented_member

(augmented_assignment_expression
  left: (subscript_expression) @target.subscript) @mutation.augmented_subscript

; Update expressions - i++, ++i, i--, --i
(update_expression
  argument: (identifier) @target.name) @mutation.update

(update_expression
  argument: (member_expression) @target.member) @mutation.update_member

; -----------------------------------------------------------------------------
; DELETE EXPRESSION (mutation)
; -----------------------------------------------------------------------------

(unary_expression
  operator: "delete"
  argument: (member_expression) @delete.member) @delete

(unary_expression
  operator: "delete"
  argument: (subscript_expression) @delete.subscript) @delete.subscript

; -----------------------------------------------------------------------------
; SIDE EFFECT CALLS - I/O and external interactions
; -----------------------------------------------------------------------------

; console.* calls
(call_expression
  function: (member_expression
    object: (identifier) @_obj
    (#eq? @_obj "console"))) @sideeffect.io

; fetch() call
(call_expression
  function: (identifier) @_func
  (#eq? @_func "fetch")) @sideeffect.external

; XMLHttpRequest
(new_expression
  constructor: (identifier) @_func
  (#eq? @_func "XMLHttpRequest")) @sideeffect.external

; axios.* calls
(call_expression
  function: (member_expression
    object: (identifier) @_obj
    (#eq? @_obj "axios"))) @sideeffect.external

; fs.* calls (Node.js)
(call_expression
  function: (member_expression
    object: (identifier) @_obj
    (#eq? @_obj "fs"))) @sideeffect.external

; alert/prompt/confirm
(call_expression
  function: (identifier) @_func
  (#match? @_func "^(alert|prompt|confirm)$")) @sideeffect.io

; setTimeout/setInterval (side effect)
(call_expression
  function: (identifier) @_func
  (#match? @_func "^(setTimeout|setInterval|setImmediate|requestAnimationFrame)$")) @sideeffect.async

; -----------------------------------------------------------------------------
; THIS MUTATIONS
; -----------------------------------------------------------------------------

; this.attr = value
(assignment_expression
  left: (member_expression
    object: (this))) @mutation.this_attribute

; this.method()
(call_expression
  function: (member_expression
    object: (this)
    property: (property_identifier) @method.name)) @call.this_method

; -----------------------------------------------------------------------------
; ARRAY MUTATIONS
; -----------------------------------------------------------------------------

; array.push(), array.pop(), etc.
(call_expression
  function: (member_expression
    property: (property_identifier) @_method
    (#match? @_method "^(push|pop|shift|unshift|splice|reverse|sort|fill|copyWithin)$"))) @mutation.array_method

; -----------------------------------------------------------------------------
; OBJECT/MAP/SET MUTATIONS
; -----------------------------------------------------------------------------

; Object.assign(), Object.defineProperty()
(call_expression
  function: (member_expression
    object: (identifier) @_obj
    (#eq? @_obj "Object")
    property: (property_identifier) @_method
    (#match? @_method "^(assign|defineProperty|defineProperties|setPrototypeOf|freeze|seal)$"))) @mutation.object_method

; Map/Set mutations
(call_expression
  function: (member_expression
    property: (property_identifier) @_method
    (#match? @_method "^(set|add|delete|clear)$"))) @mutation.collection_method

; WeakMap/WeakSet mutations
(call_expression
  function: (member_expression
    property: (property_identifier) @_method
    (#match? @_method "^(set|add|delete)$"))) @mutation.weak_collection

; -----------------------------------------------------------------------------
; FOR LOOP VARIABLE BINDING
; -----------------------------------------------------------------------------

; for (let i of arr)
(for_in_statement
  left: (identifier) @loop.variable
  right: (_) @loop.iterable) @loop.for_in

; for (let i = 0; ...)
(for_statement
  initializer: (lexical_declaration
    (variable_declarator
      name: (identifier) @loop.variable))) @loop.for

; for...of with destructuring
(for_in_statement
  left: [(object_pattern) (array_pattern)] @loop.destructure) @loop.destructure_for

; -----------------------------------------------------------------------------
; COMPREHENSION-LIKE PATTERNS
; -----------------------------------------------------------------------------

; Array map/filter/reduce callbacks
(call_expression
  function: (member_expression
    property: (property_identifier) @_method
    (#match? @_method "^(map|filter|reduce|forEach|find|findIndex|some|every|flatMap)$"))
  arguments: (arguments
    [(arrow_function) (function_expression)] @callback)) @iteration.callback

; -----------------------------------------------------------------------------
; SPREAD OPERATIONS (potential mutation)
; -----------------------------------------------------------------------------

; Object spread mutation { ...obj, newProp: value }
(object
  (spread_element)) @spread.object

; Array spread [...arr, newItem]
(array
  (spread_element)) @spread.array

; Function argument spread func(...args)
(call_expression
  arguments: (arguments
    (spread_element))) @spread.call

; -----------------------------------------------------------------------------
; ASYNC DATA FLOW
; -----------------------------------------------------------------------------

; await expression
(await_expression
  (_) @await.source) @await

; yield expression
(yield_expression
  (_) @yield.value) @yield

; Promise.then/catch/finally
(call_expression
  function: (member_expression
    property: (property_identifier) @_method
    (#match? @_method "^(then|catch|finally)$"))) @async.promise

; -----------------------------------------------------------------------------
; REACT STATE UPDATES (common mutations)
; -----------------------------------------------------------------------------

; setState call
(call_expression
  function: (identifier) @_func
  (#match? @_func "^set[A-Z]")) @mutation.react_setter

; dispatch (Redux)
(call_expression
  function: (identifier) @_func
  (#eq? @_func "dispatch")) @mutation.redux_dispatch

; useRef current mutation
(assignment_expression
  left: (member_expression
    property: (property_identifier) @_prop
    (#eq? @_prop "current"))) @mutation.ref_current
