import json
import testbed_utils
from autogenra import AutoGenWorkFlowManager, AgentWorkFlowConfig

testbed_utils.init()
##############################

# load an agent specification in JSON
agent_spec = json.load(open("agent_spec.json"))

# Creat a An AutoGen Workflow Configuration from the agent specification
agent_work_flow_config = AgentWorkFlowConfig(**agent_spec)

# Create a Workflow from the configuration
agent_work_flow = AutoGenWorkFlowManager(agent_work_flow_config)

# Run the workflow on a task
task_query = "__PROMPT__"
agent_work_flow.run(message=task_query)

##############################
testbed_utils.finalize(agents=[])
