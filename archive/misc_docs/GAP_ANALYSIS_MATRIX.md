# Gap Analysis Matrix — Canon Roles vs Current Implementations

- Generated: 2025-12-14T06:26:35
- Canon roles: `96` (source: `HADRONS_96_FULL.md`)
- Engine types: `22` (source: `spectrometer_v12_minimal/patterns/particle_defs.json`)
- Archetype snapshot types: `66` (source: `spectrometer_v12_minimal/validation/subhadrons_384_from_canvas.csv`)
- RPBL roles present: `96` (source: `1440_csv.csv`)

## Quick Findings
- Engine ∩ Canon: 8; Engine-only: 14; Canon missing in engine: 88
- CanvasTypes ∩ Canon: 49; Canvas-only: 17; Canon missing in canvas types: 47
- Canon↔RPBL mismatch: canon_missing_in_rpbl=1 rpbl_missing_in_canon=1 (naming drift likely)

## Engine Types Not In Canon (Candidates to Add or Map)
| engine type | suggested disposition |
|---|---|
| `ApplicationService` | candidate role addition (organelle-level orchestration) |
| `Command` | candidate role addition (CQRS artifacts) or map into `DTO` |
| `Controller` | map to `APIHandler` (or add `Controller` as separate presentation role) |
| `DomainService` | candidate role addition (organelle-level orchestration) |
| `Mediator` | candidate role addition |
| `Observer` | candidate role addition |
| `Policy` | candidate role addition |
| `Query` | candidate role addition (CQRS artifacts) or map into `DTO` |
| `Repository` | map to `DomainPort` (or add `Repository` explicitly) |
| `RepositoryImpl` | candidate role addition |
| `Service` | candidate role addition (organelle-level orchestration) |
| `Specification` | candidate role addition |
| `Strategy` | candidate role addition |
| `UseCase` | candidate role addition (organelle-level orchestration) |

## Canvas Types Not In Canon (Archetype-only Vocabulary)
| canvas type | count | suggested disposition |
|---|---:|---|
| `Service` | 12 | candidate role addition or smell-only type |
| `Cache` | 7 | candidate role addition or smell-only type |
| `ContextMap` | 7 | strategic DDD concept (candidate role addition) |
| `DomainEvent` | 7 | candidate role addition or smell-only type |
| `Module` | 6 | candidate role addition or smell-only type |
| `ABTestRouter` | 5 | candidate role addition or smell-only type |
| `Bulkhead` | 5 | resilience pattern (likely smell/ops catalog, not core role) |
| `RepositoryImpl` | 5 | candidate role addition or smell-only type |
| `Retry` | 5 | resilience pattern (likely smell/ops catalog, not core role) |
| `Timeout` | 5 | resilience pattern (likely smell/ops catalog, not core role) |
| `Adapter` | 4 | candidate role addition or smell-only type |
| `Outbox` | 3 | integration pattern (candidate archetype; probably not a base role) |
| `Policy` | 3 | candidate role addition or smell-only type |
| `Specification` | 3 | candidate role addition or smell-only type |
| `SharedKernel` | 2 | strategic DDD concept (candidate role addition) |
| `UseCase` | 2 | candidate role addition or smell-only type |
| `TestFunction` | 1 | candidate role addition or smell-only type |

