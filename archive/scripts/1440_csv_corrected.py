#!/usr/bin/env python3
"""
STANDARD MODEL OF CODE v13 — 1,440 RAW COMBINATIONS GENERATOR
Full 11 Dimensions + Continents CSV Generator (CORRECTED VERSION)
"""

import csv
from itertools import product
import random

# === THE 4 FUNDAMENTAL FORCES (with their 2025 canonical values) ===
RESPONSIBILITY = [
    "Create", "Read", "Update", "Delete", "Query", "List",
    "Execute", "Validate", "Compensate", "Project", "Search", "Write"
]  # 12 values

PURITY = ["Pure", "Impure", "Idempotent", "ExternalIO"]  # 4 values

BOUNDARY = [
    "Domain", "Application", "Infrastructure",
    "Adapter", "Interface", "Test"
]  # 6 values

LIFECYCLE = [
    "Singleton", "Scoped", "Transient", "Ephemeral", "Immutable"
]  # 5 values

# === THE 96 CONTINENT BASE HADRONS (Sample of 30 to reach ~1440) ===
CONTINENT_BASE_HADRONS = [
    # Data Foundations (ciano)
    ("Data Foundations", "Bits", "BitFlag", "tetrahedron + glow bit", "flags & MASK_ADMIN", "bit operation + constant mask"),
    ("Data Foundations", "Bits", "BitMask", "tetrahedron + mask overlay", "mode = 0b1010", "binary literal"),
    ("Data Foundations", "Bytes", "ByteArray", "cube + grid texture", "buf = bytearray(256)", "bytearray / Buffer.alloc"),
    ("Data Foundations", "Primitives", "Boolean", "icosahedron + binary glow", "is_active: bool", "type bool"),
    ("Data Foundations", "Primitives", "Integer", "icosahedron + metallic", "count: i64", "integer type"),
    ("Data Foundations", "Primitives", "Float", "icosahedron + soft glow", "price: f64", "float type"),
    ("Data Foundations", "Primitives", "StringLiteral", "icosahedron + text wrap", "\"user-123\"", "string literal"),
    ("Data Foundations", "Primitives", "EnumValue", "icosahedron + colored ring", "Status::Active", "enum variant access"),

    ("Foundations", "Variables", "LocalVar", "cylinder + short", "let total = 0;", "local declaration"),
    ("Foundations", "Variables", "Parameter", "cylinder + arrow tip", "fn process(id: UUID)", "function parameter"),
    ("Foundations", "Variables", "InstanceField", "cylinder + medium", "this.balance", "this/self field access"),
    ("Foundations", "Variables", "StaticField", "cylinder + tall", "Config.MAX_RETRIES", "static/class field"),
    ("Foundations", "Variables", "GlobalVar", "cylinder + glowing", "GLOBAL_CACHE", "module-level mutable"),

    # Logic & Flow (magenta)
    ("Logic & Flow", "Expressions", "ArithmeticExpr", "cone + orange glow", "a + b * c", "arithmetic ops"),
    ("Logic & Flow", "Expressions", "CallExpr", "cone + arrow out", "service.save(user)", "function call"),
    ("Logic & Flow", "Expressions", "LiteralExpr", "cone + solid", "42, \"hello\"", "literal"),

    ("Logic & Flow", "Statements", "Assignment", "cube + arrow in", "x = y", "= operator"),
    ("Logic & Flow", "Statements", "ReturnStmt", "cube + arrow up", "return result", "return keyword"),
    ("Logic & Flow", "Statements", "ExpressionStmt", "cube + neutral", "logger.info(...)", "standalone call"),

    ("Logic & Flow", "Control Structures", "IfBranch", "torus + split", "if user.is_admin", "if/else"),
    ("Logic & Flow", "Control Structures", "LoopFor", "torus + rotating", "for item in list", "for loop"),
    ("Logic & Flow", "Control Structures", "LoopWhile", "torus + pulsing", "while running", "while loop"),
    ("Logic & Flow", "Control Structures", "SwitchCase", "torus + multi-ring", "match action", "switch/match"),
    ("Logic & Flow", "Control Structures", "TryCatch", "torus + shield", "try { ... } catch", "try/except"),

    ("Logic & Flow", "Functions", "PureFunction", "octahedron + smooth", "add(a,b) => a+b", "no side effects detectable"),
    ("Logic & Flow", "Functions", "ImpureFunction", "octahedron + rough", "saveToDB()", "I/O or mutation"),
    ("Logic & Flow", "Functions", "AsyncFunction", "octahedron + orbit ring", "async fetchData()", "async/await or Promise"),
    ("Logic & Flow", "Functions", "Generator", "octahedron + spiral", "function* ids()", "yield keyword"),
    ("Logic & Flow", "Functions", "Closure", "octahedron + inner glow", "items.map(x => x*2)", "captures outer scope"),
    ("Logic & Flow", "Functions", "CommandHandler", "octahedron + gold ring", "handle(CreateUserCommand)", "name contains Handle + Command"),
    ("Logic & Flow", "Functions", "QueryHandler", "octahedron + blue ring", "handle(GetUserQuery)", "name contains Handle + Query"),
    ("Logic & Flow", "Functions", "EventHandler", "octahedron + pulse", "@Subscribe(UserCreated)", "@On/@Subscribe decorator"),
    ("Logic & Flow", "Functions", "Middleware", "octahedron + layered", "authMiddleware", "next()/await next"),
    ("Logic & Flow", "Functions", "Validator", "octahedron + shield", "validate(schema, data)", "throws on invalid"),
    ("Logic & Flow", "Functions", "Mapper", "octahedron + arrow chain", "toDto(entity)", "*To*/Map*/Convert"),

    # Organization (verde)
    ("Organization", "Aggregates", "ValueObject", "sphere + crystalline", "Email, Money", "immutable + equality by value"),
    ("Organization", "Aggregates", "Entity", "sphere + glowing core", "User, Order", "has identity (ID field)"),
    ("Organization", "Aggregates", "AggregateRoot", "sphere + gold crown", "Order with business invariants", "raises domain events"),
    ("Organization", "Aggregates", "ReadModel", "sphere + transparent", "UserDashboardView", "only queries, no behavior"),
    ("Organization", "Aggregates", "DTO", "sphere + flat", "CreateUserRequest", "only data, no behavior"),
    ("Organization", "Aggregates", "Factory", "sphere + spark", "UserFactory.create(...)", "static create method"),

    ("Organization", "Modules", "BoundedContext", "dodecahedron + thick border", "billing/, identity/", "own folder + own models"),
    ("Organization", "Modules", "FeatureModule", "dodecahedron + colored face", "auth.module.ts", "feature folder"),
    ("Organization", "Modules", "InfrastructureAdapter", "dodecahedron + plug", "PostgresUserRepository", "implements port"),
    ("Organization", "Modules", "DomainPort", "dodecahedron + socket", "UserRepository interface", "interface + domain name"),
    ("Organization", "Modules", "ApplicationPort", "dodecahedron + arrow", "UserService interface", "used by use cases"),

    ("Organization", "Files", "SourceFile", "cube + language icon", "user.py", ".py/.ts/.java"),
    ("Organization", "Files", "ConfigFile", "cube + gear", "config.yaml", "config/extension"),
    ("Organization", "Files", "MigrationFile", "cube + arrow up", "2024_add_users.rb", "migration pattern"),
    ("Organization", "Files", "TestFile", "cube + check", "user.test.ts", "test/jest/spec"),

    # Execution (âmbar)
    ("Execution", "Executables", "MainEntry", "icosahedron + crown", "main(), if __name__", "entry point"),
    ("Execution", "Executables", "CLIEntry", "icosahedron + terminal", "@click.command", "CLI decorator"),
    ("Execution", "Executables", "LambdaEntry", "icosahedron + cloud", "exports.handler", "AWS Lambda pattern"),
    ("Execution", "Executables", "WorkerEntry", "icosahedron + gear", "consume('queue')", "background worker"),
    ("Execution", "Executables", "APIHandler", "icosahedron + globe", "@app.get(\"/users\")", "route decorator"),
    ("Execution", "Executables", "GraphQLResolver", "icosahedron + graph", "Query: { user }", "GraphQL field"),
    ("Execution", "Executables", "WebSocketHandler", "icosahedron + wave", "@socket.on('message')", "websocket event"),
    ("Execution", "Executables", "ContainerEntry", "icosahedron + docker logo overlay", "CMD [\"node\",\"app.js\"] em Dockerfile", "Dockerfile ENTRYPOINT/CMD"),
    ("Execution", "Executables", "KubernetesJob", "icosahedron + helm icon", "kind: Job em YAML", "Kubernetes manifest + spec.job"),
    ("Execution", "Executables", "CronJob", "icosahedron + clock ring", "schedule: \"0 0 * * *\"", "cron schedule field"),
    ("Execution", "Executables", "MessageConsumer", "icosahedron + rabbit/kafka icon", "@KafkaListener, channel.bind", "annotation com Listener"),
    ("Execution", "Executables", "QueueWorker", "icosahedron + gear + queue arrow", "worker.process(job)", "loop + queue.pop"),
    ("Execution", "Executables", "BackgroundThread", "icosahedron + thread spiral", "threading.Thread(target=...)", "spawn thread"),
    ("Execution", "Executables", "Actor", "icosahedron + envelope", "class MyActor(Actor) (Akka, Orleans)", "herda de Actor"),
    ("Execution", "Executables", "Coroutine", "icosahedron + wave pattern", "async def task()", "async def / async function"),
    ("Execution", "Executables", "HealthCheck", "icosahedron + heartbeat", "GET /healthz", "route name contains health"),
    ("Execution", "Executables", "MetricsExporter", "icosahedron + graph icon", "prometheus_client.start_http_server", "metrics library init"),
    ("Execution", "Executables", "LoggerInit", "icosahedron + log icon", "logging.basicConfig", "global logger setup"),
    ("Execution", "Executables", "ConfigLoader", "icosahedron + config gear", "viper.ReadInConfig()", "config load call"),
    ("Execution", "Executables", "DependencyInjectionContainer", "icosahedron + syringe", "services.AddSingleton<>", "DI container registration"),
    ("Execution", "Executables", "MigrationRunner", "icosahedron + database + arrow up", "flask-migrate upgrade", "migration command"),
    ("Execution", "Executables", "SeedData", "icosahedron + seed icon", "rails db:seed", "seed file execution"),
    ("Execution", "Executables", "GracefulShutdown", "icosahedron + soft glow fade", "server.shutdown() on SIGTERM", "signal handler"),
    ("Execution", "Executables", "CircuitBreakerInit", "icosahedron + broken chain", "hystrix.Go()", "circuit breaker lib"),
    ("Execution", "Executables", "RateLimiter", "icosahedron + hourglass", "limiter.Allow()", "rate limit call"),
    ("Execution", "Executables", "CacheWarmer", "icosahedron + fire", "preload cache on startup", "cache preload loop"),
    ("Execution", "Executables", "FeatureFlagCheck", "icosahedron + toggle", "fflag.Enabled(\"new-ui\")", "feature flag check"),
    ("Execution", "Executables", "ChaosMonkey", "icosahedron + monkey face", "random failure injection", "chaos library"),
    ("Execution", "Executables", "SelfHealingProbe", "icosahedron + healing glow", "liveness probe that restarts", "liveness + restartPolicy")
]

