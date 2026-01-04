import pkg.helper as helper  # module alias named "helper"

def helper_fn():
    return 123

def main():
    # This call MUST NOT resolve_internal to the file-node for pkg/helper.py
    helper()
    # This call SHOULD resolve_internal (atomic -> atomic)
    return helper_fn()

if __name__ == "__main__":
    main()
