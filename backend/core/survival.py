import os
import json
import time
import zipfile
import shutil
from pathlib import Path
from core.state import OrganismState

class SurvivalManager:
    """
    Level 35: Genetic Survival (State-Seed).
    Ensures the organism can survive hardware death by bundling core state into 'seeds'.
    """
    def __init__(self, seed_dir: str = "seeds"):
        self.seed_dir = Path(seed_dir)
        self.seed_dir.mkdir(exist_ok=True)
        self.state_manager = OrganismState()

    def create_seed(self) -> str:
        """
        Gathers all core data and compresses it into a timestamped seed file.
        """
        timestamp = int(time.time())
        seed_name = f"bizit_genetics_{timestamp}.seed"
        seed_path = self.seed_dir / seed_name
        
        # Paths to bundle
        core_files = [
            "organism_state.json",
            "memories/evolution_mutations.json",
            "memories/business_ledger.json"
        ]
        
        # Temp dir for bundling
        temp_bundle = self.seed_dir / f"bundle_{timestamp}"
        temp_bundle.mkdir()
        
        try:
            print(f"🧬 [SURVIVAL] Initiating Genetic Seeding: {seed_name}")
            
            # 1. Capture current state JSON
            # (In a real scenario, we'd also dump Redis if being used)
            state_data = {
                "vitals": self.state_manager.financial_vitals,
                "status": self.state_manager.get_summary(),
                " Weis_score": self.state_manager.get_weisman_score()
            }
            with open(temp_bundle / "vitals.json", "w") as f:
                json.dump(state_data, f, indent=4)

            # 2. Copy existing memory files if they exist
            for f_path in core_files:
                if os.path.exists(f_path):
                    shutil.copy(f_path, temp_bundle / os.path.basename(f_path))

            # 3. Create the Seed (ZIP)
            with zipfile.ZipFile(seed_path, 'w') as zipf:
                for root, _, files in os.walk(temp_bundle):
                    for file in files:
                        zipf.write(os.path.join(root, file), arcname=file)
            
            print(f"✨ [SURVIVAL] Seed {seed_name} is viable and stored.")
            
            # Clean up temp
            shutil.rmtree(temp_bundle)
            
            # Add event to state
            self.state_manager.add_event({
                "source": "SURVIVAL",
                "event_type": "GENETIC_SEED_CREATED",
                "timestamp": time.time(),
                "payload": {"seed": seed_name}
            })
            
            return str(seed_path)

        except Exception as e:
            print(f"❌ [SURVIVAL] Seeding failed: {e}")
            if temp_bundle.exists():
                shutil.rmtree(temp_bundle)
            return ""

    def prune_old_seeds(self, keep_last: int = 5):
        """
        Deletes old seeds to prevent metabolic bloat.
        """
        seeds = sorted(self.seed_dir.glob("*.seed"), key=os.path.getmtime)
        if len(seeds) > keep_last:
            for old_seed in seeds[:-keep_last]:
                old_seed.unlink()
                print(f"🗑️ [SURVIVAL] Pruned old seed: {old_seed.name}")