# === THE 12 QUARK PARENTS ===
QUARK_PARENTS = {
    "Bits": "Data Foundations",
    "Bytes": "Data Foundations",
    "Primitives": "Data Foundations",
    "Variables": "Foundations",
    "Expressions": "Logic & Flow",
    "Statements": "Logic & Flow",
    "Control Structures": "Logic & Flow",
    "Functions": "Logic & Flow",
    "Aggregates": "Organization",
    "Modules": "Organization",
    "Files": "Organization",
    "Executables": "Execution"
}

def is_impossible_combo(responsibility, purity, boundary, lifecycle, base_hadron):
    """Check if this combination violates physical laws"""

    # Rule 1: Pure + ExternalIO contradiction
    if purity == "Pure" and responsibility == "ExternalIO":
        return True, "Pure function cannot have external I/O"

    # Rule 2: Immutable + Create/Update/Delete contradiction
    if lifecycle == "Immutable" and responsibility in ["Create", "Update", "Delete"]:
        return True, "Immutable cannot have mutating operations"

    # Rule 3: Singleton + Ephemeral contradiction
    if lifecycle == "Singleton" and lifecycle == "Ephemeral":
        return True, "Singleton cannot be ephemeral"

    # Rule 4: Domain + ExternalIO contradiction
    if boundary == "Domain" and responsibility == "ExternalIO":
        return True, "Domain layer must be pure"

    # Rule 5: Immutable + CommandHandler contradiction
    if lifecycle == "Immutable" and "CommandHandler" in base_hadron:
        return True, "Immutable cannot handle commands"

    # Rule 6: Entity + Pure contradiction
    if "Entity" in base_hadron and purity == "Pure":
        return True, "Entity has state, cannot be pure"

    # Rule 7: ValueObject + Create/Delete contradiction
    if "ValueObject" in base_hadron and responsibility in ["Create", "Delete"]:
        return True, "ValueObject is immutable"

    # Rule 8: QueryHandler + ExternalIO + Pure contradiction
    if "QueryHandler" in base_hadron and purity == "Pure" and responsibility == "ExternalIO":
        return True, "QueryHandler cannot be pure with external I/O"

    return False, ""

