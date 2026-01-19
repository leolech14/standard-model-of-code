import json
import re

# 1. Define the Mapping (Hadron Type -> Region)
# Extracted from HADRONS_96_FULL.md
TYPE_TO_REGION = {
    # DATA (1-17)
    "BitFlag": "DATA", "BitMask": "DATA", "ParityBit": "DATA", "SignBit": "DATA",
    "ByteArray": "DATA", "MagicBytes": "DATA", "PaddingBytes": "DATA",
    "Boolean": "DATA", "Integer": "DATA", "Float": "DATA", "StringLiteral": "DATA", "EnumValue": "DATA",
    "LocalVar": "DATA", "Parameter": "DATA", "InstanceField": "DATA", "StaticField": "DATA", "GlobalVar": "DATA",
    
    # LOGIC (18-42)
    "ArithmeticExpr": "LOGIC", "CallExpr": "LOGIC", "LiteralExpr": "LOGIC",
    "Assignment": "LOGIC", "ReturnStmt": "LOGIC", "ExpressionStmt": "LOGIC",
    "IfBranch": "LOGIC", "LoopFor": "LOGIC", "LoopWhile": "LOGIC", "SwitchCase": "LOGIC", "TryCatch": "LOGIC", "GuardClause": "LOGIC",
    "PureFunction": "LOGIC", "ImpureFunction": "LOGIC", "AsyncFunction": "LOGIC", "Generator": "LOGIC", "Closure": "LOGIC",
    "CommandHandler": "LOGIC", "QueryHandler": "LOGIC", "EventHandler": "LOGIC", "SagaStep": "LOGIC", "Middleware": "LOGIC",
    "Validator": "LOGIC", "Mapper": "LOGIC", "Reducer": "LOGIC",
    
    # ORG (43-58)
    "ValueObject": "ORG", "Entity": "ORG", "AggregateRoot": "ORG", "ReadModel": "ORG", "Projection": "ORG", "DTO": "ORG", "Factory": "ORG",
    "BoundedContext": "ORG", "FeatureModule": "ORG", "InfrastructureAdapter": "ORG", "DomainPort": "ORG", "ApplicationPort": "ORG",
    "SourceFile": "ORG", "ConfigFile": "ORG", "MigrationFile": "ORG", "TestFile": "ORG",
    # Additional ContextMap items inferred
    "ContextMap": "ORG", "SharedKernel": "ORG", "Policy": "ORG", "Specification": "ORG", "DependencyInjectionContainer": "ORG", # DI usually Exec or Org, headers say Exec implies DI Container? Wait, ID 83 is DI Container in Exec.
    # Let's check overrides based on actual file data
    
    # EXEC (59-96)
    "MainEntry": "EXEC", "CLIEntry": "EXEC", "LambdaEntry": "EXEC", "WorkerEntry": "EXEC",
    "APIHandler": "EXEC", "GraphQLResolver": "EXEC", "WebSocketHandler": "EXEC", "ContainerEntry": "EXEC",
    "KubernetesJob": "EXEC", "CronJob": "EXEC", "MessageConsumer": "EXEC", "QueueWorker": "EXEC",
    "BackgroundThread": "EXEC", "Actor": "EXEC", "Coroutine": "EXEC", "Fiber": "EXEC", "WebWorker": "EXEC", "ServiceWorker": "EXEC",
    "ServerlessColdStart": "EXEC", "HealthCheck": "EXEC", "MetricsExporter": "EXEC", "TracerProvider": "EXEC",
    "LoggerInit": "EXEC", "ConfigLoader": "EXEC", "DependencyInjectionContainer": "EXEC", "PluginLoader": "EXEC",
    "MigrationRunner": "EXEC", "SeedData": "EXEC", "GracefulShutdown": "EXEC", "PanicRecover": "EXEC",
    "CircuitBreakerInit": "EXEC", "RateLimiter": "EXEC", "CacheWarmer": "EXEC", "FeatureFlagCheck": "EXEC",
    "ABTestRouter": "EXEC", "CanaryDeployTrigger": "EXEC", "ChaosMonkey": "EXEC", "SelfHealingProbe": "EXEC",
    
    # Ambiguous / Missing in Table but present in Extract
    "Adapter": "ORG", # Likely InfrastructureAdapter
    "Outbox": "EXEC", # Pattern, usually infra/exec
    "Cache": "EXEC",
    "Bulkhead": "EXEC",
    "Retry": "EXEC",
    "Timeout": "EXEC",
    "TestFunction": "ORG", # TestFile?
    "UseCase": "LOGIC", # Application Service?
    "DomainService": "ORG", # or Logic? Service is usually logic but Domain Service is Org structure? table says PureFunction/ImpureFunction.
    "Service": "ORG", # Service in table? ID 54 UserService interface (Port)
    "DomainEvent": "ORG", # Logic has EventHandler, but Event itself is Org? Table doesn't list DomainEvent as Hadron. It lists EventHandler. Wait.
    # Let's double check DomainEvent. "SagaStep", "EventHandler".
    # UserRegisteredEvent is listed as "EventHandler" in extraction? No.
    # Line 57: "Type: DomainEvent".
    # I'll enable "DomainEvent" -> ORG (Structure).
}

