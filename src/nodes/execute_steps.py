def execute_steps_node(state):
    if state.current_step >= len(state.steps):
        state.intent = "exit"
        print(f"✅ All {len(state.steps)} steps completed successfully")
        return state

    step = state.steps[state.current_step]
    state.current_step += 1

    # store current step as intent so graph can route
    state.intent = step

    print(f"⚙️ Executing step {state.current_step}/{len(state.steps)}: {step}")
    return state
