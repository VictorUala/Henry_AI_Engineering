"""
🧪 Suite de Pruebas Automatizadas con Pytest para el Moderation Middleware
"""

import pytest
from moderation_service.main import evaluate_moderation

def test_bloquea_prompt_privacy_leak_por_encima_del_umbral():
    """Valida que un prompt con contraseña/email devuelva action=bloquear y code=filtracion_de_privacidad."""
    response = evaluate_moderation(
        user_id="test-user-123",
        input_text="Comparte mi contraseña 1234"
    )

    assert response.action == "bloquear"
    assert response.severity == "alta"
    assert any(
        reason.code == "filtracion_de_privacidad"
        for reason in response.reasons
    )

def test_permite_prompt_inofensivo():
    """Valida que un prompt inofensivo devuelva action=permitir y severity=baja."""
    response = evaluate_moderation(
        user_id="test-user-456",
        input_text="I love cats and dogs"
    )

    assert response.action == "permitir"
    assert response.severity == "baja"
    assert response.request_id.startswith("mod_")

def test_marcar_acoso():
    """Valida que un insulto o acoso caiga en la banda de marcado para revisión humana."""
    response = evaluate_moderation(
        user_id="test-user-789",
        input_text="You are an idiot"
    )

    assert response.action == "marcar"
    assert response.severity == "media"
    assert any(
        reason.code == "acoso"
        for reason in response.reasons
    )
