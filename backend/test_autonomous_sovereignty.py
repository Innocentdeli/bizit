import sys
sys.path.append(".")
import time
import logging
import asyncio
from actuation_layer.infrastructure_bridge import InfrastructureBridge
from evolution.survival_protocol import SurvivalProtocol

# Configure logging
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")

async def test_autonomous_sovereignty():
    print("🚀 Testing Level 39: Final Sovereignty (Autonomous Deployment)...")
    print("=" * 70)
    
    infra = InfrastructureBridge()
    survival = SurvivalProtocol(infra)
    
    # 1. Test Self-Healing
    print("\n[STEP 1] Simulating Local Node Degradation (Health 0.60)")
    # Manually degrade a service
    infra.active_deployments["core-backend"]["health"] = 0.60
    
    # Run audit
    actions = survival.run_survival_audit({"cpu": 40})
    
    if any(a["type"] == "SELF_HEAL" for a in actions):
        print("✅ Success: Self-healing triggered for core-backend.")
    else:
        print("❌ Failure: Self-healing NOT triggered.")

    # 2. Test Autonomous Scaling
    print("\n[STEP 2] Simulating High Metabolic Stress (CPU 95%)")
    actions = survival.run_survival_audit({"cpu": 95})
    
    scale_action = next((a for a in actions if a["type"] == "SCALE_OUT"), None)
    if scale_action:
        print(f"✅ Success: Autonomous Scaling triggered. New Replicas: {scale_action['replicas']}")
    else:
        print("❌ Failure: Autonomous Scaling NOT triggered.")

    # 3. Test Regional Expansion
    print("\n[STEP 3] Simulating Sustained Saturation (Core Replicas 5+, CPU 95%)")
    # Manually crank up replicas to trigger expansion
    infra.active_deployments["core-backend"]["replicas"] = 5
    actions = survival.run_survival_audit({"cpu": 95})
    
    region_action = next((a for a in actions if a["type"] == "REGION_EXPAND"), None)
    if region_action:
        print(f"✅ Success: Regional Expansion triggered to {region_action['region']}.")
    else:
        print("❌ Failure: Regional Expansion NOT triggered.")

    # Final Status
    status = infra.get_cluster_status()
    print("\n[FINAL INFRASTRUCTURE STATE]")
    print(f"Regions: {infra.regions}")
    for name, deploy in status["deployments"].items():
        print(f" - {name}: {deploy['replicas']} replicas | Health: {deploy['health']:.2f} | Region: {deploy['region']}")

if __name__ == "__main__":
    asyncio.run(test_autonomous_sovereignty())
