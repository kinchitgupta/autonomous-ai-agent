from agent.agent_core import run_agent

output = run_agent("What is 25 * (12 + 8)?")

print("\nPLAN:\n", output["plan"])
print("\nOBSERVATIONS:\n", output["observations"])
print("\nRESULT:\n", output["result"])
