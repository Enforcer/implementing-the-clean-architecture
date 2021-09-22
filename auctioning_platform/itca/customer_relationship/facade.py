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
        ...

    def notify_about_winning_auction(
        self,
        customer_id: int,
        auction_id: int,
        auction_title: str,
        amount: Money,
    ) -> None:
        ...
