"""
Setup Billing Alerts and Auto-Shutdown
Prevents runaway costs
"""

import os
from google.cloud import billing_v1
from google.cloud import compute_v1

def create_budget_alert(billing_account_id: str, project_id: str, 
                       budget_amount: float = 50.0):
    """
    Create budget alert
    
    Args:
        billing_account_id: Billing account ID
        project_id: GCP project ID
        budget_amount: Monthly budget in USD
    """
    client = billing_v1.BudgetServiceClient()
    
    # Create budget
    budget = billing_v1.Budget()
    budget.display_name = "LawScout AI Monthly Budget"
    budget.budget_filter.projects = [f"projects/{project_id}"]
    
    # Set amount
    budget.amount.specified_amount.currency_code = "USD"
    budget.amount.specified_amount.units = int(budget_amount)
    
    # Set thresholds
    budget.threshold_rules = [
        billing_v1.ThresholdRule(threshold_percent=0.5),  # 50%
        billing_v1.ThresholdRule(threshold_percent=0.75), # 75%
        billing_v1.ThresholdRule(threshold_percent=0.9),  # 90%
        billing_v1.ThresholdRule(threshold_percent=1.0),  # 100%
    ]
    
    # Create
    parent = f"billingAccounts/{billing_account_id}"
    request = billing_v1.CreateBudgetRequest(parent=parent, budget=budget)
    
    response = client.create_budget(request=request)
    print(f"✅ Created budget: {response.name}")
    print(f"   Amount: ${budget_amount}/month")
    print(f"   Alerts at: 50%, 75%, 90%, 100%")


def stop_all_instances(project_id: str, zone: str = "us-central1-a"):
    """
    Emergency stop all compute instances
    
    Args:
        project_id: GCP project ID
        zone: Compute zone
    """
    client = compute_v1.InstancesClient()
    
    # List instances
    request = compute_v1.ListInstancesRequest(project=project_id, zone=zone)
    instances = client.list(request=request)
    
    stopped = 0
    for instance in instances:
        if instance.status == "RUNNING":
            print(f"🛑 Stopping instance: {instance.name}")
            
            stop_request = compute_v1.StopInstanceRequest(
                project=project_id,
                zone=zone,
                instance=instance.name
            )
            client.stop(request=stop_request)
            stopped += 1
    
    if stopped > 0:
        print(f"✅ Stopped {stopped} instances")
    else:
        print("✅ No running instances found")


if __name__ == "__main__":
    project_id = os.getenv('GCP_PROJECT_ID')
    
    if not project_id:
        print("❌ Set GCP_PROJECT_ID environment variable")
        exit(1)
    
    print("🚨 Emergency Cost Control")
    print("========================")
    print()
    print("This will stop all compute instances.")
    print(f"Project: {project_id}")
    print()
    
    confirm = input("Continue? (yes/no): ")
    if confirm.lower() == 'yes':
        stop_all_instances(project_id)
    else:
        print("Cancelled")

