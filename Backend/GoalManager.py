import uuid
from rich import print
# Import Core Modules (assuming they are in the same Backend package)
from Backend.Planner import generate_plan
from Backend.Verifier import Verifier
from Backend.Planner import generate_plan
from Backend.Verifier import Verifier
from Backend.Automation import OpenApp, Type, Press, TranslateAndExecute, Automation, ContentWriterAI
from Backend.TextToSpeech import TTS
from Backend.OutcomeVerifier import OutcomeVerifier
from Backend.GoalExtractor import GoalExtractor
from Backend.StrategySelector import StrategySelector
from Backend.OutcomeManager import OutcomeManager
from Backend.ImageGeneration import GenerateImages
from Backend.GSOAdapter import GSOAdapter
from Backend.outcomes import Outcome
from Backend.GoalDecomposer import GoalDecomposer
from Backend.Subgoal import Subgoal
import asyncio
import time

class GoalManager:
    def __init__(self):
        self.active_goals = {}
        self.verifier = Verifier()
        self.outcome_verifier = OutcomeVerifier()
        # v3.1 Failure Analyzer
        # v3.1 Failure Analyzer
        from Backend.FailureAnalyzer import FailureAnalyzer
        self.failure_analyzer = FailureAnalyzer()
        
        # GSO Layers
        self.goal_extractor = GoalExtractor()
        self.outcome_manager = OutcomeManager(memory_dir="d:/JARVIS 2/jarvis-ai-assistant/memory")
        self.strategy_selector = StrategySelector(outcome_manager=self.outcome_manager)
        
        # v4.0 Context Engine (The New Brain)
        from Backend.ContextEngine import ContextEngine
        self.context_engine = ContextEngine()
        
        # v4.0 Expectation Model (Updated)
        # Assuming Verifier has it, but we might need it for direct context updates or checking
        # Actually Verifier has it, but let's keep it separate if we need to log expectation vs plan in GM
        # But Verifier does the heavy lifting now.
        
        # v3.2/v4.0 User State: Kept for legacy compatibility if needed
        # But ContextEngine is primary source of truth.
        self.last_goal_description = ""

    def create_goal(self, description):
        goal_id = str(uuid.uuid4())
        goal = {
            "id": goal_id,
            "description": description,
            "state": "planning",
            "attempts": 0,
            "max_attempts": 3,
            "plan": [],
            "history": [] 
        }
        self.active_goals[goal_id] = goal
        print(f"[GoalManager] Goal Created: {description} (ID: {goal_id[:8]})")
        return goal_id

    # v4.0 Subgoal & Self-Correction
    from Backend.GoalDecomposer import GoalDecomposer
    from Backend.Subgoal import Subgoal
    
    def execute_goal(self, goal_id):
        goal_record = self.active_goals.get(goal_id)
        if not goal_record:
            return "Goal not found"

        print(f"[GoalManager] Executing Goal: {goal_record['description']}")
        
        from Backend.contracts import Goal # Import if not top-level
        
        derived_goal = self.goal_extractor.extract_goal(goal_record["description"])
        print(f"[GSO] Goal Extracted: {derived_goal}")

        # --- PART 2: CONTENT GOALS BYPASS AUTOMATION ENTIRELY ---
        # Gate: If goal is content-based, executed directly via LLM -> TTS
        if derived_goal.name in ["generate_content", "generate_code", "explain", "story", "pattern"] or \
           (hasattr(derived_goal, "response_mode") and derived_goal.response_mode in ["CONTENT", "QUERY"]):
            
            print(f"[GoalManager] Content/Query Goal detected. Bypassing Automation/Verifier.")
            
            # Content Generation
            content = derived_goal.content if derived_goal.content else derived_goal.name
            print(f"[Content] Generating content for: {content}")
            
            response = ContentWriterAI(content)
            
            # TTS Output
            TTS(response)
            
            # Mark Success immediately
            goal_record["state"] = "completed"
            return "Goal Completed (Content Bypass)"

        # --- PART 5: WHATSAPP MESSAGE CONTENT SAFETY ---
        if derived_goal.name == "send_whatsapp":
            # 1. Infer Defaults (Contextual)
            if not derived_goal.content:
                 target_lower = derived_goal.target.lower() if derived_goal.target else ""
                 if "mom" in target_lower or "mum" in target_lower:
                     derived_goal.content = "Hi"
                 elif "brother" in target_lower or "friend" in target_lower:
                     derived_goal.content = "Hey"
                 else:
                     derived_goal.content = "Hello"
                 print(f"[Safety] Inferred default message for '{derived_goal.target}': '{derived_goal.content}'")
            
            # 2. Sanitize Content (Part D)
            # Handle "a", "none", "None", empty strings explicitly
            raw = str(derived_goal.content).strip().lower()
            if raw in ["none", "a", "", "null"]:
                derived_goal.content = "Hi"
                print(f"[Safety] Sanitized content '{raw}' to 'Hi'")

        # --- PART 6: CLARIFICATION RULE (STRICT) ---
        # Only ask clarification if target missing AND no safe default exists
        # E.g. "send a message" -> target missing -> Ask
        # "search courses" -> target "courses" -> EXECUTE
        
        if derived_goal.name == "send_whatsapp" and not derived_goal.target:
             TTS("Who do you want to message?") # Ask directly? Or set goal to ASK?
             # If we return here, we need to handle the state. 
             # For now, let's allow it to fall through to Decomposer which might ask, 
             # OR we can enforce it here.
             # Prompt says: "send a message" -> ask who.
             # Ideally validation fails here.
             print("[GoalManager] Strict Clarification: Target missing for send_whatsapp.")
             return "Goal Paused: Clarification Needed"
        

        # --- PART 7: MEDIA CONTROLLER (GMC) ---
        if derived_goal.name == "play_media":
            print(f"[GoalManager] Media Goal Detected: {derived_goal.target}")
            
            from Backend.MediaController import MediaController
            controller = MediaController()
            
            # Layer 1: Normalization (Happens inside Controller for now, or we pre-normalize?)
            # GoalExtractor gave us target="blinding lights on spotify"
            # We let Controller parse it fully.
            
            intent = controller.normalize_intent(derived_goal.target)
            
            # Execute
            if "calibrate" in derived_goal.target.lower() or "calibration" in derived_goal.target.lower():
                 print("[GoalManager] Triggering Media Calibration...")
                 controller.calibrate()
                 goal_record["state"] = "completed"
                 return "Calibration Completed"
            
            success = controller.execute(intent)
            
            if success:
                goal_record["state"] = "completed"
                return "Media Playback Started"
            else:
                 goal_record["state"] = "failed"
                 return "Media Playback Failed"

        
        decomposer = GoalDecomposer()
        subgoals = decomposer.decompose(derived_goal)
        print(f"[GoalManager] Decomposed into {len(subgoals)} subgoals: {[sg.description for sg in subgoals]}")
        
        # EXECUTION LOOP (Subgoals)
        overall_success = True
        
        for i, subgoal in enumerate(subgoals):
            print(f"\n[GoalManager] Starting Subgoal {i+1}/{len(subgoals)}: {subgoal.description}")
            
            # Treat Subgoal as a mini-Goal for Strategy Selection
            sub_derived_goal = self.goal_extractor.extract_goal(subgoal.description)
            
            # Strategy Selection
            strategy = self.strategy_selector.select_strategy(sub_derived_goal)
            
            if strategy.confidence < 0.3:
                 print(f"[GoalManager] Low confidence for subgoal '{subgoal.description}'.")


            # Subgoal Retry Loop (Self-Correction)
            subgoal_success = False
            attempts = 0
            max_retries = 1 # Part C: Reduced Retries (Max 1)
            
            while attempts <= max_retries:
                attempts += 1
                outcome = None
                
                try:
                    # Execute using Strategy
                    # 1. Plan (Mini-plan for this step) (Or just direct execution if simple?)
                    # Planner takes Goal/Strategy.
                    context = self.context_engine.get_context()
                    
                    # We skip full "Planner.py" for simple subgoals? 
                    # Prompt says "Execute".
                    # Existing pipeline: Plan -> Automate.
                    # We should maintain it for consistency.
                    
                    plan = generate_plan(
                        subgoal.description,
                        context=context,
                        goal_obj=sub_derived_goal,
                        strategy_obj=strategy
                    )
                    
                    # Verify Plan (Quick check)
                    # Skip full verification for speed? Or keep safety?
                    # Keep safety.
                    is_safe, _, verification = self.verifier.verify_plan(plan, context=context, user_query=subgoal.description)
                    if not is_safe:
                        raise Exception(f"Unsafe subgoal plan: {verification}")
                    
                    # Execute
                    commands = GSOAdapter.plan_to_commands(verification)
                    print(f"[Subgoal] Executing: {commands}")
                    step_outcomes = asyncio.run(Automation(commands))
                    
                    # Check result
                    failed_outcome = next((o for o in step_outcomes if not o.success), None)
                    
                    if not failed_outcome:
                        subgoal_success = True
                        outcome = step_outcomes[-1] if step_outcomes else Outcome(success=True)
                        break # Success, move to next subgoal
                    else:
                        outcome = failed_outcome
                        raise Exception(failed_outcome.reason) # Trigger catch block for diagnosis

                except Exception as e:
                    print(f"[GoalManager] Subgoal Failed: {e}")
                    
                    # DIAGNOSIS & CORRECTION
                    analysis = self.failure_analyzer.analyze_failure(
                        goal_type=subgoal.description, 
                        context="subgoal_execution", 
                        failure_stage="execution", 
                        failure_reason=str(e)
                    )
                    
                    correction = analysis["correction"]
                    print(f"[Self-Correction] Applied Fix: {correction}")
                    
                    if correction == "ABORT":
                        print("[GoalManager] Irrecoverable failure. Aborting Goal.")
                        break # Break retry loop, leads to overall failures
                    
                    if correction == "REFOCUS":
                        # Hack: Inject a click/focus? 
                        # Ideally Automation handles this, but we can instruct via side-effect or just retry.
                        print("[GoalManager] Should refocus... Retrying.")
                        
                    # Retry loop continues
            
            # Post-Subgoal Check
            if subgoal_success:
                subgoal.completed = True
                self.outcome_manager.record(
                    goal_id=goal_id, # Link to main goal? Or subgoal name? 
                    # Using main goal ID helps track overall, but target/strategy is consistent.
                    # We record stats for the STRATEGY used.
                    target=sub_derived_goal.target,
                    strategy=strategy.name,
                    primary_success=True,
                    time_taken=0.1, 
                    retries=attempts-1,
                    fallback_used=False
                )
            else:
                overall_success = False
                print(f"[GoalManager] Subgoal '{subgoal.description}' failed after {attempts} attempts.")
                # Record failure
                self.outcome_manager.record(
                    goal_id=goal_id,
                    target=sub_derived_goal.target,
                    strategy=strategy.name, 
                    primary_success=False,
                    time_taken=0.1,
                    retries=attempts-1,
                    fallback_used=False
                )
                break # Stop processing further subgoals
        
        goal_record["state"] = "completed" if overall_success else "failed"
        return "Goal Completed" if overall_success else "Goal Failed"

    def _log_failure(self, goal, strategy, outcome, retries):
        import json
        import os
        from datetime import datetime
        
        log_file = "memory/failures.json"
        
        entry = {
            "timestamp": datetime.utcnow().isoformat(),
            "goal": goal.name,
            "strategy": strategy.name,
            "reason": outcome.reason,
            "evidence": outcome.evidence,
            "retries": retries
        }
        
        try:
            if not os.path.exists(log_file):
                with open(log_file, "w") as f: json.dump([], f)
                
            with open(log_file, "r+") as f:
                data = json.load(f)
                data.append(entry)
                f.seek(0)
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"[GoalManager] Logging failed: {e}")