# Fix missing mappings
TYPE_TO_REGION["DomainEvent"] = "ORG"
TYPE_TO_REGION["Service"] = "ORG" 
TYPE_TO_REGION["Adapter"] = "ORG"
TYPE_TO_REGION["Outbox"] = "EXEC"
TYPE_TO_REGION["Cache"] = "EXEC"
TYPE_TO_REGION["Bulkhead"] = "EXEC"
TYPE_TO_REGION["Retry"] = "EXEC"
TYPE_TO_REGION["Timeout"] = "EXEC"
TYPE_TO_REGION["TestFunction"] = "ORG"
TYPE_TO_REGION["UseCase"] = "LOGIC"

def get_subhadron_name(text):
    # Extract "### 🏆 Name" or "### ⚫ Name"
    # Remove icon
    match = re.search(r'### [^ ]+ (.+?)\\n', text)
    if match:
        return match.group(1).strip()
    return "Unknown"

def get_type(text):
    match = re.search(r'Type: (.+?)"', text)
    if not match:
         match = re.search(r'Type: (.+?)\\n', text)
    if match:
        return match.group(1).strip()
    return "Unknown"

def generate_mermaid_for_region(region, subhadrons):
    # Group by Type
    grouped = {}
    for name, htype in subhadrons:
        if htype not in grouped: grouped[htype] = []
        grouped[htype].append(name)
        
    mermaid = "classDiagram\n"
    mermaid += "    direction TB\n"
    
    for htype, subs in grouped.items():
        # Clean type name
        clean_type = htype.replace(" ", "_")
        mermaid += f"    class {clean_type} {{\n"
        for sub in subs:
            # Clean sub name (take up to 30 chars)
            clean_sub = sub.replace("_", " ")[:40]
            # Check for Antimatter
            prefix = "+"
            if "ANTIMATTER" in sub or "Paradox" in sub: # Heuristic, actually use Name
                # We don't have the full text here easily, just name.
                # Names started with icons in extracted text, but we stripped them.
                pass
            
            mermaid += f"        {clean_sub}\n"
        mermaid += "    }\n"
        
    return mermaid

