from enum import StrEnum


class BtnSendInputStatus(StrEnum):
    DISABLED = 'DISABLED'
    NO_SEND = 'NO_SEND'
    SENDING = 'SENDING'