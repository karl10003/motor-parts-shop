def get_payment_methods():
    """
    This function returns the available payment methods.
    """

    return [
        "Cash on Delivery",
        "GCash",
        "Maya",
        "Bank Transfer"
    ]


def validate_payment_method(method):
    """
    This function checks if the selected payment method is valid.
    """

    return method in get_payment_methods()