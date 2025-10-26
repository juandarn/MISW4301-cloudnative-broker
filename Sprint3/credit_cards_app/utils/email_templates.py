from __future__ import annotations

from datetime import datetime


def _saludo(nombre: str | None) -> str:
    return f"Hola {nombre}," if nombre else "Hola," 


def tpl_card_approved(name: str | None, ruv: str, last_four: str, issuer: str, timestamp: datetime) -> tuple[str, str]:
    saludo = _saludo(name)
    ts = timestamp.strftime("%Y-%m-%d %H:%M:%S") if isinstance(timestamp, datetime) else str(timestamp)
    html = f"""
    <div style=\"font-family:system-ui,Segoe UI,Roboto,Arial,sans-serif\">
      <h2>🎉 Tarjeta aprobada</h2>
      <p>{saludo}</p>
      <p>Tu tarjeta de <strong>{issuer}</strong> terminada en <strong>{last_four}</strong> fue aprobada correctamente.</p>
      <p><strong>RUV:</strong> {ruv}</p>
      <p>Fecha de aprobación: {ts} (UTC)</p>
      <p>Ya puedes usarla en la plataforma.</p>
    </div>
    """
    text = (
        f"""{saludo}\n\nTu tarjeta de {issuer} terminada en {last_four} fue aprobada correctamente.\n"
        f"RUV: {ruv}\nFecha de aprobación: {ts} (UTC)\n\nYa puedes usarla en la plataforma."""
    )
    return html, text


def tpl_card_rejected(name: str | None, ruv: str, last_four: str, issuer: str, timestamp: datetime) -> tuple[str, str]:
    saludo = _saludo(name)
    ts = timestamp.strftime("%Y-%m-%d %H:%M:%S") if isinstance(timestamp, datetime) else str(timestamp)
    html = f"""
    <div style=\"font-family:system-ui,Segoe UI,Roboto,Arial,sans-serif\">
      <h2>⚠️ Tarjeta rechazada</h2>
      <p>{saludo}</p>
      <p>La tarjeta de <strong>{issuer}</strong> terminada en <strong>{last_four}</strong> fue rechazada tras la validación.</p>
      <p><strong>RUV:</strong> {ruv}</p>
      <p>Fecha de evaluación: {ts} (UTC)</p>
      <p>Si consideras que es un error, inténtalo nuevamente o contacta a soporte.</p>
    </div>
    """
    text = (
        f"""{saludo}\n\nLa tarjeta de {issuer} terminada en {last_four} fue rechazada tras la validación.\n"
        f"RUV: {ruv}\nFecha de evaluación: {ts} (UTC)\n\nSi consideras que es un error, inténtalo nuevamente o contacta a soporte."""
    )
    return html, text
