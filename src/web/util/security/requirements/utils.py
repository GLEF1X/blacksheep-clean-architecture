from __future__ import annotations

from typing import Dict, List

from guardpost import Policy

from src.web.util.security.requirements.scope_requirement import ScopeRequirement


def generate_crud_scopes(*subjects: str, delimiter: str = ":") -> Dict[str, str]:
    crud_operations = ["create", "delete", "get"]
    appropriate_crud_descriptions = [
        "Create, delete and do anything you want with {subject}",
        "Create {subject}",
        "Delete {subject}",
        "Get {subject}",
    ]
    return {
        f"{subject}{delimiter}{operation_name}": message.format(subject=subject)
        for operation_name, message in zip(crud_operations, appropriate_crud_descriptions)
        for subject in subjects
    }


def generate_crud_policies(*subjects: str, scope_delimiter: str = ":") -> List[Policy]:
    crud_scopes = generate_crud_scopes(*subjects, delimiter=scope_delimiter)
    return [Policy(k, ScopeRequirement(scopes={k: v})) for k, v in crud_scopes.items()]
