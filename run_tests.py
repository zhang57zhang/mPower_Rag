"""
Run all tests for mPower_Rag
"""
import sys
import subprocess
from pathlib import Path
import time


def run_test(test_file, name):
    """Run a test file"""
    print("\n" + "=" * 70)
    print(f"Running: {name}")
    print("=" * 70)

    start_time = time.time()
    result = subprocess.run(
        [sys.executable, str(test_file)],
        cwd=test_file.parent,
        capture_output=True,
        text=True
    )
    elapsed = (time.time() - start_time) * 1000

    # Print output
    if result.stdout:
        print(result.stdout)

    success = result.returncode == 0
    status = "[PASS]" if success else "[FAIL]"

    print(f"\n{status} {name} ({elapsed:.2f} ms)")
    print(f"    Return code: {result.returncode}")

    if not success and result.stderr:
        print(f"    Error: {result.stderr}")

    return success


def main():
    """Main function"""
    base_dir = Path(__file__).parent
    tests_dir = base_dir / "tests"

    print("=" * 70)
    print("mPower_Rag - Test Suite Runner")
    print("=" * 70)
    print(f"Tests directory: {tests_dir}")

    # Define tests
    tests = [
        ("Unit: Vector Store", tests_dir / "test_vector_store.py"),
        ("Unit: RAG Engine", tests_dir / "test_rag_engine.py"),
        ("Performance", tests_dir / "test_performance.py"),
        # ("API", tests_dir / "test_api.py")  # Requires running API server
    ]

    # Run tests
    results = []
    total_time = 0

    for name, test_file in tests:
        if test_file.exists():
            success = run_test(test_file, name)
            results.append((name, success))
            total_time += elapsed if 'elapsed' in locals() else 0
        else:
            print(f"\n[SKIP] {name} - File not found: {test_file}")
            results.append((name, None))

    # Summary
    print("\n" + "=" * 70)
    print("Test Suite Summary")
    print("=" * 70)

    passed = sum(1 for _, success in results if success is True)
    failed = sum(1 for _, success in results if success is False)
    skipped = sum(1 for _, success in results if success is None)

    print(f"\nTotal tests: {len(results)}")
    print(f"Passed: {passed}")
    print(f"Failed: {failed}")
    print(f"Skipped: {skipped}")

    print("\nDetailed results:")
    for name, success in results:
        if success is True:
            print(f"  [PASS] {name}")
        elif success is False:
            print(f"  [FAIL] {name}")
        else:
            print(f"  [SKIP] {name}")

    # Final result
    print("\n" + "=" * 70)
    if failed == 0 and passed > 0:
        print("All tests PASSED!")
        return 0
    elif failed > 0:
        print(f"{failed} test(s) FAILED")
        return 1
    else:
        print("No tests were run")
        return 1


if __name__ == "__main__":
    sys.exit(main())
