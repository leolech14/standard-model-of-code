const { Project, SyntaxKind } = require("ts-morph");

let input = "";
process.stdin.setEncoding('utf8');
process.stdin.on('data', chunk => { input += chunk; });
process.stdin.on('end', () => {
    try {
        const req = JSON.parse(input);
        const { target_file, mutations, source_code } = req;
        const project = new Project();

        // Use in-memory source code provided by the dispatcher
        const sf = project.createSourceFile(target_file, source_code, { overwrite: true });

        for (const mut of mutations) {
            let targetNode = sf.getClass(mut.target_node)
                || sf.getFunction(mut.target_node)
                || sf.getInterface(mut.target_node)
                || sf.getTypeAlias(mut.target_node);

            if (!targetNode) {
                // Try finding a method in any class
                for (const cls of sf.getClasses()) {
                    const method = cls.getMethod(mut.target_node);
                    if (method) {
                        targetNode = method;
                        break;
                    }
                }
            }

            if (!targetNode) {
                // Try variable declarations (like const myFunc = () => {})
                const varDec = sf.getVariableDeclaration(mut.target_node);
                if (varDec) {
                    targetNode = varDec;
                }
            }

            if (!targetNode) {
                console.error(`Warning: Target node '${mut.target_node}' not found.`);
                continue;
            }

            if (mut.action === "delete_node") {
                if (targetNode.getKind() === SyntaxKind.VariableDeclaration) {
                    const statement = targetNode.getVariableStatement();
                    if (statement && statement.getDeclarations().length === 1) {
                        statement.remove();
                    } else {
                        targetNode.remove();
                    }
                } else {
                    targetNode.remove();
                }
            } else if (mut.action === "replace_function_body" || mut.action === "replace_class_body") {
                if (mut.new_body) {
                    // Replaces the entire function/class definition with the new text
                    targetNode.replaceWithText(mut.new_body);
                }
            }
        }

        // Print the modified source code to stdout
        process.stdout.write(sf.getFullText());
    } catch (e) {
        console.error("Adapter Error:", e.message);
        process.exit(1);
    }
});