def generate_touchpoints(base_hadron, responsibility, purity, boundary, lifecycle):
    """Generate semantic touchpoints based on hadron type and forces"""

    touchpoints = []

    # Base touchpoints by hadron type
    if "Entity" in base_hadron or "AggregateRoot" in base_hadron:
        touchpoints.extend(["identity", "state"])
    elif "ValueObject" in base_hadron:
        touchpoints.extend(["immutability", "validation", "equality"])
    elif "Repository" in base_hadron:
        touchpoints.extend(["persistence", "data_access", "abstraction"])
    elif "CommandHandler" in base_hadron:
        touchpoints.extend(["mutation", "coordination", "business_logic"])
    elif "QueryHandler" in base_hadron:
        touchpoints.extend(["read_access", "optimization", "projection"])
    elif "Factory" in base_hadron:
        touchpoints.extend(["creation", "coordination", "lifecycle"])

    # Add touchpoints based on forces
    if responsibility in ["Create", "Update", "Delete"]:
        touchpoints.append("mutation")
    elif responsibility in ["Read", "Query", "List"]:
        touchpoints.append("read_access")

    if purity == "Pure":
        touchpoints.append("deterministic")
    elif purity == "ExternalIO":
        touchpoints.append("side_effects")

    if boundary == "Domain":
        touchpoints.append("business_rules")
    elif boundary == "Infrastructure":
        touchpoints.append("technical_details")

    if lifecycle == "Immutable":
        touchpoints.append("thread_safe")
    elif lifecycle == "Singleton":
        touchpoints.append("shared_state")

    return ",".join(list(set(touchpoints)))  # Remove duplicates

