from agent import InterveneAgent

if __name__ == "__main__":
    # Create agent for input monitoring
    agent = InterveneAgent()
    
    try:
        # Process the todo while monitoring for overrides
        if not agent.detector.override:
            agent.run_task()
        else:
            print("🛑 Manual override detected. Task cancelled.")
    finally:
        agent.shutdown()
