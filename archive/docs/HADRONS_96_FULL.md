> ⚠️ **DEPRECATED (v5.0.0)**: This 96-Hadron taxonomy is superseded by the current 8D model:
> - **200 Atoms (D1)**: AST-level constructs (Function, Class, ForLoop, etc.)
> - **33 Roles (D3)**: Semantic purposes (Repository, Controller, Handler, etc.)
> - See: `docs/STANDARD_CODE.md` for current taxonomy
>
> *Archived for historical reference. Do not use for new classification.*

# 96 Hadrons — Standard Model do Código (v4)

Source: GROK-thread-2 (Standard Model table). This is the canonical 96-item list with continent/color, fundamental particle, hadron subtype, example, and detection rule.

| # | Continente / Cor | Partícula Fundamental | Hádron (Sub-tipo) | Exemplo real (linguagem neutro) | Regra de detecção (pseudocódigo) |
|---|------------------|-----------------------|-------------------|---------------------------------|----------------------------------|
| 1 | Data Foundations (ciano) | Bits | BitFlag | `flags & MASK_ADMIN` | bit operation + constant mask |
| 2 | Data Foundations | Bits | BitMask | `mode = 0b1010` | binary literal |
| 3 | Data Foundations | Bits | ParityBit | `__builtin_popcount(x) % 2` | popcount + mod 2 |
| 4 | Data Foundations | Bits | SignBit | `x >> 31` | arithmetic shift right 31 |
| 5 | Data Foundations | Bytes | ByteArray | `buf = bytearray(256)` | bytearray / Buffer.alloc |
| 6 | Data Foundations | Bytes | MagicBytes | `b'\x89PNG\r\n\x1a\n'` | starts with known magic |
| 7 | Data Foundations | Bytes | PaddingBytes | `pad: [u8; 7]` | fixed-size padding |
| 8 | Data Foundations | Primitives | Boolean | `is_active: bool` | type bool |
| 9 | Data Foundations | Primitives | Integer | `count: i64` | integer type |
| 10 | Data Foundations | Primitives | Float | `price: f64` | float type |
| 11 | Data Foundations | Primitives | StringLiteral | `"user-123"` | string literal |
| 12 | Data Foundations | Primitives | EnumValue | `Status::Active` | enum variant access |
| 13 | Data Foundations | Variables | LocalVar | `let total = 0;` | local declaration |
| 14 | Foundations | Variables | Parameter | `fn process(id: UUID)` | function parameter |
| 15 | Foundations | Variables | InstanceField | `this.balance` | this/self field access |
| 16 | Foundations | Variables | StaticField | `Config.MAX_RETRIES` | static/class field |
| 17 | Foundations | Variables | GlobalVar | `GLOBAL_CACHE` | module-level mutable |
| 18 | Logic & Flow (magenta) | Expressions | ArithmeticExpr | `a + b * c` | arithmetic ops |
| 19 | Logic & Flow | Expressions | CallExpr | `service.save(user)` | function call |
| 20 | Logic & Flow | Expressions | LiteralExpr | `42`, `"hello"` | literal |
| 21 | Logic & Flow | Statements | Assignment | `x = y` | = operator |
| 22 | Logic & Flow | Statements | ReturnStmt | `return result` | return keyword |
| 23 | Logic & Flow | Statements | ExpressionStmt | `logger.info(...)` | standalone call |
| 24 | Logic & Flow | Control Structures | IfBranch | `if user.is_admin` | if/else |
| 25 | Logic & Flow | Control Structures | LoopFor | `for item in list` | for loop |
| 26 | Logic & Flow | Control Structures | LoopWhile | `while running` | while loop |
| 27 | Logic & Flow | Control Structures | SwitchCase | `match action` | switch/match |
| 28 | Logic & Flow | Control Structures | TryCatch | `try { … } catch` | try/except |
| 29 | Logic & Flow | Control Structures | GuardClause | `if (!user) throw` | early return + error |
| 30 | Logic & Flow | Functions | PureFunction | `add(a,b) => a+b` | no side effects detectable |
| 31 | Logic & Flow | Functions | ImpureFunction | `saveToDB()` | I/O or mutation |
| 32 | Logic & Flow | Functions | AsyncFunction | `async fetchData()` | async/await or Promise |
| 33 | Logic & Flow | Functions | Generator | `function* ids()` | yield keyword |
| 34 | Logic & Flow | Functions | Closure | `items.map(x => x*2)` | captures outer scope |
| 35 | Logic & Flow | Functions | CommandHandler | `handle(CreateUserCommand)` | name contains Handle + Command |
| 36 | Logic & Flow | Functions | QueryHandler | `handle(GetUserQuery)` | name contains Handle + Query |
| 37 | Logic & Flow | Functions | EventHandler | `@Subscribe(UserCreated)` | @On/@Subscribe decorator |
| 38 | Logic & Flow | Functions | SagaStep | `compensateDeleteUser` | saga/orchestration pattern |
| 39 | Logic & Flow | Functions | Middleware | `authMiddleware` | next()/await next |
| 40 | Logic & Flow | Functions | Validator | `validate(schema, data)` | throws on invalid |
| 41 | Logic & Flow | Functions | Mapper | `toDto(entity)` | *To*/Map*/Convert |
| 42 | Logic & Flow | Functions | Reducer | `reduce(acc, item)` | reduce/fold |
| 43 | Organization (verde) | Aggregates | ValueObject | `Email`, `Money` | immutable + equality by value |
| 44 | Organization | Aggregates | Entity | `User`, `Order` | has identity (ID field) |
| 45 | Organization | Aggregates | AggregateRoot | `Order` with business invariants | raises domain events |
| 46 | Organization | Aggregates | ReadModel | `UserDashboardView` | only queries, no behavior |
| 47 | Organization | Aggregates | Projection | handles events → updates read model | @EventHandler on read model |
| 48 | Organization | Aggregates | DTO | `CreateUserRequest` | only data, no behavior |
| 49 | Organization | Aggregates | Factory | `UserFactory.create(...)` | static create method |
| 50 | Organization | Modules | BoundedContext | `billing/`, `identity/` | own folder + own models |
| 51 | Organization | Modules | FeatureModule | `auth.module.ts` | feature folder |
| 52 | Organization | Modules | InfrastructureAdapter | `PostgresUserRepository` | implements port |
| 53 | Organization | Modules | DomainPort | `UserRepository` interface | interface + domain name |
| 54 | Organization | Modules | ApplicationPort | `UserService` interface | used by use cases |
| 55 | Organization | Files | SourceFile | `user.py` | .py/.ts/.java |
| 56 | Organization | Files | ConfigFile | `config.yaml` | config/extension |
| 57 | Organization | Files | MigrationFile | `2024_add_users.rb` | migration pattern |
| 58 | Organization | Files | TestFile | `user.test.ts` | test/jest/spec |
| 59 | Execution (âmbar) | Executables | MainEntry | `main()`, `if __name__` | entry point |
| 60 | Execution | Executables | CLIEntry | `@click.command` | CLI decorator |
| 61 | Execution | Executables | LambdaEntry | `exports.handler` | AWS Lambda pattern |
| 62 | Execution | Executables | WorkerEntry | `consume('queue')` | background worker |
| 63 | Execution | Executables | APIHandler | `@app.get("/users")` | route decorator |
| 64 | Execution | Executables | GraphQLResolver | `Query: { user }` | GraphQL field |
| 65 | Execution | Executables | WebSocketHandler | `@socket.on('message')` | websocket event |
| 66 | Execution | Executables | ContainerEntry | `CMD ["node","app.js"]` in Dockerfile | Dockerfile ENTRYPOINT/CMD |
| 67 | Execution | Executables | KubernetesJob | `kind: Job` (YAML) | Kubernetes manifest + spec.job |
| 68 | Execution | Executables | CronJob | `schedule: "0 0 * * *"` | cron schedule field |
| 69 | Execution | Executables | MessageConsumer | `@KafkaListener`, `channel.bind` | annotation with Listener |
| 70 | Execution | Executables | QueueWorker | `worker.process(job)` | loop + queue.pop |
| 71 | Execution | Executables | BackgroundThread | `threading.Thread(target=...)` | spawn thread |
| 72 | Execution | Executables | Actor | `class MyActor(Actor)` | inherits Actor |
| 73 | Execution | Executables | Coroutine | `async def task()` | async def / async function |
| 74 | Execution | Executables | Fiber | `Fiber.schedule { ... }` | Fiber keyword |
| 75 | Execution | Executables | WebWorker | `new Worker('worker.js')` | new Worker |
| 76 | Execution | Executables | ServiceWorker | `self.addEventListener('install')` | Service Worker scope |
| 77 | Execution | Executables | ServerlessColdStart | handler first run | internal metric |
| 78 | Execution | Executables | HealthCheck | `GET /healthz` | route name contains health |
| 79 | Execution | Executables | MetricsExporter | `prometheus_client.start_http_server` | metrics library init |
| 80 | Execution | Executables | TracerProvider | `OpenTelemetry.sdk.trace` | OpenTelemetry init |
| 81 | Execution | Executables | LoggerInit | `logging.basicConfig` | global logger setup |
| 82 | Execution | Executables | ConfigLoader | `viper.ReadInConfig()` | config load call |
| 83 | Execution | Executables | DependencyInjectionContainer | `services.AddSingleton<>` | DI container registration |
| 84 | Execution | Executables | PluginLoader | `plugin.load("*.so")` | dynamic plugin load |
| 85 | Execution | Executables | MigrationRunner | `flask-migrate upgrade` | migration command |
| 86 | Execution | Executables | SeedData | `rails db:seed` | seed file execution |
| 87 | Execution | Executables | GracefulShutdown | `server.shutdown()` on SIGTERM | signal handler |
| 88 | Execution | Executables | PanicRecover | `defer recover()` | recover/defer |
| 89 | Execution | Executables | CircuitBreakerInit | `hystrix.Go()` | circuit breaker lib |
| 90 | Execution | Executables | RateLimiter | `limiter.Allow()` | rate limit call |
| 91 | Execution | Executables | CacheWarmer | preload cache on startup | cache preload loop |
| 92 | Execution | Executables | FeatureFlagCheck | `fflag.Enabled("new-ui")` | feature flag check |
| 93 | Execution | Executables | A/B Test Router | `abtest.variant("exp-123")` | A/B test routing |
| 94 | Execution | Executables | CanaryDeployTrigger | `if canary_rollout` | canary condition |
| 95 | Execution | Executables | ChaosMonkey | random failure injection | chaos library |
| 96 | Execution | Executables | SelfHealingProbe | liveness probe that restarts | liveness + restartPolicy |
