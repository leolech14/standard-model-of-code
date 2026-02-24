package main

import (
	"bytes"
	"encoding/json"
	"fmt"
	"go/parser"
	"go/token"
	"io/ioutil"
	"os"

	"github.com/dave/dst"
	"github.com/dave/dst/decorator"
)

type MutationOperation struct {
	Action     string `json:"action"`
	TargetNode string `json:"target_node"`
	NewBody    string `json:"new_body,omitempty"`
}

type MutationRequest struct {
	TargetFile string              `json:"target_file"`
	SourceCode string              `json:"source_code"` // Injected by compiler.py
	Mutations  []MutationOperation `json:"mutations"`
}

func main() {
	// Read JSON from stdin
	inputData, err := ioutil.ReadAll(os.Stdin)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error reading stdin: %v\n", err)
		os.Exit(1)
	}

	var req MutationRequest
	if err := json.Unmarshal(inputData, &req); err != nil {
		fmt.Fprintf(os.Stderr, "Error parsing JSON request: %v\n", err)
		os.Exit(1)
	}

	if req.SourceCode == "" {
		fmt.Fprintf(os.Stderr, "Error: source_code is empty\n")
		os.Exit(1)
	}

	// Parse the source code using dst
	fset := token.NewFileSet()
	f, err := decorator.ParseFile(fset, req.TargetFile, req.SourceCode, parser.ParseComments)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error parsing Go source code: %v\n", err)
		os.Exit(1)
	}

	// Apply mutations manually instead of ast.Inspect to handle deletions easily
	for _, mut := range req.Mutations {
		applyMutation(f, mut, fset)
	}

	// Write back the modified AST to stdout
	var buf bytes.Buffer
	if err := decorator.Fprint(&buf, f); err != nil {
		fmt.Fprintf(os.Stderr, "Error writing modified Go code: %v\n", err)
		os.Exit(1)
	}

	fmt.Print(buf.String())
}

func applyMutation(f *dst.File, mut MutationOperation, fset *token.FileSet) {
	// First pass for modification (replace_function_body)
	if mut.Action == "replace_function_body" && mut.NewBody != "" {
		for _, decl := range f.Decls {
			if funcDecl, ok := decl.(*dst.FuncDecl); ok {
				if funcDecl.Name.Name == mut.TargetNode {
					// We wrap the new body in a dummy package and parse it easily
					dummyCode := fmt.Sprintf("package dummy\n%s", mut.NewBody)
					dummyF, err := decorator.ParseFile(token.NewFileSet(), "", dummyCode, parser.ParseComments)
					if err == nil && len(dummyF.Decls) > 0 {
						if dummyFunc, ok := dummyF.Decls[0].(*dst.FuncDecl); ok {
							funcDecl.Body = dummyFunc.Body
						}
					} else {
						fmt.Fprintf(os.Stderr, "Failed to parse new body for %s: %v\n", mut.TargetNode, err)
					}
					break // Found and replaced
				}
			}
		}
	}

	// Handle deletions by filtering Decls
	if mut.Action == "delete_node" {
		var newDecls []dst.Decl
		for _, decl := range f.Decls {
			if funcDecl, ok := decl.(*dst.FuncDecl); ok {
				if funcDecl.Name.Name == mut.TargetNode {
					continue // Skip this node to delete it
				}
			} else if genDecl, ok := decl.(*dst.GenDecl); ok && genDecl.Tok == token.TYPE {
				// Handle struct/interface deletion if the TargetNode matches the type name
				keepGenDecl := true
				if len(genDecl.Specs) == 1 {
					if typeSpec, ok := genDecl.Specs[0].(*dst.TypeSpec); ok {
						if typeSpec.Name.Name == mut.TargetNode {
							keepGenDecl = false
						}
					}
				}
				if !keepGenDecl {
					continue
				}
			}
			newDecls = append(newDecls, decl)
		}
		f.Decls = newDecls
	}
}
