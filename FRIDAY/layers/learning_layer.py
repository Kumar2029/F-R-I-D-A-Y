import os
import json
import time
from typing import Dict, List, Optional
from FRIDAY.core.models import Intent, IntentHints, ActionDomain, ExecutionPlan, ActionResult

MEMORY_DIR = os.path.join(os.getcwd(), "FRIDAY", "memory")

class LearningAdvisoryLayer:
    def __init__(self):
        self._ensure_memory_dir()
        self.preferences = self._load_json("preferences.json", {})
        self.plan_stats = self._load_json("plan_stats.json", {})
        self.failures = self._load_json("failures.json", [])

    def _ensure_memory_dir(self):
        if not os.path.exists(MEMORY_DIR):
            try:
                os.makedirs(MEMORY_DIR)
            except Exception as e:
                print(f"[Learning] Failed to create memory dir: {e}")

    def _load_json(self, filename: str, default):
        path = os.path.join(MEMORY_DIR, filename)
        if not os.path.exists(path):
            return default
        try:
            with open(path, 'r') as f:
                return json.load(f)
        except Exception as e:
            print(f"[Learning] Error loading {filename}: {e}")
            return default

    def _save_json(self, filename: str, data):
        path = os.path.join(MEMORY_DIR, filename)
        try:
            with open(path, 'w') as f:
                json.dump(data, f, indent=4)
        except Exception as e:
            print(f"[Learning] Error saving {filename}: {e}")

    # ------------------------------------------------------------------
    # 1. ADVISE (Read-Only)
    # ------------------------------------------------------------------
    def advise(self, intent: Intent) -> Intent:
        """
        Enriches the intent with hints based on history and preferences.
        NEVER modifies the core intent action/params.
        """
        try:
            hints = IntentHints()
            
            # A. Check Preferences
            if intent.domain == ActionDomain.MEDIA:
                if not intent.parameters.get("platform"):
                    # Default to preference if not specified
                    hints.preferred_platform = self.preferences.get("default_music_app", "spotify")
            
            elif intent.domain == ActionDomain.CODE:
                 # Any code preferences? e.g. default language?
                 pass

            # B. Check Failure Patterns
            # (Simple implementation: if we failed recently on this exact query, maybe warn or suggest retry)
            # For now, we skip complex pattern matching to keep it safe.

            # Attach hints
            # intent.hints = hints (Disabled temporarily to reduce console noise)
            # print(f"[Learning] Advised: {hints}")
            return intent

        except Exception as e:
            print(f"[Learning] Advisory failed: {e}")
            return intent  # Fail safe: return original

    # ------------------------------------------------------------------
    # 2. LEARN (Write)
    # ------------------------------------------------------------------
    def learn(self, intent: Intent, plan: ExecutionPlan, result: ActionResult):
        """
        Updates statistics based on execution outcome.
        """
        try:
            # Update Plan Stats
            plan_id = getattr(plan, "plan_id", "unknown")
            if plan_id not in self.plan_stats:
                self.plan_stats[plan_id] = {
                    "success": 0, "failure": 0, "last_used": 0
                }
            
            stats = self.plan_stats[plan_id]
            stats["last_used"] = time.time()
            if result.success:
                stats["success"] += 1
            else:
                stats["failure"] += 1
            
            self._save_json("plan_stats.json", self.plan_stats)

            # Record Failure details if failed
            if not result.success:
                failure_record = {
                    "timestamp": time.time(),
                    "domain": intent.domain.name,
                    "action": intent.action,
                    "plan_id": plan_id,
                    "error": result.message,
                    "verification_error": getattr(result, "verification", None).error_message if hasattr(result, "verification") and result.verification else None
                }
                self.failures.append(failure_record)
                # Keep log manageable (last 50)
                if len(self.failures) > 50:
                    self.failures = self.failures[-50:]
                self._save_json("failures.json", self.failures)
                
        except Exception as e:
            print(f"[Learning] Learning update failed: {e}")

    # ------------------------------------------------------------------
    # 3. EXPLICIT TEACHING (User Preference Updates)
    # ------------------------------------------------------------------
    def set_preference(self, key: str, value: str):
        self.preferences[key] = value
        self._save_json("preferences.json", self.preferences)

    # ------------------------------------------------------------------
    # 4. MEDIA LEARNING (GMC Specific)
    # ------------------------------------------------------------------
    def get_preferred_platform(self, song_name: Optional[str] = None) -> Optional[str]:
        # 1. Check specific song history (Last successful platform)
        if song_name:
            # Simple sanitization
            key = f"media_history_{song_name.lower().strip()}"
            if key in self.preferences:
                return self.preferences[key]

        # 2. Check global default
        return self.preferences.get("default_music_app")

    def record_media_success(self, song_name: str, platform: str):
        # Save last successful platform for this song
        if song_name:
            key = f"media_history_{song_name.lower().strip()}"
            self.preferences[key] = platform
            self._save_json("preferences.json", self.preferences)
        
        # Update global stats
        # (covered by generic learn() if we pass the plan, but specific helps)
    
    def record_media_failure(self, song_name: str, platform: str):
        # Maybe blacklist platform for this song temporarily?
        # For now, just logging failure in generic failures is enough.
        pass
