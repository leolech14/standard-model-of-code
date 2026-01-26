; FALLBACK LAYER (D2_LAYER)

; Generic patterns that work across multiple languages
; Layers: Interface | Application | Core | Infrastructure | Test | Unknown

; INFRASTRUCTURE LAYER (Generic patterns)

; Repository pattern (naming convention)
(identifier) @_name
(#match? @_name "(Repository|Store|DAO|DataAccess|Persistence|Gateway|Adapter)$")
@layer.infrastructure.repository

; Database keywords in identifiers
(identifier) @_name
(#match? @_name "(database|db|sql|query|transaction|connection|pool)$")
@layer.infrastructure.database

; INTERFACE LAYER (Generic patterns)

; Controller/Handler naming
(identifier) @_name
(#match? @_name "(Controller|Handler|Endpoint|Router|Resource|View)$")
@layer.interface.naming

; Route-like identifiers
(identifier) @_name
(#match? @_name "(route|api|endpoint|handler)$")
@layer.interface.route

; APPLICATION LAYER (Generic patterns)

; Service pattern
(identifier) @_name
(#match? @_name "(Service|UseCase|Interactor|Orchestrator|Application|Manager)$")
@layer.application.service

; CORE/DOMAIN LAYER (Generic patterns)

; Entity/Model naming
(identifier) @_name
(#match? @_name "(Entity|Model|Domain|Aggregate|ValueObject)$")
@layer.core.entity

; TEST LAYER (Generic patterns)

; Test naming conventions
(identifier) @_name
(#match? @_name "^(test_|Test|_test$|Spec$|_spec$)")
@layer.test.function
