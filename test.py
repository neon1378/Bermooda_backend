

from WalletManager.models import Wallet,WalletTransAction
import os
from dotenv import load_dotenv
import random
load_dotenv()
from core.models import MainFile
wallet = Wallet.objects.get(id=32)

price_per_mb = int(os.getenv("PRICE_FOR_ANY_MB", 0))  # Default to 0 if not set
price_per_user = int(os.getenv("PRICE_FOR_ANY_USER", 0))  # Default to 0 if not set
    # Calculate total MB used by the workspace
mb_used = sum(
        file.file.size / (1024 * 1024)  # Convert bytes to MB
        for file in MainFile.objects.filter(its_blong=True, workspace_id=wallet.workspace.id)
        if file.file  # Ensure the file exists
)

    # Calculate total users in the workspace
user_member_count = wallet.workspace.workspace_member.count()

    # Calculate the total price to deduct
decrease_price = (mb_used * price_per_mb) + (user_member_count * price_per_user)
print(user_member_count, "@@")
if decrease_price > 0:
        # Deduct the price from the wallet balance
    wallet.balance -= decrease_price
    wallet.save()

        # Create a wallet transaction record
    WalletTransAction.objects.create(
            wallet=wallet,
            price=decrease_price,
            trans_action_status="decrease",
            total_gb=mb_used,
            total_user=user_member_count,
            status_deposit=True,
            order_id=f"D_{random.randint(9999, 100000)}"
    )