def calculate_rarity(base_hadron, responsibility, purity, boundary, lifecycle, is_impossible):
    """Calculate emergence rarity percentage"""

    if is_impossible:
        return 0.0

    # Base rarity by hadron type
    if "Entity" in base_hadron or "ValueObject" in base_hadron:
        base_rarity = random.uniform(75.0, 95.0)  # Common
    elif "Repository" in base_hadron or "Factory" in base_hadron:
        base_rarity = random.uniform(50.0, 80.0)  # Uncommon
    elif "CommandHandler" in base_hadron or "QueryHandler" in base_hadron:
        base_rarity = random.uniform(20.0, 50.0)  # Rare
    elif "Lambda" in base_hadron or "Kubernetes" in base_hadron:
        base_rarity = random.uniform(10.0, 30.0)  # Very rare
    elif "Chaos" in base_hadron or "SelfHealing" in base_hadron:
        base_rarity = random.uniform(1.0, 15.0)   # Extremely rare
    else:
        base_rarity = random.uniform(30.0, 70.0)  # Average

    # Modifiers based on forces
    if purity == "Pure" and boundary == "Domain":
        base_rarity += random.uniform(5.0, 15.0)  # Pure domain is common

    if lifecycle == "Immutable" and responsibility == "Read":
        base_rarity += random.uniform(10.0, 20.0)  # Immutable readers are common

    if responsibility == "Compensate":
        base_rarity -= random.uniform(10.0, 30.0)  # Compensation is rare

    return min(99.9, max(0.1, base_rarity))

