from agents import Agent, Runner, function_tool


def build_agent():
    @function_tool
    def search_orders(customer_id: str) -> str:
        """Look up the order associated with a customer ID."""
        return ORDERS.get(
            customer_id,
            f"No order found for customer {customer_id}."
        )

    @function_tool
    def get_customer(customer_id: str) -> str:
        """Look up a customer's name using their customer ID."""
        return CUSTOMERS.get(
            customer_id,
            f"No customer found with ID {customer_id}."
        )

    return Agent(
        name="Customer Support Agent",
        instructions=(
            "You are a customer support assistant. "
            "Use search_orders to retrieve order details and get_customer "
            "to retrieve customer information. Never guess order details "
            "or customer identities. If the customer or order cannot be "
            "found, set resolved to false and explain why. "
            "When an order is found, provide its details and the customer ID. "
            "Return the answer using the required structured output."
        ),
        tools=[search_orders, get_customer],
        output_type=SupportAnswer,
        model=MODEL,
        model_settings=SETTINGS,
    )


async def answer(question):
    agent = build_agent()
    result = await Runner.run(
        agent,
        question,
        max_turns=5,
    )
    return result.final_output
