import Lake
open Lake DSL

package «contextome_proof» where
  -- Settings applied to both the library and executables
  leanOptions := #[
    ⟨`pp.unicode.fun, true⟩
  ]

@[default_target]
lean_lib «ContextomeNecessity» where
  -- add any library-specific settings here
