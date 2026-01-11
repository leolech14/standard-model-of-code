
import re
from typing import List, Dict, Any, Tuple
from collections import Counter

class ConceptExtractor:
    """
    Extracts high-level business concepts from code identifiers.
    Helps the LLM understand the 'Domain' of the software.
    """
    
    # Common technical stops words to ignore
    STOP_WORDS = {
        'get', 'set', 'is', 'has', 'do', 'make', 'create', 'update', 'delete', 'remove',
        'add', 'new', 'init', 'main', 'test', 'spec', 'mock', 'fake', 'dummy', 'util',
        'helper', 'common', 'base', 'core', 'impl', 'interface', 'abstract', 'factory',
        'builder', 'provider', 'service', 'repository', 'controller', 'manager', 'handler',
        'wrapper', 'proxy', 'adapter', 'bridge', 'facade', 'decorator', 'visitor',
        'strategy', 'observer', 'listener', 'event', 'command', 'state', 'model', 'view',
        'dto', 'entity', 'value', 'object', 'class', 'struct', 'enum', 'int', 'str', 'bool',
        'list', 'dict', 'array', 'map', 'set', 'queue', 'stack', 'tree', 'graph', 'node',
        'func', 'method', 'prop', 'arg', 'param', 'var', 'val', 'const', 'let', 'return',
        'async', 'await', 'promise', 'future', 'task', 'thread', 'process', 'run', 'start',
        'stop', 'pause', 'resume', 'print', 'log', 'debug', 'info', 'warn', 'error', 'exception'
    }

    def extract_concepts(self, nodes: List[Dict]) -> Dict[str, Any]:
        """
        Analyze node names to find dominant concepts.
        e.g. 'UserAccountController' -> 'User', 'Account'
        """
        term_counter = Counter()
        
        for node in nodes:
            name = node.get('name', '')
            # Extract distinct words
            words = self._tokenize(name)
            for word in words:
                word_lower = word.lower()
                if len(word) > 2 and word_lower not in self.STOP_WORDS:
                    term_counter[word] += 1
        
        # Get top concepts
        top_concepts = term_counter.most_common(20)
        
        # Heuristic domain classification
        domain_guess = self._guess_domain(top_concepts)
        
        return {
            "top_concepts": [{"term": t, "count": c} for t, c in top_concepts],
            "domain_inference": domain_guess
        }

    def _tokenize(self, identifier: str) -> List[str]:
        """Split CamelCase and snake_case."""
        # Split by non-alphanumeric (snake_case, kabob-case, etc)
        parts = re.split(r'[^a-zA-Z0-9]', identifier)
        tokens = []
        for part in parts:
            if not part:
                continue
            # Split CamelCase (e.g. UserAccount -> User, Account)
            # Find transitions from lower to upper
            sub_tokens = re.findall(r'[A-Z]?[a-z]+|[A-Z]+(?=[A-Z][a-z]|\d|\W|$)|\d+', part)
            if sub_tokens:
                tokens.extend(sub_tokens)
            else:
                tokens.append(part)
        return tokens

    def _guess_domain(self, top_concepts: List[Tuple[str, int]]) -> str:
        """Simple keyword matching to guess domain."""
        keywords = [t[0].lower() for t in top_concepts]
        keywords_set = set(keywords)
        
        scores = {
            "Finance/FinTech": {"money", "cash", "bank", "account", "transaction", "payment", "bill", "invoice", "tax", "rate", "currency", "wallet", "credit", "debit", "ledger", "balance"},
            "E-Commerce": {"product", "cart", "order", "checkout", "shipping", "delivery", "inventory", "stock", "catalog", "price", "discount", "coupon", "merchant", "customer"},
            "Social Media": {"post", "comment", "like", "share", "friend", "follower", "feed", "timeline", "message", "chat", "profile", "avatar", "group", "notification"},
            "DevTools/Compiler": {"parser", "ast", "token", "node", "syntax", "grammar", "compile", "scan", "lex", "symbol", "scope", "type", "error", "warning", "lint"},
            "Infrastructure/Ops": {"server", "client", "request", "response", "cluster", "deploy", "build", "container", "pod", "node", "network", "cloud", "bucket", "queue"},
            "Health/Medical": {"patient", "doctor", "appointment", "record", "diagnosis", "treatment", "prescription", "drug", "clinic", "hospital", "insurance", "claim"},
            "Gaming": {"player", "level", "score", "game", "match", "lobby", "weapon", "inventory", "item", "character", "enemy", "world", "map", "physics"}
        }
        
        best_domain = "General Software"
        max_score = 0
        
        for domain, domain_terms in scores.items():
            matches = len(keywords_set.intersection(domain_terms))
            if matches > max_score:
                max_score = matches
                best_domain = domain
        
        if max_score == 0 and keywords:
             # Fallback: Use the #1 most common term as signature? 
             # Or just General.
             pass

        return best_domain
