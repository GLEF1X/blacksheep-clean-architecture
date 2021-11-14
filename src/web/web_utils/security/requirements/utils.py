from __future__ import annotations

from typing import Dict


def generate_crud_scopes(*subjects: str, delimiter: str = ":") -> Dict[str, str]:
    crud_operations = ["all", "create", "delete", "get"]
    appropriate_crud_messages = [
        "Create, delete and do anything you want with orders",
        "Only create orders",
        "Only delete orders",
        "Only get order/orders",
    ]
    return {
        f"{subject}{delimiter}{operation_name}": message
        for operation_name, message in zip(crud_operations, appropriate_crud_messages)
        for subject in subjects
    }
