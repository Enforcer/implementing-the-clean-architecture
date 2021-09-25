from itca.foundation.money import Money


class CustomerRelationshipFacade:
    def register_customer(self, customer_id: int, email: str) -> None:
        ...

    def unregister_customer(self, customer_id: int) -> None:
        ...

    def update_contact_info(self, customer_id: int, email: str) -> None:
        ...

    def notify_about_overbid(
        self,
        customer_id: int,
        auction_id: int,
        auction_title: str,
        new_price: Money,
    ) -> None:
        print(
            f"Hey, you - #{customer_id}!"
            f"You've been overbid on auction #{auction_id} '{auction_title}'"
            f"New price is {new_price}."
        )

    def notify_about_winning_auction(
        self,
        customer_id: int,
        auction_id: int,
        auction_title: str,
        amount: Money,
    ) -> None:
        print(
            f"Hey, you - #{customer_id}!"
            f"You've won the auction #{auction_id} '{auction_title}'"
            f"Now, you owe us {amount}."
        )
