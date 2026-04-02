import logging
import time
from typing import Dict, Any
from actuation_layer.infrastructure_bridge import InfrastructureBridge

logger = logging.getLogger(__name__)

class SurvivalProtocol:
    """
    Autonomous logic for ensuring BIZIT's infrastructure survival.
    Level 39: Final Sovereignty.
    """
    def __init__(self, infra_bridge: InfrastructureBridge):
        self.infra = infra_bridge
        self.last_audit = time.time()
        self.survival_threshold = 0.70 # Minimum health before recovery
        self.stress_threshold = 0.90 # CPU stress before scaling

    def run_survival_audit(self, metabolic_stats: Dict[str, Any]):
        """
        Analyzes infrastructure health and metabolic stress to determine survival actions.
        """
        status = self.infra.get_cluster_status()
        cpu = metabolic_stats.get("cpu", 0) / 100.0
        
        actions_taken = []
        
        # 1. Self-Healing (Reaction to low health)
        for name, deploy in status["deployments"].items():
            if deploy["health"] < self.survival_threshold:
                logger.warning(f"⚠️ [SURVIVAL] Critical Health detected for {name} ({deploy['health']:.2f}). Triggering Self-Healing.")
                self.infra.heal_service(name)
                actions_taken.append({"type": "SELF_HEAL", "service": name})

        # 2. Autonomous Scaling (Reaction to metabolic stress)
        if cpu > self.stress_threshold:
            logger.info(f"📈 [SURVIVAL] Sustained Metabolic Stress ({cpu:.2f}). Increasing compute redundancy.")
            for name, deploy in status["deployments"].items():
                if "core" in name:
                    new_replicas = deploy["replicas"] + 1
                    self.infra.scale_deployment(name, new_replicas)
                    actions_taken.append({"type": "SCALE_OUT", "service": name, "replicas": new_replicas})

        # 3. Regional Expansion (Reaction to system-wide complexity)
        # If we have 3+ core nodes and still high stress, expand to a new region
        core_replicas = sum(d["replicas"] for n, d in status["deployments"].items() if "core" in n)
        if core_replicas >= 5 and cpu > 0.85 and len(self.infra.regions) < 3:
            new_region = "AWS-US-EAST-1"
            logger.info(f"🌐 [SURVIVAL] Regional saturation detected. Provisioning {new_region} for global redundancy.")
            self.infra.provision_region(new_region)
            actions_taken.append({"type": "REGION_EXPAND", "region": new_region})

        return actions_taken
