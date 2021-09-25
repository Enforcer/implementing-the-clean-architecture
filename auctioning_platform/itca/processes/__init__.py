import injector

from itca.processes.paying_for_won_auction import PayingForWonAuctionModule


class Processes(injector.Module):
    def configure(self, binder: injector.Binder) -> None:
        binder.install(PayingForWonAuctionModule())
