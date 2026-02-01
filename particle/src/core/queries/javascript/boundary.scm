; JAVASCRIPT D4_BOUNDARY QUERIES - External boundary crossing detection
; Detects I/O operations for D4:BOUNDARY dimension classification
; Values: internal, input, output, io

; -----------------------------------------------------------------------------
; INPUT BOUNDARIES - Reading from external sources
; -----------------------------------------------------------------------------

; Fetch API - GET requests
(call_expression
  function: (identifier) @_func
  (#eq? @_func "fetch")) @boundary.input.http

(call_expression
  function: (member_expression
    property: (property_identifier) @_method
    (#match? @_method "^(get|head|options)$"))) @boundary.input.http

; Axios GET
(call_expression
  function: (member_expression
    object: (identifier) @_axios
    (#eq? @_axios "axios")
    property: (property_identifier) @_method
    (#match? @_method "^(get|head|options)$"))) @boundary.input.http

; fs.readFile / fs.readFileSync (Node.js)
(call_expression
  function: (member_expression
    object: (identifier) @_fs
    (#eq? @_fs "fs")
    property: (property_identifier) @_method
    (#match? @_method "^(readFile|readFileSync|readdir|readdirSync|read|readSync)$"))) @boundary.input.file

; fsPromises.readFile
(call_expression
  function: (member_expression
    object: (member_expression
      object: (identifier) @_fs
      (#eq? @_fs "fs")
      property: (property_identifier) @_promises
      (#eq? @_promises "promises"))
    property: (property_identifier) @_method
    (#match? @_method "^(readFile|readdir)$"))) @boundary.input.file

; process.env (Node.js environment)
(member_expression
  object: (member_expression
    object: (identifier) @_process
    (#eq? @_process "process")
    property: (property_identifier) @_env
    (#eq? @_env "env"))) @boundary.input.env

; process.argv (CLI args)
(member_expression
  object: (identifier) @_process
  (#eq? @_process "process")
  property: (property_identifier) @_argv
  (#eq? @_argv "argv")) @boundary.input.cli

; readline (user input)
(call_expression
  function: (member_expression
    object: (identifier) @_readline
    (#match? @_readline "^(readline|rl)$")
    property: (property_identifier) @_method
    (#match? @_method "^(question|prompt)$"))) @boundary.input.user

; prompt() browser input
(call_expression
  function: (identifier) @_prompt
  (#eq? @_prompt "prompt")) @boundary.input.user

; JSON.parse (deserialization)
(call_expression
  function: (member_expression
    object: (identifier) @_json
    (#eq? @_json "JSON")
    property: (property_identifier) @_parse
    (#eq? @_parse "parse"))) @boundary.input.serialization

; Database reads (common ORMs)
(call_expression
  function: (member_expression
    property: (property_identifier) @_method
    (#match? @_method "^(find|findOne|findMany|findAll|findById|findByPk|findUnique|findFirst|get|query|select|fetch|aggregate)$"))) @boundary.input.database

; localStorage/sessionStorage getItem
(call_expression
  function: (member_expression
    object: (identifier) @_storage
    (#match? @_storage "^(localStorage|sessionStorage)$")
    property: (property_identifier) @_method
    (#eq? @_method "getItem"))) @boundary.input.storage

; Socket receive
(call_expression
  function: (member_expression
    property: (property_identifier) @_method
    (#match? @_method "^(on|once|addListener)$"))
  arguments: (arguments
    (string) @_event
    (#match? @_event "^['\"]?(message|data|receive)['\"]?$"))) @boundary.input.socket

; Event listeners (browser input)
(call_expression
  function: (member_expression
    property: (property_identifier) @_method
    (#eq? @_method "addEventListener"))
  arguments: (arguments
    (string) @_event
    (#match? @_event "^['\"]?(click|input|change|keydown|keyup|submit|focus|blur)['\"]?$"))) @boundary.input.dom

; -----------------------------------------------------------------------------
; OUTPUT BOUNDARIES - Writing to external destinations
; -----------------------------------------------------------------------------

; console.log and friends
(call_expression
  function: (member_expression
    object: (identifier) @_console
    (#eq? @_console "console")
    property: (property_identifier) @_method
    (#match? @_method "^(log|info|warn|error|debug|trace|table|dir)$"))) @boundary.output.stdout

; fs.writeFile / fs.writeFileSync (Node.js)
(call_expression
  function: (member_expression
    object: (identifier) @_fs
    (#eq? @_fs "fs")
    property: (property_identifier) @_method
    (#match? @_method "^(writeFile|writeFileSync|appendFile|appendFileSync|write|writeSync)$"))) @boundary.output.file

; fsPromises.writeFile
(call_expression
  function: (member_expression
    object: (member_expression
      object: (identifier) @_fs
      (#eq? @_fs "fs")
      property: (property_identifier) @_promises
      (#eq? @_promises "promises"))
    property: (property_identifier) @_method
    (#match? @_method "^(writeFile|appendFile)$"))) @boundary.output.file

; HTTP write requests (fetch with POST/PUT)
(call_expression
  function: (member_expression
    object: (identifier) @_axios
    (#eq? @_axios "axios")
    property: (property_identifier) @_method
    (#match? @_method "^(post|put|patch|delete)$"))) @boundary.output.http

; Database mutations
(call_expression
  function: (member_expression
    property: (property_identifier) @_method
    (#match? @_method "^(create|createMany|insert|insertMany|update|updateOne|updateMany|delete|deleteOne|deleteMany|save|upsert|remove|destroy|bulkCreate|bulkUpdate)$"))) @boundary.output.database

; JSON.stringify (serialization)
(call_expression
  function: (member_expression
    object: (identifier) @_json
    (#eq? @_json "JSON")
    property: (property_identifier) @_stringify
    (#eq? @_stringify "stringify"))) @boundary.output.serialization

; localStorage/sessionStorage setItem
(call_expression
  function: (member_expression
    object: (identifier) @_storage
    (#match? @_storage "^(localStorage|sessionStorage)$")
    property: (property_identifier) @_method
    (#eq? @_method "setItem"))) @boundary.output.storage

; Socket send
(call_expression
  function: (member_expression
    property: (property_identifier) @_method
    (#match? @_method "^(send|emit|write)$"))) @boundary.output.socket

; DOM manipulation
(call_expression
  function: (member_expression
    property: (property_identifier) @_method
    (#match? @_method "^(appendChild|insertBefore|removeChild|replaceChild|innerHTML|outerHTML|textContent|innerText)$"))) @boundary.output.dom

(assignment_expression
  left: (member_expression
    property: (property_identifier) @_prop
    (#match? @_prop "^(innerHTML|outerHTML|textContent|innerText|value)$"))) @boundary.output.dom

; Express/HTTP response methods
(call_expression
  function: (member_expression
    object: (identifier) @_res
    (#match? @_res "^(res|response)$")
    property: (property_identifier) @_method
    (#match? @_method "^(send|json|render|redirect|status|write|end)$"))) @boundary.output.http

; Child process (Node.js)
(call_expression
  function: (member_expression
    object: (identifier) @_cp
    (#match? @_cp "^(child_process|childProcess|cp)$")
    property: (property_identifier) @_method
    (#match? @_method "^(exec|execSync|spawn|spawnSync|fork)$"))) @boundary.output.subprocess

; Timers (side effects)
(call_expression
  function: (identifier) @_timer
  (#match? @_timer "^(setTimeout|setInterval|setImmediate)$")) @boundary.output.timer

; alert/confirm (browser output)
(call_expression
  function: (identifier) @_alert
  (#match? @_alert "^(alert|confirm)$")) @boundary.output.user
