import uuid
from rich import print
# Import Core Modules (assuming they are in the same Backend package)
from Backend.Planner import generate_plan
from Backend.Verifier import Verifier
from Backend.Planner import generate_plan
from Backend.Verifier import Verifier
from Backend.Automation import OpenApp, Type, Press, TranslateAndExecute, Automation
from Backend.OutcomeVerifier import OutcomeVerifier
from Backend.GoalExtractor import GoalExtractor
from Backend.StrategySelector import StrategySelector
from Backend.OutcomeManager import OutcomeManager
from Backend.ImageGeneration import GenerateImages
from Backend.GSOAdapter import GSOAdapter
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

    def execute_goal(self, goal_id):
        goal = self.active_goals.get(goal_id)
        if not goal:
            return "Goal not found"

        print(f"[GoalManager] Executing Goal: {goal['description']}")
        
        # v4.0: Context Update (Repetition Check)
        if goal['description'] == self.last_goal_description:
            self.context_engine.update_context("repetition", intensity=1.0)
            print("[GoalManager] Detected command repetition. Updating context.")
        self.last_goal_description = goal['description']
        
        context = self.context_engine.get_context()
        print(f"[GoalManager] Context: {self.context_engine.format_context()}")
        
        # v4.0: PAUSE if Overload or Low Surprise Tolerance + Mismatch (handled in Verifier)
        # But check raw overload here if mapped
        # ContextEngine doesn't explicitly have 'overload' key, it has 'autonomy' and 'speed'
        # Check interaction_speed. If very low, maybe pause?
        # Let's rely on strict Mismatch Detection in Verifier.
        
        while goal["attempts"] < goal["max_attempts"]:
            goal["attempts"] += 1
            print(f"[GoalManager] Attempt {goal['attempts']} of {goal['max_attempts']}")
            
            # 72
            
            # --- GSO FRAMEWORK INTEGRATION ---
            # 1. Goal Extraction
            derived_goal = self.goal_extractor.extract_goal(goal["description"])
            print(f"[GSO] Goal Extracted: {derived_goal}")
            
            # 2. Strategy Selection
            selected_strategy = self.strategy_selector.select_strategy(derived_goal)
            
            if not selected_strategy:
                print(f"[GSO] No valid strategy found for goal: {derived_goal.goal_id}")
                return "Goal failed: No valid strategy found."

            print(f"[GSO] Strategy Selected: {selected_strategy}")
            
            # Verify Strategy Confidence - Ask User if needed (Rule 6)
            # PART 3: ASK-BEFORE-ACT DECISION GATE
            if selected_strategy.confidence < 0.5:
                # Execution must STOP here
                return {
                    "status": "needs_confirmation",
                    "message": f"I'm not confident about using {selected_strategy.strategy_id}. Do you want me to proceed?",
                    "goal_id": goal_id, # Helpful context
                    "strategy": selected_strategy.strategy_id
                }

            # 3. PLANNING (with Failure Context, Context Constraints, and GSO)
            failure_context = self.failure_analyzer.get_learning_context(goal["description"])
            
            goal["state"] = "planning"
            # Pass Goal and Strategy to Planner
            plan = generate_plan(
                goal["description"], 
                failure_context=failure_context, 
                context=context,
                goal_obj=derived_goal,
                strategy_obj=selected_strategy
            )
            
            # 4. VERIFICATION (with Risk Logic)
             # Get Adaptation Strategy
            # Use 'planning' as stage for pre-check
            # For simpler integration, we just fetch past fail count implicitly via analyzer, 
            # ideally analyze_failure returned modifiers, but here we can query memory.
            # Let's rely on the Planner Context for mitigation, and Verifier for safety.
            
            learning_data = self.failure_analyzer.analyze_failure(goal["description"], "system", "planning", "pre_check")
            risk_modifier = learning_data["risk_modifier"]
            
            # Don't record pre_check as a hard failure, just retrieving data. 
            # Actually analyze_failure records it. We should use get_learning_context logic.
            # Simplified: Use failure_analysis on actual failure. 
            # For verification, we just want the modifier.
            # Let's make a helper or just recalculate locally for now:
            # risk_modifier = 0.2 * failure_count (approx)
            pad_failures = self.failure_analyzer.memory.get_failures_by_goal(goal["description"])
            risk_modifier = 0.2 * len(pad_failures)

            is_safe, risk_score, verification = self.verifier.verify_plan(plan, risk_modifier=risk_modifier, context=context, user_query=goal["description"])
            
            if not is_safe:
                goal["state"] = "failed"
                # Record this as a planning failure
                self.failure_analyzer.analyze_failure(goal["description"], "verifier", "planning", f"Unsafe Plan (Risk: {risk_score})")
                return f"Plan unsafe: {verification}"
            
            goal["plan"] = verification
            
            # 3. EXECUTION LOOP (ADAPTER + LEGACY)
            goal["state"] = "executing"
            execution_success = True
            primary_success = False
            fallback_triggered = False
            start_time = time.time() # Measure from execution start
            
            try:
                # ADAPTER: Convert Plan -> Commands
                commands = GSOAdapter.plan_to_commands(goal["plan"])
                print(f"[GSO] Converted to Legacy Commands: {commands}")
                
                # EXECUTION: Run via Legacy Automation Pipeline
                async def run_automation(cmds):
                    results = await Automation(cmds)
                    for res in results:
                        if res.get("status") == "failed":
                             raise Exception(res.get("reason", "Unknown Error"))
                
                asyncio.run(run_automation(commands))
                primary_success = True # If we get here without exception, primary worked
            
            except Exception as e:
                print(f"[GSO] Execution Failed: {e}")
                print("[GSO] Falling back to legacy execution")
                self.context_engine.update_context("failure", intensity=0.5)
                fallback_triggered = True
                primary_success = False
                
                # FALLBACK: Execute user prompt directly as a command (or extraction fallback)
                # The user prompt 'user_input' is goal['description']
                # If extraction failed or plan failed, we try to interpret the raw description as a command?
                # Or re-run automation with just the description if it's simple?
                # "await Automation([user_input])" suggests treating input as a command.
                
                try:
                     async def run_fallback():
                         commands = [goal['description']] 
                         await Automation(commands)
                     
                     asyncio.run(run_fallback())
                     # If fallback succeeds, we count it as specific success? 
                     # Or just proceed.
                except Exception as fallback_error:
                     print(f"[GSO] Fallback also failed: {fallback_error}")
                     execution_success = False
                     
                     # Analysis
                     analysis = self.failure_analyzer.analyze_failure(
                        goal_type=goal["description"],
                        context="fallback",
                        failure_stage="execution",
                        failure_reason=str(e)
                     )
                     if analysis["recommendation"] == "ASK_USER":
                        goal["state"] = "failed"
                        return f"Multiple failures. Recommendation: {analysis['recommendation']}"
                     
                     break # Trigger retry loop
            
            # --- OUTCOME RECORDING (PART 4) ---
            end_time = time.time()
            time_taken = round(end_time - start_time, 2)
            
            # Use self.outcome_manager (Assuming it's the new class)
            # --- OUTCOME RECORDING (PART 4 & 6) ---
            end_time = time.time()
            time_taken = round(end_time - start_time, 2)
            
            # Determine success semantics
            # If execution_success is True, it means NO exception occurred in either primary OR fallback.
            # But we need to know if we used fallback.
            # We track this via a flag 'fallback_triggered'
            
            # Use self.outcome_manager (Assuming it's the new class)
            self.outcome_manager.record(
                goal_id=derived_goal.goal_id, 
                target=derived_goal.target,
                strategy=selected_strategy.strategy_id,
                primary_success=primary_success, # We need to track this locally!
                time_taken=time_taken,
                retries=goal["attempts"] - 1,
                fallback_used=fallback_triggered
            )
            
            # Logging as required
            print(f"[ODL] Outcome Recorded. Success: {primary_success} | Fallback: {fallback_triggered}")

            if execution_success: # This implies overall system success (primary or fallback)
                goal["state"] = "completed"
                self.context_engine.update_context("success", intensity=0.5)
                return "Goal Completed Successfully"
            
            # If we are here, execution failed. Loop will retry if attempts < max.
            
        goal["state"] = "failed"
        return "Goal failed during execution"
