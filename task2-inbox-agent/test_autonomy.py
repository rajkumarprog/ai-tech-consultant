import os
import feedback

if feedback.DB_PATH.exists():
    os.remove(feedback.DB_PATH)          # start clean for the test

draft = "You can change your logo in Settings > Design."

for i in range(1, 21):
    state = feedback.record(i, "how_to", draft, draft, "sent")
print("after 20 unchanged how_to:", state, "| auto:", feedback.may_auto_send("how_to"))

state = feedback.record(21, "how_to", draft, draft + " Anything else?", "sent")
print("after 1 edit:", state, "| auto:", feedback.may_auto_send("how_to"))

for i in range(30):
    state = feedback.record(100 + i, "refund_cancel", draft, draft, "sent")
print("30 unchanged refund_cancel:", state, "| auto:", feedback.may_auto_send("refund_cancel"))