def inject_maps(file_path):
    print("Reading extracted subhadrons...")
    subhadrons = [] # List of (Name, Type, FullText)
    
    with open('/Users/lech/PROJECTS_all/PROJECT_elements/extracted_subhadrons.txt', 'r') as f:
        content = f.read()
        # Split by "text":
        parts = content.split('"text":')
        for p in parts:
            if not p.strip(): continue
            p = '"text":' + p
            
            name = get_subhadron_name(p)
            htype = get_type(p)
            
            if name != "Unknown":
                subhadrons.append((name, htype))
                
    print(f"Parsed {len(subhadrons)} subhadrons.")
    
    # Categorize
    by_region = {"DATA": [], "LOGIC": [], "ORG": [], "EXEC": []}
    
    for name, htype in subhadrons:
        reg = TYPE_TO_REGION.get(htype, "UNKNOWN")
        if reg in by_region:
            by_region[reg].append((name, htype))
        else:
            # Default to Logic if unknown? or Print warning
            # print(f"Unknown Region for Type: {htype} ({name})")
            # Fallback based on visual check, or dump to Logic
            pass
            
    # Generate Narratives
    nodes_to_inject = []
    
    # Unified Diagram Update (Move Up)
    # We will just edit the JSON directly for the Unified Node if it exists
    
    # New Map Nodes
    # We need coordinates of the Regions to place them "On Top"
    # Logic: -5920, -4480. Header at -5480.
    # Exec: -4650, -5850. Header at ...
    
    # Let's read the canvas to get current group positions
    with open(file_path, 'r') as f:
        data = json.load(f)
        
    # Update Unified Diagram POS
    for n in data['nodes']:
        if n['id'] == 'unified_theory_diagram':
            n['y'] = -10000 # Move WAY up
            n['height'] = 2500
            n['width'] = 2500
            n['x'] = -500
            
    # Locate groups
    groups = {n['id']: n for n in data['nodes'] if n['type'] == 'group'}
    
    # Map Region Code to Group ID
    region_groups = {
        "LOGIC": "group_logic",
        "ORG": "group_org", # Need to find the exact ID. Usually inferred.
        "EXEC": "group_exec",
        "DATA": "group_data"
    }
    
    # Determine IDs dynamically if standard names fail
    for n in data['nodes']:
        if n['type'] == 'group':
            if n.get('label') == 'LOGIC REGION': region_groups['LOGIC'] = n['id']
            if n.get('label') == 'ORGANIZATION REGION': region_groups['ORG'] = n['id'] # Check label
            # Based on previous scripts, IDs were group_logic, etc.
            
            # Use color as fallback
            if n.get('color') == '1': region_groups['LOGIC'] = n['id']
            if n.get('color') == '4': region_groups['ORG'] = n['id']
            if n.get('color') == '3': region_groups['EXEC'] = n['id']
            if n.get('color') == '5': region_groups['DATA'] = n['id']
            
    for reg, items in by_region.items():
        if not items: 
            print(f"Skipping {reg} - No items found.")
            continue
        
        target_x = 0
        target_y = 0
        target_w = 2000
        target_c = "1"
        found = False
        
        # Strategy 1: Find Group
        gid = region_groups.get(reg)
        if gid:
            gnode = next((n for n in data['nodes'] if n['id'] == gid), None)
            if gnode:
                target_x = gnode['x']
                target_y = gnode['y']
                target_w = gnode.get('width', 2000)
                target_c = gnode.get('color', '1')
                found = True
        
        # Strategy 2: Find Header (Fallback)
        if not found:
            header_id = f"header_theory_{reg.lower()}"
            hnode = next((n for n in data['nodes'] if n['id'] == header_id), None)
            if hnode:
                print(f"Fallback: Found header for {reg}")
                target_x = hnode['x']
                target_y = hnode['y'] # Header is already above group
                target_w = hnode.get('width', 2000)
                target_c = hnode.get('color', '1')
                found = True
                
        if not found:
            print(f"Could not locate region {reg} (Group or Header not found).")
            continue
        
        # Generate Mermaid
        mermaid = generate_mermaid_for_region(reg, items)
        
        # Place above the target
        # If target was group, we went -3000.
        # If target was header, header is already -1000 from group.
        # So we want to be ABOVE header.
        # Header is at Y. Map should be Y - 1800 - Gap.
        
        new_y = target_y - 2000
        
        content = f"# {reg} SUB-HADRONS ({len(items)})\\n"
        content += f"**The Basic Units of {reg}**\\n\\n"
        content += "```mermaid\\n" + mermaid + "\\n```"
        
        new_node = {
            "id": f"subhadron_map_{reg.lower()}",
            "type": "text",
            "text": content,
            "x": target_x,
            "y": new_y,
            "width": target_w,
            "height": 1800,
            "color": target_c
        }
        
        nodes_to_inject.append(new_node)
        
    # Remove old map nodes
    data['nodes'] = [n for n in data['nodes'] if not n['id'].startswith('subhadron_map_')]
    data['nodes'].extend(nodes_to_inject)
    
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=4)
        
    print(f"Injected {len(nodes_to_inject)} map nodes.")
    print("Moved Unified Diagram to y=-10000.")

if __name__ == "__main__":
    inject_maps("/Users/lech/PROJECTS_all/PROJECT_elements/THEORY_COMPLETE.canvas")