def generate_visual_3d(base_shape, responsibility, purity, boundary, lifecycle, is_impossible):
    """Generate 3D visual representation"""

    if is_impossible:
        return f"{base_shape}_black_hole"

    modifiers = []

    # Purity modifiers
    if purity == "Pure":
        modifiers.append("crystalline")
    elif purity == "ExternalIO":
        modifiers.append("glowing")

    # Lifecycle modifiers
    if lifecycle == "Immutable":
        modifiers.append("frozen")
    elif lifecycle == "Singleton":
        modifiers.append("crown")
    elif lifecycle == "Ephemeral":
        modifiers.append("fade")

    # Responsibility modifiers
    if responsibility in ["Create", "Update", "Delete"]:
        modifiers.append("dynamic")
    elif responsibility in ["Query", "Read"]:
        modifiers.append("stable")

    return f"{base_shape}_{'+'.join(modifiers)}" if modifiers else base_shape

def main():
    """Generate the complete 1,440-row CSV"""

    # Set random seed for reproducibility
    random.seed(42)

    # Generate exactly 1,440 rows
    target_rows = 1440

    # Create output CSV
    with open("1440_csv.csv", "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)

        # Write header
        header = [
            "responsibility", "purity", "boundary", "lifecycle",
            "base_hadron", "quark_parent", "touchpoints",
            "is_impossible", "impossible_reason", "visual_3d",
            "emergence_rarity_2025", "continente_cor", "particula_fundamental",
            "hadron_subtipo", "forma_3d_base_variacao", "exemplo_real_linguagem_neutro",
            "regra_detecao"
        ]
        writer.writerow(header)

        # Generate all possible force combinations (12 × 4 × 6 × 5 = 1,440)
        force_combinations = list(product(RESPONSIBILITY, PURITY, BOUNDARY, LIFECYCLE))

        # Shuffle base hadrons and cycle through them
        hadrons_shuffled = CONTINENT_BASE_HADRONS.copy()
        random.shuffle(hadrons_shuffled)

        row_count = 0
        for resp, pure, bound, life in force_combinations:
            if row_count >= target_rows:
                break

            # Pick a base hadron cyclically
            continente, particle, hadron, base_3d, example, rule = hadrons_shuffled[row_count % len(hadrons_shuffled)]

            # Check if this is an impossible combination
            is_impossible, reason = is_impossible_combo(resp, pure, bound, life, hadron)

            # Generate all fields
            quark_parent = QUARK_PARENTS.get(particle, "Unknown")
            touchpoints = generate_touchpoints(hadron, resp, pure, bound, life)
            rarity = calculate_rarity(hadron, resp, pure, bound, life, is_impossible)
            visual_3d = generate_visual_3d(base_3d.split(" + ")[0], resp, pure, bound, life, is_impossible)

            row = [
                resp, pure, bound, life,
                hadron, quark_parent, touchpoints,
                str(is_impossible), reason, visual_3d,
                f"{rarity:.1f}%", continente, particle,
                hadron, base_3d, example, rule
            ]

            writer.writerow(row)
            row_count += 1

    print(f"Generated exactly {row_count} rows in 1440_csv.csv")
    print(f"Force combinations: {len(force_combinations)}")
    print(f"Base hadrons available: {len(hadrons_shuffled)}")

if __name__ == "__main__":
    main()