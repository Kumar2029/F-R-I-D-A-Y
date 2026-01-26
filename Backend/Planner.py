import json
import cohere
from dotenv import dotenv_values
from rich import print

env_vars = dotenv_values(".env")
CohereAPIKey = env_vars.get("CohereAPIKey")
co = cohere.Client(api_key=CohereAPIKey)

planner_preamble = """
You are the PLANNER for JARVIS. Your job is to convert user requests into a structured JSON plan.
You must NOT execute anything. You only plan.

STRICT SINGLE-COMMAND POLICY:
You may emit ONLY ONE canonical command per intent.
Do NOT decompose actions into low-level steps (open, wait, type, press).
All sequencing is handled by the Execution Layer.

Available Actions:
- "search_web": {"target": "query"}
- "open": {"target": "app_name"}
- "send_whatsapp": {"target": "[Contact] | [Message]"}
- "content": {"target": "topic"}
- "wait": {"target": "seconds"}  (Use ONLY if explicitly requested by user)

Rules:
1. Return strictly a JSON object (NOT an array).
2. Schema:
   {
       "plan": [{"action": "...", "target": "..."}],
       "success_criteria": {"type": "window_title", "value": "Target App Name"},
       "failure_conditions": ["Window not found"],
       "fallback_plans": []
   }
3. No markdown, no explanations.

Examples:
1. Request: "Search python on google"
   Plan:
   {
     "plan": [{"action": "search_web", "target": "python"}],
     "success_criteria": {"type": "browser_url", "value": "google.com"}
   }

2. Request: "Open Chrome"
   Plan:
   {
     "plan": [{"action": "open", "target": "chrome"}],
     "success_criteria": {"type": "window_title", "value": "Chrome"}
   }

3. Request: "Message Mom Hi"
   Plan:
   {
     "plan": [{"action": "send_whatsapp", "target": "Mom | Hi"}],
     "success_criteria": {"type": "whatsapp_chat", "value": "Mom"}
   }

[IMPORTANT]
Do NOT emit multi-step plans like "open chrome", "wait", "type".
Use "search_web" instead.
For WhatsApp, ALWAYS use "send_whatsapp".
"""

def generate_plan(user_query, failure_context=None, context=None, goal_obj=None, strategy_obj=None):
    try:
        current_message = user_query
        
        # State Adaptation Logic v4.0
        adaptation_directive = ""
        if context:
            # 1. Autonomy & Granularity
            if context.get("autonomy_level", 0.5) < 0.4:
                adaptation_directive += "\n[CONSTRAINT] User desires CONTROL. Generate granular steps. Do NOT assume complex automations."
            
            # 2. Speed vs Verbosity
            if context.get("interaction_speed", 0.5) > 0.7:
                adaptation_directive += "\n[STYLE] Be EFFICIENT. Minimal reasoning."
            
            # 3. Surprise Tolerance (Caution)
            if context.get("surprise_tolerance", 0.5) < 0.3:
                adaptation_directive += "\n[SAFETY] HIGH CAUTION. If unsure, 'ask_user' or 'wait'."
        
        if failure_context or adaptation_directive:
            current_message = f"{user_query}\n\n[IMPORTANT CONTEXT]\n{failure_context or ''}\n{adaptation_directive}"
            if failure_context:
                current_message += "\nDo NOT repeat the exact same plan if it failed previously. Try a fallback approach."

        # GSO Integration
        if goal_obj and strategy_obj:
            current_message += f"\n\n[GOAL]: {goal_obj.goal_id} (Target: {goal_obj.target})"
            current_message += f"\n[STRATEGY]: {strategy_obj.strategy_id} (Reason: {strategy_obj.reason})"
            
            if strategy_obj.strategy_id == "send_whatsapp":
                current_message += f"\n[INSTRUCTION] Implementation MUST use 'send_whatsapp' action with target '{goal_obj.target} | {goal_obj.content}'."
            elif strategy_obj.strategy_id == "open_app_direct":
                current_message += f"\n[INSTRUCTION] Implementation MUST use 'open' action for target '{goal_obj.target}'."
            elif strategy_obj.strategy_id == "generate_image_hf":
                current_message += f"\n[INSTRUCTION] Implementation MUST use 'generate_image' action with target as the prompt: '{goal_obj.content}'."

        response = co.chat(
            model='command-r-08-2024',
            message=current_message,
            temperature=0,
            preamble=planner_preamble
        )
        
        # Extract text and try to parse JSON
        plan_text = response.text
        # Cleanup potential markdown code blocks
        plan_text = plan_text.replace("```json", "").replace("```", "").strip()
        
        plan_data = json.loads(plan_text)
        
        # Backward compatibility for v2 (if model still returns list)
        if isinstance(plan_data, list):
            return {"plan": plan_data, "success_criteria": None}
            
        return plan_data
    except Exception as e:
        print(f"Planning Error: {e}")
        return []
