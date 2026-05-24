import sys
from agent.orchestrator import run_bugray_engine

def main():
    if len(sys.argv) < 2:
        print("System Error:Missing debugging instructions")
        print("Usage: python main.py 'Debugging Instructions'")
        sys.exit(1)
    user_query = sys.argv[1]

    print("\n=======================================================")
    print("BUGRAY CLI Debugging Agent Initialized")
    print("=======================================================\n")

    run_bugray_engine(user_query)

    print("\n=======================================================")
    print("BUGRAY Session Ended")

if __name__ == "__main__":
    main()