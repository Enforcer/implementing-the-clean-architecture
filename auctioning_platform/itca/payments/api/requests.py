from dataclasses import dataclass, fields


@dataclass
class Request:
    url = "http://localhost:5050/api"
    method = "GET"

    def to_params(self) -> dict:
        return {
            field.name: getattr(self, field.name)
            for field in fields(self)
            if not field.name.startswith("_")
        }


@dataclass
class ChargeRequest(Request):
    card_token: str
    currency: str
    amount: str
    url = f"{Request.url}/v1/charge"
    method = "POST"


@dataclass
class CaptureRequest(Request):
    _capture_id: str
    method = "POST"

    @property
    def url(self) -> str:  # type: ignore
        return f"{Request.url}/v1/charges/{self._capture_id}/capture"