## Canon Role Matrix (96)
| # | continent | family | hadron | in RPBL | in engine | in canvas types | notes |
|---:|---|---|---|:---:|:---:|:---:|---|
| 1 | Data Foundations (ciano) | Bits | `BitFlag` | ✅ | ❌ | ❌ | missing in both (no current support) |
| 2 | Data Foundations | Bits | `BitMask` | ✅ | ❌ | ❌ | missing in both (no current support) |
| 3 | Data Foundations | Bits | `ParityBit` | ✅ | ❌ | ❌ | missing in both (no current support) |
| 4 | Data Foundations | Bits | `SignBit` | ✅ | ❌ | ❌ | missing in both (no current support) |
| 5 | Data Foundations | Bytes | `ByteArray` | ✅ | ❌ | ❌ | missing in both (no current support) |
| 6 | Data Foundations | Bytes | `MagicBytes` | ✅ | ❌ | ❌ | missing in both (no current support) |
| 7 | Data Foundations | Bytes | `PaddingBytes` | ✅ | ❌ | ❌ | missing in both (no current support) |
| 8 | Data Foundations | Primitives | `Boolean` | ✅ | ❌ | ❌ | missing in both (no current support) |
| 9 | Data Foundations | Primitives | `Integer` | ✅ | ❌ | ❌ | missing in both (no current support) |
| 10 | Data Foundations | Primitives | `Float` | ✅ | ❌ | ❌ | missing in both (no current support) |
| 11 | Data Foundations | Primitives | `StringLiteral` | ✅ | ❌ | ❌ | missing in both (no current support) |
| 12 | Data Foundations | Primitives | `EnumValue` | ✅ | ❌ | ❌ | missing in both (no current support) |
| 13 | Data Foundations | Variables | `LocalVar` | ✅ | ❌ | ❌ | missing in both (no current support) |
| 14 | Foundations | Variables | `Parameter` | ✅ | ❌ | ❌ | missing in both (no current support) |
| 15 | Foundations | Variables | `InstanceField` | ✅ | ❌ | ❌ | missing in both (no current support) |
| 16 | Foundations | Variables | `StaticField` | ✅ | ❌ | ❌ | missing in both (no current support) |
| 17 | Foundations | Variables | `GlobalVar` | ✅ | ❌ | ❌ | missing in both (no current support) |
| 18 | Logic & Flow (magenta) | Expressions | `ArithmeticExpr` | ✅ | ❌ | ❌ | missing in both (no current support) |
| 19 | Logic & Flow | Expressions | `CallExpr` | ✅ | ❌ | ❌ | missing in both (no current support) |
| 20 | Logic & Flow | Expressions | `LiteralExpr` | ✅ | ❌ | ❌ | missing in both (no current support) |
| 21 | Logic & Flow | Statements | `Assignment` | ✅ | ❌ | ❌ | missing in both (no current support) |
| 22 | Logic & Flow | Statements | `ReturnStmt` | ✅ | ❌ | ❌ | missing in both (no current support) |
| 23 | Logic & Flow | Statements | `ExpressionStmt` | ✅ | ❌ | ❌ | missing in both (no current support) |
| 24 | Logic & Flow | Control Structures | `IfBranch` | ✅ | ❌ | ❌ | missing in both (no current support) |
| 25 | Logic & Flow | Control Structures | `LoopFor` | ✅ | ❌ | ❌ | missing in both (no current support) |
| 26 | Logic & Flow | Control Structures | `LoopWhile` | ✅ | ❌ | ❌ | missing in both (no current support) |
| 27 | Logic & Flow | Control Structures | `SwitchCase` | ✅ | ❌ | ❌ | missing in both (no current support) |
| 28 | Logic & Flow | Control Structures | `TryCatch` | ✅ | ❌ | ❌ | missing in both (no current support) |
| 29 | Logic & Flow | Control Structures | `GuardClause` | ✅ | ❌ | ❌ | missing in both (no current support) |
| 30 | Logic & Flow | Functions | `PureFunction` | ✅ | ❌ | ❌ | missing in both (no current support) |
| 31 | Logic & Flow | Functions | `ImpureFunction` | ✅ | ❌ | ❌ | missing in both (no current support) |
| 32 | Logic & Flow | Functions | `AsyncFunction` | ✅ | ❌ | ❌ | missing in both (no current support) |
| 33 | Logic & Flow | Functions | `Generator` | ✅ | ❌ | ❌ | missing in both (no current support) |
| 34 | Logic & Flow | Functions | `Closure` | ✅ | ❌ | ❌ | missing in both (no current support) |
| 35 | Logic & Flow | Functions | `CommandHandler` | ✅ | ❌ | ✅ | engine has `Command`/`Query` but not handlers (taxonomy gap); present in archetype snapshot; engine taxonomy missing |
| 36 | Logic & Flow | Functions | `QueryHandler` | ✅ | ❌ | ✅ | engine has `Command`/`Query` but not handlers (taxonomy gap); present in archetype snapshot; engine taxonomy missing |
| 37 | Logic & Flow | Functions | `EventHandler` | ✅ | ✅ | ✅ | direct engine type |
| 38 | Logic & Flow | Functions | `SagaStep` | ✅ | ❌ | ✅ | present in archetype snapshot; engine taxonomy missing |
| 39 | Logic & Flow | Functions | `Middleware` | ✅ | ❌ | ❌ | missing in both (no current support) |
| 40 | Logic & Flow | Functions | `Validator` | ✅ | ❌ | ✅ | present in archetype snapshot; engine taxonomy missing |
| 41 | Logic & Flow | Functions | `Mapper` | ✅ | ❌ | ❌ | missing in both (no current support) |
| 42 | Logic & Flow | Functions | `Reducer` | ✅ | ❌ | ❌ | missing in both (no current support) |
| 43 | Organization (verde) | Aggregates | `ValueObject` | ✅ | ✅ | ✅ | direct engine type |
| 44 | Organization | Aggregates | `Entity` | ✅ | ✅ | ✅ | direct engine type |
| 45 | Organization | Aggregates | `AggregateRoot` | ✅ | ✅ | ✅ | direct engine type |
| 46 | Organization | Aggregates | `ReadModel` | ✅ | ✅ | ✅ | direct engine type |
| 47 | Organization | Aggregates | `Projection` | ✅ | ✅ | ✅ | direct engine type |
| 48 | Organization | Aggregates | `DTO` | ✅ | ✅ | ✅ | direct engine type |
| 49 | Organization | Aggregates | `Factory` | ✅ | ✅ | ✅ | direct engine type |
| 50 | Organization | Modules | `BoundedContext` | ✅ | ❌ | ✅ | present in archetype snapshot; engine taxonomy missing |
| 51 | Organization | Modules | `FeatureModule` | ✅ | ❌ | ❌ | missing in both (no current support) |
| 52 | Organization | Modules | `InfrastructureAdapter` | ✅ | ❌ | ✅ | engine has `RepositoryImpl` (possible mapping); present in archetype snapshot; engine taxonomy missing |
| 53 | Organization | Modules | `DomainPort` | ✅ | ❌ | ✅ | engine has `Repository` (possible mapping); present in archetype snapshot; engine taxonomy missing |
| 54 | Organization | Modules | `ApplicationPort` | ✅ | ❌ | ❌ | missing in both (no current support) |
| 55 | Organization | Files | `SourceFile` | ✅ | ❌ | ❌ | missing in both (no current support) |
| 56 | Organization | Files | `ConfigFile` | ✅ | ❌ | ❌ | missing in both (no current support) |
| 57 | Organization | Files | `MigrationFile` | ✅ | ❌ | ❌ | missing in both (no current support) |
| 58 | Organization | Files | `TestFile` | ✅ | ❌ | ❌ | missing in both (no current support) |
| 59 | Execution (âmbar) | Executables | `MainEntry` | ✅ | ❌ | ✅ | present in archetype snapshot; engine taxonomy missing |
| 60 | Execution | Executables | `CLIEntry` | ✅ | ❌ | ✅ | present in archetype snapshot; engine taxonomy missing |
| 61 | Execution | Executables | `LambdaEntry` | ✅ | ❌ | ✅ | present in archetype snapshot; engine taxonomy missing |
| 62 | Execution | Executables | `WorkerEntry` | ✅ | ❌ | ✅ | present in archetype snapshot; engine taxonomy missing |
| 63 | Execution | Executables | `APIHandler` | ✅ | ❌ | ✅ | engine has `Controller` (possible mapping); present in archetype snapshot; engine taxonomy missing |
| 64 | Execution | Executables | `GraphQLResolver` | ✅ | ❌ | ✅ | present in archetype snapshot; engine taxonomy missing |
| 65 | Execution | Executables | `WebSocketHandler` | ✅ | ❌ | ✅ | present in archetype snapshot; engine taxonomy missing |
| 66 | Execution | Executables | `ContainerEntry` | ✅ | ❌ | ✅ | present in archetype snapshot; engine taxonomy missing |
| 67 | Execution | Executables | `KubernetesJob` | ✅ | ❌ | ✅ | present in archetype snapshot; engine taxonomy missing |
| 68 | Execution | Executables | `CronJob` | ✅ | ❌ | ✅ | present in archetype snapshot; engine taxonomy missing |
| 69 | Execution | Executables | `MessageConsumer` | ✅ | ❌ | ✅ | present in archetype snapshot; engine taxonomy missing |
| 70 | Execution | Executables | `QueueWorker` | ✅ | ❌ | ✅ | present in archetype snapshot; engine taxonomy missing |
| 71 | Execution | Executables | `BackgroundThread` | ✅ | ❌ | ✅ | present in archetype snapshot; engine taxonomy missing |
| 72 | Execution | Executables | `Actor` | ✅ | ❌ | ✅ | present in archetype snapshot; engine taxonomy missing |
| 73 | Execution | Executables | `Coroutine` | ✅ | ❌ | ❌ | missing in both (no current support) |
| 74 | Execution | Executables | `Fiber` | ✅ | ❌ | ❌ | missing in both (no current support) |
| 75 | Execution | Executables | `WebWorker` | ✅ | ❌ | ✅ | present in archetype snapshot; engine taxonomy missing |
| 76 | Execution | Executables | `ServiceWorker` | ✅ | ❌ | ✅ | present in archetype snapshot; engine taxonomy missing |
| 77 | Execution | Executables | `ServerlessColdStart` | ✅ | ❌ | ❌ | missing in both (no current support) |
| 78 | Execution | Executables | `HealthCheck` | ✅ | ❌ | ✅ | present in archetype snapshot; engine taxonomy missing |
| 79 | Execution | Executables | `MetricsExporter` | ✅ | ❌ | ✅ | present in archetype snapshot; engine taxonomy missing |
| 80 | Execution | Executables | `TracerProvider` | ✅ | ❌ | ✅ | present in archetype snapshot; engine taxonomy missing |
| 81 | Execution | Executables | `LoggerInit` | ✅ | ❌ | ✅ | present in archetype snapshot; engine taxonomy missing |
| 82 | Execution | Executables | `ConfigLoader` | ✅ | ❌ | ✅ | present in archetype snapshot; engine taxonomy missing |
| 83 | Execution | Executables | `DependencyInjectionContainer` | ✅ | ❌ | ✅ | present in archetype snapshot; engine taxonomy missing |
| 84 | Execution | Executables | `PluginLoader` | ✅ | ❌ | ✅ | present in archetype snapshot; engine taxonomy missing |
| 85 | Execution | Executables | `MigrationRunner` | ✅ | ❌ | ✅ | present in archetype snapshot; engine taxonomy missing |
| 86 | Execution | Executables | `SeedData` | ✅ | ❌ | ✅ | present in archetype snapshot; engine taxonomy missing |
| 87 | Execution | Executables | `GracefulShutdown` | ✅ | ❌ | ✅ | present in archetype snapshot; engine taxonomy missing |
| 88 | Execution | Executables | `PanicRecover` | ✅ | ❌ | ✅ | present in archetype snapshot; engine taxonomy missing |
| 89 | Execution | Executables | `CircuitBreakerInit` | ✅ | ❌ | ✅ | present in archetype snapshot; engine taxonomy missing |
| 90 | Execution | Executables | `RateLimiter` | ✅ | ❌ | ✅ | present in archetype snapshot; engine taxonomy missing |
| 91 | Execution | Executables | `CacheWarmer` | ✅ | ❌ | ✅ | present in archetype snapshot; engine taxonomy missing |
| 92 | Execution | Executables | `FeatureFlagCheck` | ✅ | ❌ | ✅ | present in archetype snapshot; engine taxonomy missing |
| 93 | Execution | Executables | `A/B Test Router` | ❌ | ❌ | ❌ | missing in both (no current support) |
| 94 | Execution | Executables | `CanaryDeployTrigger` | ✅ | ❌ | ✅ | present in archetype snapshot; engine taxonomy missing |
| 95 | Execution | Executables | `ChaosMonkey` | ✅ | ❌ | ✅ | present in archetype snapshot; engine taxonomy missing |
| 96 | Execution | Executables | `SelfHealingProbe` | ✅ | ❌ | ✅ | present in archetype snapshot; engine taxonomy missing |

## Prioritized Gaps (High ROI)
- Add artifact-level extraction (config/infra/runtime) to cover many Execution roles.
- Add atom-level extraction (statements/expressions/variables) to support “physics” signals (complexity/flow).
- Unify vocab: either (a) expand the Role Catalog beyond 96, or (b) map engine/canvas extras into existing roles explicitly.
- Split violations into `forbidden` (hard) vs `smells` (soft) to stabilize the model.

