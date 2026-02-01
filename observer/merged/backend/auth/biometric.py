"""Touch ID / Face ID authentication via macOS LocalAuthentication.

Ported from: tools/file_explorer.py (lines 108-162)
"""

import subprocess
import sys
from typing import Tuple


def request_biometric_auth(reason: str = "Control Room requires authentication") -> Tuple[bool, str]:
    """Request Touch ID / Face ID authentication via macOS LocalAuthentication.

    Returns:
        Tuple of (success: bool, error_message: str)
    """
    # Only works on macOS
    if sys.platform != 'darwin':
        return False, "Biometric authentication only available on macOS"

    # Swift code to trigger biometric auth with passcode fallback
    swift_code = f'''
import LocalAuthentication
import Foundation

let context = LAContext()
var error: NSError?

if context.canEvaluatePolicy(.deviceOwnerAuthenticationWithBiometrics, error: &error) {{
    let semaphore = DispatchSemaphore(value: 0)
    var success = false

    context.evaluatePolicy(.deviceOwnerAuthenticationWithBiometrics,
                          localizedReason: "{reason}") {{ result, _ in
        success = result
        semaphore.signal()
    }}

    semaphore.wait()
    exit(success ? 0 : 1)
}} else {{
    // Fallback to device passcode if biometrics unavailable
    if context.canEvaluatePolicy(.deviceOwnerAuthentication, error: &error) {{
        let semaphore = DispatchSemaphore(value: 0)
        var success = false

        context.evaluatePolicy(.deviceOwnerAuthentication,
                              localizedReason: "{reason}") {{ result, _ in
            success = result
            semaphore.signal()
        }}

        semaphore.wait()
        exit(success ? 0 : 1)
    }}
    exit(1)
}}
'''
    try:
        result = subprocess.run(
            ['swift', '-e', swift_code],
            capture_output=True,
            timeout=60  # 60 second timeout for user interaction
        )
        if result.returncode == 0:
            return True, ""
        else:
            return False, "Authentication failed or cancelled"
    except subprocess.TimeoutExpired:
        return False, "Authentication timed out"
    except FileNotFoundError:
        return False, "Swift not found - macOS development tools required"
    except Exception as e:
        return False, f"Authentication error: {str(e)}"


def is_biometric_available() -> Tuple[bool, str]:
    """Check if biometric authentication is available.

    Returns:
        Tuple of (available: bool, reason: str)
    """
    if sys.platform != 'darwin':
        return False, "Not running on macOS"

    # Check if Swift is available
    try:
        subprocess.run(['swift', '--version'], capture_output=True, timeout=5)
    except (FileNotFoundError, subprocess.TimeoutExpired):
        return False, "Swift not available"

    return True, "Biometric authentication available"
