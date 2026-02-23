package main

import (
	"encoding/json"
	"fmt"
	"io"
	"os"

	"github.com/dave/dst"
	"github.com/dave/dst/decorator"
)

type Mutation struct {
	Action     string `json:"action"`
	TargetNode string `json:"target_node"`
	NewBody    string `json:"new_body"`
}

type Request struct {
	TargetFile string     `json:"target_file"`
	SourceCode string     `json:"source_code"` // Inject from python
	Mutations  []Mutation `json:"mutations"`
}

func main() {
	inputData, err := io.ReadAll(os.Stdin)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error reading stdin: %v\n", err)
		os.Exit(1)
	}

	var req Request
	if err := json.Unmarshal(inputData, &req); err != nil {
		fmt.Fprintf(os.Stderr, "Error parsing JSON: %v\n", err)
		os.Exit(1)
	}

	f, err := decorator.Parse(req.SourceCode)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error parsing source code: %v\n", err)
		os.Exit(1)
	}

	for _, decl := range f.Decls {
		if funcDecl, ok := decl.(*dst.FuncDecl); ok {
			funcName := funcDecl.Name.Name
			for _, mut := range req.Mutations {
				if mut.TargetNode == funcName {
					// Handling action
					if mut.Action == "replace_function_body" && mut.NewBody != "" {
						wrappedCode := "package dummy\n" + mut.NewBody
						newF, err := decorator.Parse(wrappedCode)
						if err == nil && len(newF.Decls) > 0 {
							if newFunc, ok := newF.Decls[0].(*dst.FuncDecl); ok {
								// We preserve the original signature, but drop-in the new body
								funcDecl.Body = newFunc.Body
							}
						} else {
							fmt.Fprintf(os.Stderr, "Error parsing new_body snippet for %s: %v\n", funcName, err)
						}
					}
					// Add delete_node logic later if needed
				}
			}
		}
	}

	// Render directly to stdout, which python intercepts
	if err := decorator.Print(f); err != nil {
		fmt.Fprintf(os.Stderr, "Error printing output: %v\n", err)
		os.Exit(1)
	}
}
