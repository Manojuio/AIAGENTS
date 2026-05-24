import sys
from google import genai
from google.genai import types
from config import GEMINI_API_KEY, MAX_AGENT_ITERATIONS
from agent.system_prompt import SYSTEM_PROMPT
from agent.tools import TOOL_DECLARATIONS, execute_agent_tool

def run_bugray_engine(user_query: str):
    """
    Manages the core state machine loop, processing conversation updates and tool calls.
    """
    client = genai.Client(api_key=GEMINI_API_KEY)
    
    # Track complete multi-turn conversation state to make stateless API behave logically
    messages = [
        types.Content(role="user", parts=[types.Part.from_text(text=user_query)])
    ]
    
    # Register our tool schemas and prompt rules inside the configuration profile
    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT,
        temperature=0.1,  # Low temperature guarantees deterministic code inspection
        tools=[types.Tool(function_declarations=TOOL_DECLARATIONS)]
    )

    for iteration in range(MAX_AGENT_ITERATIONS):
        print(f"🔄 [Turn {iteration + 1}/{MAX_AGENT_ITERATIONS}] Analyzing state...")
        
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=messages,
                config=config
            )
            
            # Scenario A: Gemini requires tool calling access to gather more context
            if response.function_calls:
                for call in response.function_calls:
                    print(f"🤖 Agent Intent: Executing tool '{call.name}' with args {call.args}")
                    
                    # Run the tool locally on your hard drive
                    tool_result = execute_agent_tool(call.name, call.args)
                    
                    # Append the model's action intent to history
                    messages.append(response.candidates[0].content)
                    
                    # Append the tool's execution data to history with role="tool"
                    messages.append(types.Content(
                        role="tool",
                        parts=[types.Part.from_function_response(
                            name=call.name, 
                            response={"result": tool_result}
                        )]
                    ))
                    
            # Scenario B: Gemini has found the error and responds directly with text
            elif response.text:
                print(f"\n💡 Bugray Solution:\n{response.text}")
                return
                
        except Exception as e:
            print(f"❌ Critical Engine Failure: {str(e)}")
            sys.exit(1)
            
    print(f"\n⚠️ Cap Reached: Terminated loop at MAX_AGENT_ITERATIONS ({MAX_AGENT_ITERATIONS}).")