class PaymentDeclined(Exception):
    pass

class InventoryUnavailable(Exception):
    pass

class InvalidAddress(Exception):
    pass

def process_order(order):
    try:
        validate_address(order)
        reserve_inventory(order)
        charge_payment(order)
        create_shipping_label(order)
        return {"status": "success"}

    # --- System 1: specific, fast handlers ---
    except InvalidAddress as e:
        return {
            "status": "error",
            "type": "invalid_address",
            "message": "The shipping address appears invalid."
        }

    except InventoryUnavailable as e:
        return {
            "status": "error",
            "type": "inventory_unavailable",
            "message": "Item is out of stock."
        }

    except PaymentDeclined as e:
        return {
            "status": "error",
            "type": "payment_declined",
            "message": "Payment was declined. Please retry."
        }

    # --- System 2: catch-all handler ---
    except Exception as e:
        # Historically this is where a human support engineer
        # would inspect logs and determine next steps.
        # Now an LLM can analyze the context dynamically.

        context = {
            "order_id": order.get("id"),
            "raw_error": str(e),
            "order_data": order
        }

        resolution = llm_reason_about_exception(context)

        return {
            "status": "escalated",
            "type": "unclassified_exception",
            "llm_resolution": resolution
        }
