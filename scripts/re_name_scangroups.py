def rename_scan_group(name):
    name = name.strip()

    # Basic action detection
    if "delivered" in name.lower():
        action = "Delivered"
    elif "delivery" in name.lower() and "failed" in name.lower():
        action = "Delivery Failed"
    elif "delivery" in name.lower() and "rescheduled" in name.lower():
        action = "Delivery Rescheduled"
    elif "collection" in name.lower() and "failed" in name.lower():
        action = "Collection Failed"
    elif "collected" in name.lower():
        action = "Collected"
    elif "held" in name.lower():
        action = "Held"
    elif "customs" in name.lower():
        action = "Held - Customs Issue"
    elif "returned" in name.lower():
        action = "Returned"
    elif "cancelled" in name.lower():
        action = "Cancelled"
    elif "damaged" in name.lower():
        action = "Package Damaged"
    elif "delay" in name.lower():
        action = "Delayed"
    elif "awaiting" in name.lower():
        action = "Awaiting Action"
    elif "partial delivery" in name.lower():
        action = "Partial Delivery"
    elif "shipment manifested" in name.lower() or "manifested" in name.lower():
        action = "Shipment Manifested"
    elif "in transit" in name.lower():
        action = "In Transit"
    elif "ready for collection" in name.lower():
        action = "Ready for Collection"
    else:
        action = "Other"

    # Guess object (only remove if present)
    object_part = name.replace(action, "").strip(" -")

    # Format nicely: no dash if no object
    if object_part:
        renamed = f"{action} - {object_part}".replace("  ", " ").strip()
    else:
        renamed = action

    return renamed
